#coding=utf-8
#version 1.4

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
    def __init__(self, host_forward: str, port_forward: int,host_server='127.0.0.1',port_server=9999,bar=None):
        self.host_server = host_server
        self.port_server = port_server
        self.host_forward = host_forward
        self.port_forward = port_forward
        self.listener = 50
        self.buffer = 102400
        self.out_processer=lambda x:x
        self.in_processer=lambda x:x
        self.sock=None#监听socket
        self.codec='utf-8'
        self._conns=Queue()
        self._processing_conn_num=0#正在处理的连接数


        self._bar=bar
        if self._bar!=None:
            self._bar.start_bar()

        self._end_server=False#决定转发器线程的关闭
        self._is_end_accept=False#标志是否结束accept

        self._forwarder_num=1#转发线程数
        self._lock=threading.Lock()
        self._threads=[]
        self._accept_thread=None

        self._forword_success_num=0
        self._forword_fail_num=0

        self._history=[]#转发的历史记录(原始请求,处理后请求体,原始响应,处理后响应体,错误信息)



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


    def show_history(self,skip=True):
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
                time.sleep(0.1)
        self._waitting_forwarder_end()
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
            while 1:
                end=True
                for t in self._threads:
                    if t!=None and t.isAlive():
                        end=False
                        break
                if end:
                    return
                else:
                    time.sleep(0.01)
            


    def server(self,forwarder_num=1,waitting=False):
        if forwarder_num>self.listener:
            self._print('[-]forwarder_num > listen_num,will modify listen_num')
            self.listener=forwarder_num
        self._start_listen()
        self._accept_thread=threading.Thread(target=self._accepter)
        self._accept_thread.start()
        self._forwarder_num=forwarder_num
        self._start_forworder()
        self._print("[+]server start success")
        if waitting:
            while 1:
                self._lock.acquire()
                end_server=self._end_server
                self._lock.release()
                if self.get_processing_conn_num()==forwarder_num:
                    self._bar.set_move_mode('ll')
                else:
                    self._bar.set_move_mode('lr')

                self._bar.set_rate(int((self._conns.qsize()+self.get_processing_conn_num())/self.listener*100),'conn/max={}/{} f_s|f_f={}|{}'.format(self._conns.qsize()+self.get_processing_conn_num(),self.listener,self.get_forword_success_num(),self.get_forword_fail_num()))
                if end_server:
                    return
                else:
                    time.sleep(1)


    def _start_forworder(self):
        '''启动转发线程'''
        for i in range(self._forwarder_num):
            t=threading.Thread(target=self._forwarder_thread)
            t.start()
            self._threads.append(t)
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


    def set_out_processer(self,method):
        '''设置发送的请求数据的处理函数,输入输出字符串'''
        if not callable(method):
            raise Exception('out_processer必须是callable')
        self.out_processer=method

    def set_in_processer(self,method):
        '''设置发送的请求数据的处理函数,输入输出字符串'''
        if not callable(method):
            raise Exception('in_processer必须是callable')
        self.in_processer=method


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
                body=self.out_processer(self._get_http_body(data.decode(self.codec)))
                log_data[1]=body
            except Exception as ex:
                body=self._get_http_body(data.decode(self.codec))
                self._print('\n[!]error in out_processer->'+str(ex))

            head=self._get_http_head(data.decode(self.codec))
            head=head.replace('Connection: keep-alive','Connection: close')

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
                else:#原样返回
                    pass

                log_data[2]=result
                try:
                    body=self.in_processer(self._get_http_body(result))
                    log_data[3]=body
                except Exception as ex:
                    body=self._get_http_body(result)
                    self._print('\n[!]error in in_processer->'+str(ex))
                
                head=self._get_http_head(result)
                if 'Content-Type: text/html' in head:
                    body=body.encode(self.codec)
                if 'Content-Encoding: gzip' in head:
                    if isinstance(body,str):
                        body=body.encode(self.codec)
                    body=self._gzip_encode(body)
                result=head.encode(self.codec)+b'\r\n\r\n'+body+b'\r\n\r\n'
                result=self._rebuild_content_lenth(result)

                self._history.append(log_data)
                return (True,result)
        except Exception as ex:
            log_data[4]=ex
            self._history.append(log_data)
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
                self._print('[+]end forwarder')
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


    def _recv_http(self,sock):
        time.sleep(0.1)
        #s_time=time.time()
        data=b''
        while 1:
            data_recv = sock.recv(self.buffer)
            #self._bar.print(str(int((time.time()-s_time)*1000))+'ms')
            if data_recv==b'':
                break
            data+=data_recv
            if b'\r\n\r\n' in data_recv:
                contenlen_index=data_recv.find(b'Content-Length: ')
                if contenlen_index==-1:
                    if data_recv.count(b'\r\n\r\n')==2:
                        break
                    elif data[:3]==b'GET':
                        break
                    else:
                        time.sleep(1)

                        tmp_d=sock.recv(self.buffer)
                        if tmp_d!=b'':
                            data+=tmp_d
                            continue
                        else:
                            break
                
                #正常接收http body
                tmp=data_recv[contenlen_index:]

                num=int(tmp.split(b'\r\n')[0][16:].decode('utf-8'))
                now_num=len(tmp.split(b'\r\n')[-1])
                if num==now_num:
                    break
                while 1:
                    if data.count(b'\r\n\r\n')==2:
                        break
                    data_recv=sock.recv(num-now_num)
                    if data_recv==b'':break
                    data+=data_recv
                    now_num+=len(data_recv)
                    if num==now_num:
                        break
                break
            #self._bar.print(str(int((time.time()-s_time)*1000))+'ms')
        #self._bar.print(str(int((time.time()-s_time)*1000))+'ms')
        return data

#响应信号
def exit_server(signum, frame):
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
    bar=Pbar(info_len=50)
    port_server=6789
    host_forward='45.32.110.197'
    port_forward=80
    forwarder_num=2

    # func_file='z:\\cache\\a.py'
    # outprocess_func='pout'
    # inprocess_func='pin'
    # outfunc=pyfunc_util(func_file,'def '+outprocess_func+'*:').get_func(outprocess_func)
    # infunc=pyfunc_util(func_file,'def '+inprocess_func+'*:').get_func(inprocess_func)


    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server,bar=bar)
    # F.set_out_processer(outfunc[3])
    # F.set_in_processer(infunc[3])

    F.server(forwarder_num=forwarder_num,waitting=True)
    #time.sleep(5)
    #F.end_server()
    exit(1)


if __name__ == "__main__":
    #debug()
    bar=Pbar(info_len=50)
    print('[+]这是一个http代理服务器,可以自己增加对输入输出的请求进行处理的函数,ctrl+c结束程序')
    try:
        port_server=int(input('本地监听端口:').strip())
        host_forward=input('转发目标ip:')
        port_forward=int(input('转发目标端口:').strip())
        forwarder_num=int(input('转发线程数:').strip())
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



    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server,bar=bar)
    if set_func:
        F.set_out_processer(outfunc[3])
        F.set_in_processer(infunc[3])
    F.server(forwarder_num=forwarder_num,waitting=True)
    #time.sleep(5)
    #F.end_server()