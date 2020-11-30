
from os import truncate
import subprocess
from queue import Queue,Empty
import threading
import time
import sys,os
import random,string
from time import sleep

try:
    from .thread_safe_access_inject import inject_get_set
    from .auto_decoder import auto_decode
except ImportError as ex:
    path=os.path.abspath('.')
    if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
        path=path.split('tools',maxsplit=1)[0]+'Library/utils'
    else:
        path=path+'/Library/utils'
    if not path in (p.replace('\\','/') for p in sys.path):
        sys.path.append(path)
    from thread_safe_access_inject import inject_get_set
    from auto_decoder import auto_decode


def agent_system(s,sp=' ',return_error=False):
    '''运行指定cmd命令,获取返回code和结果'''
    s=[i.strip() for i in s.split(sp)]
    while '' in s:
        s.remove('')
    #import locale
    
    #if locale.getdefaultlocale()[1]=='cp936':
    #    recode=True
    #else:
    #    recode=False
    if len(s)==0:return None
    
    #s[0]='set PYTHONIOENCODING=UTF-8&&'+s[0] 
    try:
        subs=subprocess.Popen(s,bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        #subs.stdin.close()
    except Exception as ex:
        if not return_error:
            return -1,''
        return -1,'',str(ex)

    #subs.wait()
    result,errors=subs.communicate()

    result=auto_decode(result)
    errors=auto_decode(errors)

    # result=''
    # errors=''
    # for line in subs.stdout.readlines():
    #     ##blow for pycharm and cygwin show chinese#

    #     output = auto_decode(line)
    #     result+=output
    # for line in subs.stderr.readlines():
    #     ##blow for pycharm and cygwin show chinese#

    #     output = auto_decode(line)
    #     errors+=output
    if return_error:
        return (subs.returncode,result,errors)
    else:
        return (subs.returncode,result)


class Interactive_system:
    def __init__(self,cmdline,cwd,sp=' ',input_codec='utf-8'):
        '''传入命令和分隔符'''
        self.platform='win32'
        self._input_codec=input_codec
        self._cmdline=[i.strip() for i in cmdline.split(sp)]
        self._cwd=cwd
        while '' in self._cmdline:
            self._cmdline.remove('')
        try:
            self._subp=subprocess.Popen(self._cmdline,bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self._cwd)
        except Exception as ex:
            raise Exception('create process error -> '+str(ex))
        
        self._rtcode=None

        self._cache_result=Queue()
        self._cache_error=Queue()
        self._raw_result=bytearray()
        self._raw_error=bytearray()
        self._last_get_result_index=0
        self._last_get_error_index=0
        self._results=[]
        self._errors=[]
        self._input_queue=Queue()
        self._end=False
        self._busy=True
        inject_get_set(self,var=('_busy'))
        self._start_loop()


    def _start_loop(self):
        self._r_thread=threading.Thread(target=self._get_data2queue,args=(self._subp.stdout,self._cache_result,self._raw_result))
        self._e_thread=threading.Thread(target=self._get_data2queue,args=(self._subp.stderr,self._cache_error,self._raw_error))
        self._i_thread=threading.Thread(target=self._input_loop,args=(self._subp.stdin,self._input_queue))
        self._m_thread=threading.Thread(target=self._monitor)
        self._r_thread.start()
        self._e_thread.start()
        self._i_thread.start()
        self._m_thread.start()


    def _get_data2queue(self,fd,c:Queue,r:bytearray):
        while 1:
            if self._end:return
            self._busy_set(True)
            i=fd.read(1)
            if i==b'':
                self._busy_set(False)
                time.sleep(0.01)
                continue
            c.put(i)
            r.append(ord(i))

    def _input_loop(self,fd,t:Queue):
        while 1:
            if self._end:return
            self._busy_set(True)
            try:
                code=self._input_queue.get(timeout=0.000001)
            except TimeoutError as ex:
                self._busy_set(False)
                time.sleep(0.01)
                continue
            except Empty as ex:
                self._busy_set(False)
                time.sleep(0.01)
                continue
            fd.write(code)


    def _read_cache(self,c:Queue,b:bytearray):
        triggers=b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
        build_index=0
        while 1:
            try:
                r=c.get(timeout=0.000001)
            except TimeoutError as ex:
                break
            except Empty as ex:
                break
            b.append(ord(r))
            if r in triggers:
                build_index=len(b)
        return build_index


    def _build_str(self,ba:bytearray,index):
        tmpline=ba[:index]
        try:
            return auto_decode(tmpline)
        except Exception as ex:
            return bytes(tmpline).__str__()

    def _check_end(self):
        if self._subp.poll()==None or self._cache_result.qsize()!=0 or self._cache_error.qsize()!=0:
            return False
        else:
            return True

    def _monitor(self):
        now_result=bytearray()
        now_error=bytearray()
        
        r_build_index=e_build_index=0
        while 1:
            if self._end:return
            r_build_index=self._read_cache(self._cache_result,now_result)
            e_build_index=self._read_cache(self._cache_error,now_error)

            if r_build_index!=0:
                self._results.append(self._build_str(now_result,r_build_index))
                now_result=now_result[r_build_index:]
            if e_build_index!=0:
                self._errors.append(self._build_str(now_error,e_build_index))
                now_error=now_error[e_build_index:]
            
            if len(now_result)==0 and len(now_error)==0 and self._check_end() and self._busy_get()==False:
                self._end=True




    def _get_output_data(self,origin:list,index:int,getall:bool):
        if getall:
            return ''.join(origin),index
        else:
            l=len(origin)
            r=''
            for i in range(index,l):
               r+=origin[i]
            return r,l

    def _enter(self):
        if self.platform=='win32':
            return b'\r\n'
        else:
            return b'\n'

    def getresult(self,getall=False):
        r,index=self._get_output_data(self._results,self._last_get_result_index,getall)
        self._last_get_result_index=index
        return r

    def geterror(self,getall=False):
        r,index=self._get_output_data(self._errors,self._last_get_error_index,getall)
        self._last_get_error_index=index
        return r

    def getdata(self,getall=False):
        d=self.geterror(getall)
        if d=='':
            d=self.getresult(getall)
        return d

    def input_data(self,d:str,auto_enter=True,wait_result=False,max_time=60,tag_mode=False):
        ''''在不确定被调程序情况下不建议开启wait_result,启用tag_mode的时候不会等待执行完成(此时wait_result无效),将会返回结果开始结束标记'''
        if not auto_enter:
            d=d.encode(self._input_codec)
        else:
            d=d.rstrip().encode(self._input_codec)+self._enter()
        random_start= ''.join(random.choice(string.ascii_letters) for i in range(32))
        random_end= ''.join(random.choice(string.ascii_letters) for i in range(32))
        if tag_mode:
            self._input_queue.put(b'echo '+random_start.encode(self._input_codec)+self._enter())
        self._input_queue.put(d)
        if tag_mode:
            self._input_queue.put(b'echo '+random_end.encode(self._input_codec)+self._enter())

        if tag_mode:
            if wait_result:
                self.enter_until_data(max_time=max_time)
            return random_start,random_end
        if wait_result:
            return self.enter_until_data(max_time=max_time)

    def gettagresult(self,start_tag:str,end_tag:str):
        r=self.getresult(True)
        r=r.split(start_tag)
        while len(r)==1:
            time.sleep(0.3)
            r=self.getresult(True).split(start_tag)
        r=r[1]
        r=r.split(end_tag)
        while len(r)==1:
            time.sleep(0.3)
            r=self.getresult(True).split(start_tag)[1].split(end_tag)
        return r[0]


    def enter_until_data(self,enter=True,check_delay=0.5,max_time=60):
        ''''在不确定被调程序情况下不建议使用此方法'''
        stime=time.time()
        while 1:
            if self._end:
                raise Exception('end')
            time.sleep(check_delay)
            if self.have_data():
                return self
            if enter:
                self.input_data('')
            if time.time()-stime>max_time:return self
    

    def check(self):
        '''check is end'''
        if self._end and self._last_get_result_index==len(self._results) and self._last_get_error_index==len(self._errors):
            return self._subp.returncode



    def have_result(self):
        return self._last_get_result_index < len(self._results)
    def have_error(self):
        return self._last_get_error_index < len(self._errors)
    def have_data(self):
        return self.have_error() or self.have_result()

    def clear(self,with_enter=False,max_time=2):
        if with_enter:
            self.input_data('',wait_result=True,max_time=max_time)
        self._last_get_error_index=len(self._errors)
        self._last_get_result_index=len(self._results)
        return self

    def close(self):
        self._subp.kill()
        self._end=True


    def read_untile(self,point_str,output=False):
        while 1:
            self.enter_until_data(False,0.1,0.5)
            



        
###需要在套一层。。。因为不能保证被执行程序支持echo

if __name__ == "__main__":
    # code,result=agent_system('G:\\python\\tool_manager\\installer.exe serverinfo')
    # print(code,result)

    I=Interactive_system('W:\\programs\\NM-Down\\BiliBili-down.exe','W:\\programs\\NM-Down\\')
    #I=Interactive_system('python G:\\python\\tool_manager\\output\\test.py')
    #I=Interactive_system('bash')
    I.platform='win32'
    sleep(1)
    #I.clear(True)
    while 1:
        #print('-----start')
        #print(I._results)
        #print(I._errors)
        #print(I.getresult(),end='')
        #print('-------end')
        
        print(I.enter_until_data(False).getdata())
        s=input('>')
        I.input_data(s,auto_enter=True,wait_result=True,max_time=20,tag_mode=False)
        

        #print(I.clear(with_enter=False).input_data(input('bash>'),wait_result=True,max_time=2).getdata())

        
