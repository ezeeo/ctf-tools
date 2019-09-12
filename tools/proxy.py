#coding=utf-8
#version 1.0

import socket
import threading
import time
from queue import Queue,Empty
import gzip
import signal

class ProxyForward:
    def __init__(self, host_forward: str, port_forward: int,host_server='127.0.0.1',port_server=9999):
        self.host_server = host_server
        self.port_server = port_server
        self.host_forward = host_forward
        self.port_forward = port_forward
        self.listener = 50
        self.buffer = 102400
        self.out_processer=lambda x:str(x)
        self.in_processer=lambda x:str(x)
        self.sock=None#监听socket
        self.codec='utf-8'
        self._conns=Queue()

        self._end_server=False#决定转发器线程的关闭
        self._is_end_accept=False#标志是否结束accept

        self._forwarder_num=1#转发线程数
        self._lock=threading.Lock()
        self._threads=[]
        self._accept_thread=None

    def end_server(self):
        self._lock.acquire()
        self._end_server=True
        self._lock.release()
        print('[+]tell threads end...')
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
        print('[+]end server')

    def _waitting_forwarder_end(self):
        '''等待所有转发线程结束'''
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
        self._start_listen()
        self._accept_thread=threading.Thread(target=self._accepter)
        self._accept_thread.start()
        self._forwarder_num=forwarder_num
        self._start_forworder()
        print("[+]server start success")
        if waitting:
            while 1:
                self._lock.acquire()
                end_server=self._end_server
                self._lock.release()
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
        print('[+]success start {} forworder'.format(self._forwarder_num))

    def _start_listen(self):
        '''启动监听'''
        self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host_server, self.port_server))
        self.sock.listen(self.listener)
        # sock.setblocking(False)
        self.sock.settimeout(3)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[+]server begin to listen....")


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
                return data[-1]
        else:
            data=data.strip().split(b'\r\n\r\n')
            if len(data)==1:
                return b''
            else:
                return data[-1]

    def _get_http_head(self,data):
        if isinstance(data,str):
            data=data.strip().split('\r\n\r\n')
        else:
            data=data.strip().split(b'\r\n\r\n')
        return data[0]


    def _gzip_decode(self,data):
        data = gzip.decompress(data)  #解压缩
        return data

    def _gzip_encode(self,data):
        data = gzip.compress(data)  #压缩
        return data

    def _forward(self,data:bytes):
        try:
            try:
                body=self.out_processer(self._get_http_body(data.decode(self.codec)))
            except Exception as ex:
                body=self._get_http_body(data.decode(self.codec))
                print('\n[!]error in out_processer->'+str(ex))

            head=self._get_http_head(data.decode(self.codec))
            data=head+'\r\n\r\n'+body+'\r\n\r\n'

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_forward, self.port_forward))
                self._send_http(sock,data.encode(self.codec))
                result=self._recv_http(sock)
                #判定需不需要gzip解压
                head=self._get_http_head(result).decode(self.codec)
                if 'Content-Encoding: gzip' in head:
                    body=self._get_http_body(result)
                    body=self._gzip_decode(body).decode(self.codec)
                    result=head+'\r\n\r\n'+body+'\r\n\r\n'
                else:
                    result=result.decode(self.codec)
                try:
                    body=self.in_processer(self._get_http_body(result))
                except Exception as ex:
                    body=self._get_http_body(result)
                    print('\n[!]error in in_processer->'+str(ex))
                
                head=self._get_http_head(result)
                body=body.encode(self.codec)
                if 'Content-Encoding: gzip' in head:
                    body=self._gzip_encode(body)
                result=head.encode(self.codec)+b'\r\n\r\n'+body+b'\r\n\r\n'

                return (True,result)
        except Exception as ex:
            return (False,ex)


    def _accepter(self):
        '''接受请求进队列'''
        print("[+]server begin to accept....")
        while 1:
            #判定结束
            self._lock.acquire()
            end_server=self._end_server
            self._lock.release()
            if end_server:
                print('[+]end accepter')
                self._lock.acquire()
                self._is_end_accept=True
                self._lock.release()
                return
            try:
                self.sock.settimeout(3)
                conn, addr = self.sock.accept()
                self.sock.settimeout(None)
                self._conns.put((conn,addr))
                print('+',end='',flush=True)
            except socket.timeout as ex:
                pass
            except Exception as ex:
                print('\n[!]accepter error->'+str(ex))



    def _forwarder_thread(self):
        '''请求事件监听线程'''
        while 1:
            #判定结束
            self._lock.acquire()
            end_server=self._end_server
            self._lock.release()
            if end_server:
                print('[+]end forwarder')
                return
            try:
                conn, addr=self._conns.get(timeout=1)
            except Empty as ex:
                continue
            
            print('<',end='',flush=True)
            try:
                data=self._recv_http(conn)
            except Exception as ex:
                print('\n[!]',addr,ex)
                conn.close()
                continue
            print('><',end='',flush=True)
            result=self._forward(data)
            print('>',end='',flush=True)
            if result[0]==False:
                print('\n[!]',addr,result[1])
                conn.close()
            else:
                try:
                    self._send_http(conn,result[1])
                    print('-',end='',flush=True)
                except Exception as ex:
                    print('\n[!]return data error->'+str(ex))



    def _send_http(self,sock,data:bytes):
        sock.sendall(data)


    def _recv_http(self,sock):
        time.sleep(0.1)
        data=b''
        while 1:
            data_recv = sock.recv(self.buffer)
            if data_recv==b'':break
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
                        data+=sock.recv(self.buffer)
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
                    data+=data_recv
                    now_num+=len(data_recv)
                    if num==now_num:
                        break
                break
        return data

#响应信号
def exit_server(signum, frame):
    global F
    print('[!]get stop signal, now stop...')
    F.end_server()
    exit()
signal.signal(signal.SIGINT, exit_server)
signal.signal(signal.SIGTERM, exit_server)


if __name__ == "__main__":
    print('[+]这是一个http代理服务器,可以自己增加对输入输出的请求进行处理的函数,ctrl+c结束程序')
    try:
        port_server=int(input('本地监听端口:').strip())
        host_forward=input('转发目标ip:')
        port_forward=int(input('转发目标端口:').strip())
        forwarder_num=int(input('转发线程数:').strip())
    except Exception as ex:
        print('[!]input format error')
        exit(0)

    F=ProxyForward(host_forward=host_forward, port_forward=port_forward,port_server=port_server)
    #F.set_out_processer(encrypt_http)
    #F.set_in_processer(decrypt_http)
    F.server(forwarder_num=forwarder_num,waitting=True)
    #time.sleep(5)
    #F.end_server()