import os
import sys

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from thread_safe_access_inject import inject_get_set
from value_snapshot import value_snapshot,value_rollback
from auto_decoder import auto_decode
import threading
import subprocess
import time
class NoRootIPdelayMonitor:
    def __init__(self,ip):
        self._ip=ip

        self._thread_state='end'
        self._thread_info=[]

        self._last_update_time=0#上次延时的更新时刻
        self._last_delay=0#上次更新的延时(ms)
        self._history_record=[]#历史记录(时刻:延时)

        self._ping_process=None#subprocess.Popen ping子进程
        self._m_thread=None

        fd=inject_get_set(self)#注入线程安全的属性访问方法
        if fd==False:
            raise Exception('inject method fail')
        #value_snapshot(self)


    def start_monitor(self):
        if self._thread_state_get()=='end':
            self._start_ping_process()
            self._thread_state_set('start')
            self._m_thread=threading.Thread(target=self._monitor_thread)
            self._m_thread.start()
        time.sleep(0.5)

    def _start_ping_process(self):
        s=['ping',self._ip,'-t']#-w 9000
        subs=subprocess.Popen(s,bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
        subs.stdin.close()
        
        self._ping_process=subs

    def _parse_ping_line(self,line:str):
        return int(line.strip().split(' ')[-2].split('=')[1][:-2])


    def _monitor_thread(self):
        while 1:
            try:
                state=self._thread_state_get()
                if state=='end':
                    return
                elif state=='pause':
                    time.sleep(0.001)
                    continue
                else:
                    pass
                
                if self._ping_process==None:
                    self._thread_info.append('ping_process==None -> thread_state={}->end'.format(self._thread_state))
                    return

                while self._ping_process.poll() is None:
                    line=self._ping_process.stdout.readline()
                    output = auto_decode(line).strip()
                    if output=='':continue
                    self._last_update_time_set(time.time())
                    if len(output.split(' '))>=5 and ': ' in output:
                        self._last_delay_set(self._parse_ping_line(output))
                        self._history_record.append((self._last_update_time_get(),self._last_delay_get()))
                    else:
                        self._last_delay_set(-1)
                        self._history_record.append((self._last_update_time_get(),-1))

                time.sleep(0.5)

            except Exception as ex:
                self._thread_info.append('exception -> '+str(ex))



    def get_delay(self):
        if self._thread_state_get()=='end':return
        if time.time()-self._last_update_time_get()>3 and self._last_delay_get()<3000:
            return int((time.time()-self._last_update_time_get())*1000)
        return self._last_delay_get()

    def end_monitor(self):
        if self._thread_state_get()!='end':
            self._thread_state_set('end')
            self._ping_process.kill()
            self._ping_process=None
            self._m_thread=None

if __name__ == "__main__":
    T=NoRootIPdelayMonitor('192.168.1.1')
    T.start_monitor()

    for i in range(10):
        print(T.get_delay())
        time.sleep(0.5)
    T.end_monitor()
    print(T._thread_info)