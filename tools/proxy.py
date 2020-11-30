#coding=utf-8
#version 2.0

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
import ssl
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
from auto_decoder import auto_decode
from auto_input import autokbex_input
from re_read_socket import seeked_socket

class ProxyForward:
    '''正反向http代理，不支持https'''
    def __init__(self, host_forward=None, port_forward=None,host_server='0.0.0.0',port_server=9999,bar=None,debug=False):
        '''当host_forward与port_forward不为空时反向代理，否则正向'''
        self.host_server = host_server
        self.port_server = port_server
        if host_forward!=None and port_forward!=None:
            self.reverse=True
        else:
            self.reverse=False

        self.host_forward = host_forward
        self.port_forward = port_forward
        self.listener = 50
        self.buffer = 102400
        self.out_processer=[lambda x:x.replace('Connection: keep-alive','Connection: close'),lambda x:x]#分别处理请求头和请求体
        self.in_processer=[lambda x:x,lambda x:x]#分别处理响应头和响应体
        self.sock=None#监听socket
        self.codec='utf-8'#默认发送编码
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
 
        self.save_log=True#标记是否保存历史纪录
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
                if t!=None and t.is_alive():
                    self._stop_thread(t)
        else:
            loop_num=0
            while 1:
                loop_num+=1
                end=True
                e_num=0
                for t in self._threads:
                    if t!=None and t.is_alive():
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
        if isinstance(head_method,tuple):
            head_method=head_method[3]
        if isinstance(body_method,tuple):
            body_method=body_method[3]
        if not (head_method==None or callable(head_method)) or not (body_method==None or callable(body_method)):
            raise Exception('out_processer必须是callable')
        if head_method!=None:
            self.out_processer[0]=head_method
        if body_method!=None:
            self.out_processer[1]=body_method

    def set_in_processer(self,head_method,body_method):
        '''设置发送的请求数据的处理函数,输入输出字符串'''
        if isinstance(head_method,tuple):
            head_method=head_method[3]
        if isinstance(body_method,tuple):
            body_method=body_method[3]
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

    def _get_http_head(self,data)->str:
        if isinstance(data,str):
            data=data.strip().split('\r\n\r\n')
            return data[0]
        else:
            data=data.strip().split(b'\r\n\r\n')
            d=auto_decode(data[0])
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
            return data.replace(b'Transfer-Encoding: chunked',b'Content-Length: '+str(lenth).encode('utf-8'))#这里数字的编码都可以互相兼容
            
        else:
            data=data.split(b'Content-Length: ',maxsplit=1)
            if len(data)==1:
                return data[0]
            data[1]= str(lenth).encode('utf-8')+b'\r\n'+data[1].split(b'\r\n',maxsplit=1)[1]
            return b'Content-Length: '.join(data)


    def _unpack_http(self,data:bytes):
        '''bytes请求转为head(str)和body,自动处理编码和gzip'''
        head=self._get_http_head(data)
        body=self._get_http_body(data)
        #处理请求gzip
        if 'Content-Encoding: gzip' in head:
            body=self._gzip_decode(body)
        if 'Content-Type: text/html' in head:
            body=auto_decode(body)
        try:#无标识才尝试
            body=auto_decode(body)
        except Exception as ex:
            pass
        return head,body

    def _pack_http(self,head:str,body,codec=None):
        if codec==None:
            codec=self.codec
        if 'Content-Type: text/html' in head:
            body=body.encode(codec)
        if 'Content-Encoding: gzip' in head:
            if isinstance(body,str):
                body=body.encode(codec)
            body=self._gzip_encode(body)
        if isinstance(body,str):
            body=body.encode(codec)
        result=head.encode(codec)+b'\r\n\r\n'
        if len(body)!=0:
            result=result+body+b'\r\n\r\n'
        return result

    def _get_host_port_from_head(self,head):
        for line in head.split('\n'):
            if line.startswith('Host:'):
                tmp=line.strip().split(' ')[1]
                if ':' in tmp:
                    tmp=tmp.split(':')
                    host=tmp[0]
                    port=int(tmp[1])
                else:
                    host=tmp
                    port=80
                return host,port
        else:
            raise Exception('cannot find host in http head')

    def _forward(self,data:bytes):
        log_data=[None,None,None,None,None]
        try:
            log_data[0]=data.__str__()
            head,body=self._unpack_http(data)

            try:
                head=self.out_processer[0](head)
                body=self.out_processer[1](body)
                if isinstance(body,bytes):
                    log_data[1]=head+body.__str__()
                else:
                    log_data[1]=head+'\r\n\r\n'+body
            except Exception as ex:
                self._print('\n[!]error in out_processer->'+str(ex))

            if self.reverse:
                host,port=self.host_forward, self.port_forward
            else:
                host,port=self._get_host_port_from_head(head)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host,port))
                self._send_http(sock,self._pack_http(head,body))

                result=self._recv_http(sock)
                log_data[2]=result.__str__()
                head,body=self._unpack_http(result)
                
                try:
                    head=self.in_processer[0](head)
                    body=self.in_processer[1](body)
                    if isinstance(body,bytes):
                        log_data[3]=head+body.__str__()
                    else:
                        log_data[3]=head+'\r\n\r\n'+body
                except Exception as ex:
                    self._print('\n[!]error in in_processer->'+str(ex))
                
                #重新打包
                result=self._pack_http(head,body)
                result=self._rebuild_content_lenth(result)
                if self.save_log:
                    self._history.append(log_data)
                if self._debug:
                    self.show_history(rt_mode=True)

                return (True,result)
        except Exception as ex:
            log_data[4]=ex
            if self.save_log:
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
                self._print('[-]accept overload...')
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
                self._print('[-]Receiving non-standard requests->data is None')
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


            

    def _recv_http(self,sock)->bytes:
        data=b''
        nodata_num=0
        while 1:
            if nodata_num>15:#不得已
                break
            
            
            ssl.wrap_socket()
           
            #sock=seeked_socket(sock)

            
            #sock=ssl.wrap_socket(sock)
            #data_recv = sock.recv(self.buffer)
            data_recv=sock.recv(1)
            # data_recv = sock.recv(self.buffer)
            if data_recv==b'\x16':
                
                #sock.seek(0)
                sock=ssl.wrap_socket(sock)
                data_recv = sock.recv(self.buffer)

            if len(data_recv)==0:
                nodata_num+=1
            else:
                nodata_num=0
            data+=data_recv
            if b'\r\n\r\n' in data:#接收完成请求头
                contenlen_index=data.split(b'\r\n\r\n',maxsplit=1)[0].find(b'Content-Length: ')
                if contenlen_index==-1:
                    contenlen_index=data.split(b'\r\n\r\n',maxsplit=1)[0].find(b'content-length: ')
                if contenlen_index==-1:
                    if data.split(b'\r\n')[0].split(b' ')[0] in (b'GET',b'OPTIONS'):
                        if data.split(b'\r\n\r\n')[1]==b'':
                            break
                        else:
                            continue
                    elif b'Transfer-Encoding: chunked' in data:
                        return self._recv_chunked(sock,data)
                    else:
                        time.sleep(0.1)
                        continue
                else:
                    #正常接收http body
                    tmp=data[contenlen_index:]
                    
                    num=int(auto_decode(tmp.split(b'\r\n')[0][16:]),base=10)

                    now_num=len(tmp.split(b'\r\n\r\n',maxsplit=1)[-1])
                    if num==now_num:
                        break
                    elif now_num>num:
                        self._print('[-]warn:recv http response lenth error -> now_num>content lenth')
                        break
                    while 1:
                        data_recv=sock.recv(num-now_num)
                        data+=data_recv
                        now_num+=len(data_recv)
                        if num==now_num:
                            break
                        elif now_num>num:
                            self._print('[-]warn:recv http response lenth error -> now_num>content lenth')
                            break
                    break
            
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

    #bar=Pbar(speed=20,info_len=50)
    port_server=9999
    #host_forward='192.168.8.203'
    #host_forward='127.0.0.1'
    #port_forward=8001
    forwarder_num=1

    #func_file='./dynamic_replacement/login_live_com.py'
    #func_util=pyfunc_util(func_file,'def process_*:')
    #outprocess_func='process_out'

    #outfunc=pyfunc_util(func_file,'def '+outprocess_func+'*:').get_func(outprocess_func)


    F=ProxyForward(host_forward='192.168.0.203', port_forward=5001,port_server=port_server,bar=None,debug=True)

    #F.set_out_processer(func_util.get_func('process_out_head')[3],func_util.get_func('process_out_body')[3])
    #F.set_in_processer(func_util.get_func('process_in_head')[3],func_util.get_func('process_in_body')[3])

    F.server(forwarder_num=forwarder_num,waitting=False)
    F.waitting_server_end()
    #time.sleep(5)
    #F.end_server()
    #exit(1)
    

if __name__ == "__main__":
    debug()

    print('[+]这是一个http代理服务器,可以自己增加对输入输出的请求进行处理的函数,ctrl+c结束程序')
    debug=False
    log=True
    if '--nolog' in sys.argv:
        print('[+]日志记录已关闭')
        log=False
    if '--debug' in sys.argv:
        print('[+]进入debug模式.将会实时输出数据,debug依赖于log,--nolog将失效')
        debug=True
        log=True

    if '-r' in sys.argv or '--reverse' in sys.argv:
        reverse=True
        print('[+]已选择反向代理模式')
    else:
        reverse=False
        print('[+]已选择正向代理模式')

    try:
        port_server=int(autokbex_input('本地监听端口:').strip())
        if reverse:
            host_forward=autokbex_input('转发目标ip:')
            port_forward=int(autokbex_input('转发目标端口:').strip())
        else:
            host_forward=port_forward=None
        forwarder_num=int(autokbex_input('转发线程数:').strip())
        #codec=input('发送编码方式:').strip()
        #if codec=='':
        #    codec='utf-8'
        func_file=autokbex_input('存储处理函数的文件(方法名为out_head,out_body,in_head,in_body:')
        set_func=False
        if func_file!='':
            if os.path.exists(func_file):
                U=pyfunc_util(func_file,'def *:*')
                out_head=U.get_func('out_head')
                out_body=U.get_func('out_body')
                in_head=U.get_func('in_head')
                in_body=U.get_func('in_body')
                set_func=True
            else:
                print('[!]文件不存在')
    except Exception as ex:
        print('[!]input format error')
        exit(0)

    bar=Pbar(info_len=50)
    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server,bar=bar,debug=debug)
    F.save_log=log
    #F.codec=codec
    if set_func:
        F.set_out_processer(out_head,out_body)
        F.set_in_processer(in_head,in_body)
    while 1:
        try:
            F.server(forwarder_num=forwarder_num,waitting=True)
            break
        except Exception as ex:

            print('[!]error:'+str(ex))
            i=autokbex_input('[-]try again?').strip()
            if i=='y' or i=='Y':
                continue
            if F._bar!=None:
                F._bar.clear()
            break
    #time.sleep(5)
    #F.end_server()