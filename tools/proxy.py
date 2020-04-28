#coding=utf-8
#version 1.8

import socket
import threading
import time
from queue import Queue,Empty
import gzip
import signal
import sys
import os
import traceback
import inspect
import ctypes
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
from pbar import Pbar
from get_func_from_pyfile import pyfunc_util


class ProxyForward:
    def __init__(self, host_forward: str, port_forward: int,host_server='127.0.0.1',port_server=9999,bar=None,debug=False):
        self.host_server = host_server
        self.port_server = port_server
        self.host_forward = host_forward
        self.port_forward = port_forward
        self.listener = 50
        self.buffer = 102400
        self.out_processer=[lambda x:x.replace('Connection: keep-alive','Connection: close'),lambda x:x]#分别处理请求头和请求体
        self.in_processer=[lambda x:x,lambda x:x]#分别处理响应头和响应体
        self.sock=None#监听socket
        self.codec='utf-8'
        self._conns=Queue()
        self._processing_conn_num=0#正在处理的连接数


        self._bar=bar
        if self._bar!=None:
            self._bar.start_bar()
            self._bar.hidden()

        self._end_server=False#决定转发器线程的关闭
        self._is_end_accept=False#标志是否结束accept

        self._forwarder_num=1#转发线程数
        self._lock=threading.Lock()
        self._threads=[]
        self._accept_thread=None

        self._forword_success_num=0
        self._forword_fail_num=0

        self._history=[]#转发的历史记录(原始请求,处理后请求体,原始响应,处理后响应体,错误信息)
        self._debug=debug
        self._isshow_his=False

    def add_forword_success_num(self):
        self._lock.acquire()
        self._forword_success_num+=1
        self._lock.release()
    def add_forword_fail_num(self):
        self._lock.acquire()
        self._forword_fail_num+=1
        self._lock.release()
    def get_forword_success_num(self):
        self._lock.acquire()
        a=self._forword_success_num
        self._lock.release()
        return a
    def get_forword_fail_num(self):
        self._lock.acquire()
        a=self._forword_fail_num
        self._lock.release()
        return a
    def add_processing_conn_num(self):
        self._lock.acquire()
        self._processing_conn_num+=1
        self._lock.release()
    def get_processing_conn_num(self):
        self._lock.acquire()
        a=self._processing_conn_num
        self._lock.release()
        return a
    def minus_processing_conn_num(self):
        self._lock.acquire()
        self._processing_conn_num-=1
        self._lock.release()

    def _print(self,s):
        if self._bar!=None:
            self._bar.print(s)
        else:
            print(s)


    def show_history(self,skip=True,rt_mode=False):
        if self._isshow_his:return
        self._isshow_his=True
        if self._debug and rt_mode:
            if len(self._history)!=0:
                self._print('='*61)
                while len(self._history)!=0:
                    log=self._history.pop(0)
                    self._print('>'*24+'   raw req   '+'>'*24)
                    self._print(log[0])
                    self._print('>'*24+'processed req'+'>'*24)
                    self._print(log[1])
                    self._print('<'*24+'   raw res   '+'<'*24)
                    self._print(log[2])
                    self._print('<'*24+'processed res'+'<'*24)
                    self._print(log[3])
                    self._print('-'*24+'  errorinfo  '+'-'*24)
                    self._print(str(log[4]))
                    self._print('='*61)
        else:
            print('='*61)
            for log in self._history:
                if skip==True and log[4]==None:
                    continue
                print('>'*24+'   raw req   '+'>'*24)
                print(log[0])
                print('>'*24+'processed req'+'>'*24)
                print(log[1])
                print('<'*24+'   raw res   '+'<'*24)
                print(log[2])
                print('<'*24+'processed res'+'<'*24)
                print(log[3])
                print('-'*24+'  errorinfo  '+'-'*24)
                print(log[4])
                print('='*61)
            self._history.clear()
        self._isshow_his=False


    def _async_raise(self,tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def _stop_thread(self,t):
        '''强制停止线程'''
        try:
            self._async_raise(t.ident, SystemExit)
        except SystemExit as ex:
            pass
        

    

    def end_server(self):
        self._lock.acquire()
        self._end_server=True
        self._lock.release()
        self._print('[+]tell threads end...')
        self._bar.set_rate(0,'waitting end server...')
        self._bar.set_move_mode('rr')
        #等待accepter结束
        while 1:
            self._lock.acquire()
            end=self._is_end_accept
            self._lock.release()
            if end:
                break
            else:
                time.sleep(0.01)
        self._waitting_forwarder_end()
        self._print('[+]end all forwarder')
        if self.sock!=None:
            self.sock.close()
        self._print('[+]end server')

    def _waitting_forwarder_end(self,force=False):
        '''等待所有转发线程结束,force指示是否使用强制结束线程'''
        if force:
            for t in self._threads:
                if t!=None and t.isAlive():
                    self._stop_thread(t)
        else:
            loop_num=0
            while 1:
                loop_num+=1
                end=True
                e_num=0
                for t in self._threads:
                    if t!=None and t.isAlive():
                        end=False
                    else:
                        e_num+=1
                if loop_num%50==1:
                    self._bar.set_rate(0,'end forwarder {}|{}'.format(e_num,len(self._threads)))
                if end:
                    return
                else:
                    time.sleep(0.01)
            

    def waitting_server_end(self):
        '''阻塞到服务器接收到退出信号并且成功退出'''
        while 1:
            self._lock.acquire()
            end_server=self._end_server
            self._lock.release()
            if self._bar!=None:
                if self.get_processing_conn_num()==self._forwarder_num:
                    self._bar.set_move_mode('ll')
                else:
                    self._bar.set_move_mode('lr')

                self._bar.set_rate(int((self._conns.qsize()+self.get_processing_conn_num())/self.listener*100),'conn/max={}/{} f_s|f_f={}|{}'.format(self._conns.qsize()+self.get_processing_conn_num(),self.listener,self.get_forword_success_num(),self.get_forword_fail_num()))
            if end_server:
                return
            else:
                time.sleep(1)



    def server(self,forwarder_num=1,waitting=False):
        if forwarder_num>self.listener:
            self._print('[-]forwarder_num > listen_num,will modify listen_num')
            self.listener=forwarder_num
        self._start_listen()
        self._accept_thread=threading.Thread(target=self._accepter)
        self._accept_thread.start()
        self._forwarder_num=forwarder_num
        self._print("[+]start forworder...")
        self._start_forworder()
        self._print("[+]server start success")
        if waitting:
            self._bar.reshow()
            self.waitting_server_end()


    def _start_forworder(self):
        '''启动转发线程'''
        for i in range(self._forwarder_num):
            t=threading.Thread(target=self._forwarder_thread)
            t.start()
            self._threads.append(t)
            if (i+1)%100==0:
                self._bar.set_rate((i+1)*100//self._forwarder_num,'satrting forworder {}|{}'.format(i+1,self._forwarder_num))
        self._print('[+]success start {} forworder'.format(self._forwarder_num))

    def _start_listen(self):
        '''启动监听'''
        self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host_server, self.port_server))
        self.sock.listen(self.listener)
        # sock.setblocking(False)
        self.sock.settimeout(3)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._print("[+]server begin to listen....")


    def set_out_processer(self,head_method,body_method):
        '''设置发送的请求数据的处理函数,输入输出字符串'''
        if not (head_method==None or callable(head_method)) or not (body_method==None or callable(body_method)):
            raise Exception('out_processer必须是callable')
        if head_method!=None:
            self.out_processer[0]=head_method
        if body_method!=None:
            self.out_processer[1]=body_method

    def set_in_processer(self,head_method,body_method):
        '''设置发送的请求数据的处理函数,输入输出字符串'''
        if not (head_method==None or callable(head_method)) or not (body_method==None or callable(body_method)):
            raise Exception('in_processer必须是callable')
        if head_method!=None:
            self.in_processer[0]=head_method
        if body_method!=None:
            self.in_processer[1]=body_method


    def _get_http_body(self,data):
        if isinstance(data,str):
            data=data.strip().split('\r\n\r\n')
            if len(data)==1:
                return ''
            else:
                return '\r\n\r\n'.join(data[1:])
        else:
            data=data.strip().split(b'\r\n\r\n')
            if len(data)==1:
                return b''
            else:
                return b'\r\n\r\n'.join(data[1:])

    def _get_http_head(self,data):
        if isinstance(data,str):
            data=data.strip().split('\r\n\r\n')
            return data[0]
        else:
            data=data.strip().split(b'\r\n\r\n')
            d=data[0].decode(self.codec)
            return d
        


    def _gzip_decode(self,data):
        data = gzip.decompress(data)  #解压缩
        return data

    def _gzip_encode(self,data):
        data = gzip.compress(data)  #压缩
        return data

    def _rebuild_content_lenth(self,data:bytes):
        '''重建content的长度'''
        body=self._get_http_body(data)
        lenth=len(body)
        if b'Transfer-Encoding: chunked' in data:
            return data.replace(b'Transfer-Encoding: chunked',b'Content-Length: '+str(lenth).encode(self.codec))
            
        else:
            data=data.split(b'Content-Length: ',maxsplit=1)
            if len(data)==1:
                return data[0]
            data[1]= str(lenth).encode(self.codec)+b'\r\n'+data[1].split(b'\r\n',maxsplit=1)[1]
            return b'Content-Length: '.join(data)



    def _forward(self,data:bytes):
        log_data=[None,None,None,None,None]
        try:
            log_data[0]=data.decode(self.codec)
            try:
                head=self.out_processer[0](self._get_http_head(data.decode(self.codec)))
                body=self.out_processer[1](self._get_http_body(data.decode(self.codec)))
                log_data[1]=body
            except Exception as ex:
                head=self._get_http_head(data.decode(self.codec))
                body=self._get_http_body(data.decode(self.codec))
                self._print('\n[!]error in out_processer->'+str(ex))

        

            data=head+'\r\n\r\n'+body+'\r\n\r\n'

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_forward, self.port_forward))
                self._send_http(sock,data.encode(self.codec))
                result=self._recv_http(sock)
                #判定需不需要gzip解压
                head=self._get_http_head(result)
                if 'Content-Encoding: gzip' in head:
                    body=self._get_http_body(result)
                    body=self._gzip_decode(body).decode(self.codec)
                    result=head+'\r\n\r\n'+body+'\r\n\r\n'
                elif 'Content-Type: text/html' in head:
                    result=result.decode(self.codec)
                else:#未明确说明尝试解码否则原样返回
                    try:
                        result=result.decode(self.codec)
                    except Exception as ex:
                        pass

                log_data[2]=result
                try:
                    head=self.in_processer[0](self._get_http_head(result))
                    body=self.in_processer[1](self._get_http_body(result))
                    log_data[3]=body
                except Exception as ex:
                    head=self._get_http_head(result)
                    body=self._get_http_body(result)
                    self._print('\n[!]error in in_processer->'+str(ex))
                
                
                if 'Content-Type: text/html' in head:
                    body=body.encode(self.codec)
                if 'Content-Encoding: gzip' in head:
                    if isinstance(body,str):
                        body=body.encode(self.codec)
                    body=self._gzip_encode(body)
                if isinstance(body,str):
                    body=body.encode(self.codec)
                result=head.encode(self.codec)+b'\r\n\r\n'+body+b'\r\n\r\n'
                result=self._rebuild_content_lenth(result)

                self._history.append(log_data)
                if self._debug:
                    self.show_history(rt_mode=True)

                return (True,result)
        except Exception as ex:
            log_data[4]=ex
            self._history.append(log_data)
            if self._debug:
                self.show_history(rt_mode=True)
            return (False,ex)


    def _accepter(self):
        '''接受请求进队列'''
        self._print("[+]server begin to accept....")
        while 1:
            #判定结束
            self._lock.acquire()
            end_server=self._end_server
            self._lock.release()
            if end_server:
                self._print('[+]end accepter')
                self._lock.acquire()
                self._is_end_accept=True
                self._lock.release()
                return
            if self._conns.qsize()+self.get_processing_conn_num()>=self.listener:
                self._bar.print('[-]accept overload...')
                time.sleep(0.1)
                continue
            try:
                self.sock.settimeout(3)
                conn, addr = self.sock.accept()
                self.sock.settimeout(None)
                self._conns.put((conn,addr))
                #self._print('+',end='',flush=True)
            except socket.timeout as ex:
                pass
            except Exception as ex:
                self._print('\n[!]accepter error->'+str(ex))



    def _forwarder_thread(self):
        '''请求事件监听线程'''
        while 1:
            #判定结束
            self._lock.acquire()
            end_server=self._end_server
            self._lock.release()
            if end_server:
                #self._print('[+]end forwarder')
                return
            try:
                conn, addr=self._conns.get(timeout=1)
                self.add_processing_conn_num()
            except Empty as ex:
                continue
            
            #self._print('<',end='',flush=True)
            try:
                data=self._recv_http(conn)
            except Exception as ex:
                self._print('[!]recv error'+str(addr)+str(ex))
                conn.close()
                self.add_forword_fail_num()
                self.minus_processing_conn_num()
                continue
            if data==b'':
                conn.close()
                self._bar.print('[-]Receiving non-standard requests->data is None')
                self.minus_processing_conn_num()
                continue
            #self._print('><',end='',flush=True)
            result=self._forward(data)
            #self._print('>',end='',flush=True)
            if result[0]==False:
                self._print('[!]forword error:'+str(addr)+str(result[1]))
                conn.close()
                self.add_forword_fail_num()
            else:
                try:
                    self._send_http(conn,result[1])
                    #print('-',end='',flush=True)
                    self.add_forword_success_num()
                except Exception as ex:
                    self._print('[!]return data error->'+str(ex))
                    self.add_forword_fail_num()
                conn.close()
            self.minus_processing_conn_num()


    def _send_http(self,sock,data:bytes):
        sock.sendall(data)


    def _recv_chunked(self,sock,data):
        '''读取Transfer-Encoding: chunked'''
        head=data.split(b'\r\n\r\n',maxsplit=1)[0]
        real_body=b''
        body=data.split(b'\r\n\r\n',maxsplit=1)[1]#初始的响应体，每轮的那一部分
        while 1:
            if b'\r\n' not in body:
                body+=sock.recv(self.buffer)
                continue
            else:
                Lbody=body.split(b'\r\n',maxsplit=1)
                chunked_lenth=int(Lbody[0],base=16)
                if chunked_lenth==0:
                    return head+b'\r\n\r\n'+real_body

                if len(Lbody[1])<chunked_lenth:
                    body+=sock.recv(chunked_lenth-len(Lbody[1])+2)
                    continue
                #组装真实body
                real_body+=Lbody[1][:chunked_lenth]
                body=Lbody[1][chunked_lenth:]
                #接收换行符
                while 1:
                    if len(body)>=2 and body[:2]==b'\r\n':
                        body=body[2:]
                        break
                    else:
                        body+=sock.recv(self.buffer)


            

    def _recv_http(self,sock):
        data=b''
        nodata_num=0
        while 1:
            if nodata_num>15:#不得已
                break
            data_recv = sock.recv(self.buffer)
            data+=data_recv
            if b'\r\n\r\n' in data:#接收完成请求头
                contenlen_index=data.find(b'Content-Length: ')
                if contenlen_index==-1:
                    if data[:3]==b'GET':
                        break
                    elif b'Transfer-Encoding: chunked' in data:
                        return self._recv_chunked(sock,data)
                    else:
                        time.sleep(0.1)
                        continue
                else:
                    #正常接收http body
                    tmp=data_recv[contenlen_index:]

                    num=int(tmp.split(b'\r\n')[0][16:].decode('utf-8'))

                    now_num=len(tmp.split(b'\r\n\r\n',maxsplit=1)[-1])
                    if num==now_num:
                        break
                    while 1:
                        data_recv=sock.recv(num-now_num)
                        data+=data_recv
                        now_num+=len(data_recv)
                        if num==now_num:
                            break
                    break
            else:
                nodata_num+=1
                continue
        return data
            


#响应信号
def exit_server(signum, frame)->None:
    global F,bar
    if F._end_server==True:
        bar.print('[!]get muti stop signal, now force stop')
        F._waitting_forwarder_end(True)
        bar.clear()
        exit(1)
    else:
        bar.print('[!]get stop signal, now stop...')
        bar.print('[+]if it cannot be stopped for a long, you can ctrl+c again')
        F.end_server()
        if bar!=None:
            bar.clear(True)
        if input('[+]show http hsitory?(y/n):').strip().lower()=='y':
            if input('[+]skip None error hsitory?(y/n):').strip().lower()=='y':
                F.show_history(True)
            else:
                F.show_history(False)

    exit(0)
signal.signal(signal.SIGINT, exit_server)
signal.signal(signal.SIGTERM, exit_server)


def debug():
    global bar,F
    bar=Pbar(speed=20,info_len=50)
    port_server=8001
    host_forward='192.168.8.203'
    #host_forward='127.0.0.1'
    port_forward=8001
    forwarder_num=5

    func_file='./dynamic_replacement/login_live_com.py'
    func_util=pyfunc_util(func_file,'def process_*:')
    #outprocess_func='process_out'

    #outfunc=pyfunc_util(func_file,'def '+outprocess_func+'*:').get_func(outprocess_func)


    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server,bar=None,debug=False)

    F.set_out_processer(func_util.get_func('process_out_head')[3],func_util.get_func('process_out_body')[3])
    F.set_in_processer(func_util.get_func('process_in_head')[3],func_util.get_func('process_in_body')[3])

    F.server(forwarder_num=forwarder_num,waitting=False)
    F.waitting_server_end()
    #time.sleep(5)
    #F.end_server()
    #exit(1)
    


if __name__ == "__main__":
    #debug()

    debug=False
    if len(sys.argv)==2 and sys.argv[1]=='--debug':
        print('[+]进入debug模式.将会实时输出数据')
        debug=True
    #debug()
    bar=Pbar(info_len=50)
    print('[+]这是一个http代理服务器,可以自己增加对输入输出的请求进行处理的函数,ctrl+c结束程序')
    try:
        port_server=int(input('本地监听端口:').strip())
        host_forward=input('转发目标ip:')
        port_forward=int(input('转发目标端口:').strip())
        forwarder_num=int(input('转发线程数:').strip())
        codec=input('编码方式:').strip()
        func_file=input('存储处理函数的文件:')
        set_func=False
        if func_file!='':
            if os.path.exists(func_file):
                outprocess_func=input('输出需要进行的处理的函数名(自己到目标需要的处理):').strip()
                inprocess_func=input('输入需要进行的处理的函数名(目标到自己需要的处理):').strip()
                outfunc=pyfunc_util(func_file,'def '+outprocess_func+'*:').get_func(outprocess_func)
                infunc=pyfunc_util(func_file,'def '+inprocess_func+'*:').get_func(inprocess_func)
                set_func=True
            else:
                print('[!]文件不存在')
    except Exception as ex:
        print('[!]input format error')
        exit(0)


    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server,bar=bar,debug=debug)
    F.codec=codec
    if set_func:
        F.set_out_processer(None,outfunc[3])
        F.set_in_processer(None,infunc[3])
    while 1:
        try:
            F.server(forwarder_num=forwarder_num,waitting=True)
            break
        except Exception as ex:

            print('[!]error:'+str(ex))
            i=input('[-]try again?').strip()
            if i=='y' or i=='Y':
                continue
            if F._bar!=None:
                F._bar.clear()
            break
    #time.sleep(5)
    #F.end_server()