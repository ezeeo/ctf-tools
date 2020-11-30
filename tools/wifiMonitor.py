#coding=utf-8
#version 1.4

import os,sys,time
import threading
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
from run_sys_agent import agent_system
from IPdelayMonitor import NoRootIPdelayMonitor

def get_router_ip():
    if sys.platform=='win32':
        rcode,result,error=agent_system('tracert -h 3 www.baidu.com',return_error=True)
    else:
        rcode,result,error=agent_system('traceroute -m 3 www.baidu.com',return_error=True)
    
    if rcode==0 or error=='':
        r=result.split('\n')[4:]
        result=None
        for l in r:
            if '请求超时' in l or 'Request timed out' in l:
                continue
            else:
                tmp=l.strip().split(' ')[-1]
                if tmp.startswith('['):
                    tmp=tmp[1:-1]
                if tmp[:3] in ('10.','172','192'):
                    result=tmp
                    break
        return result
    else:
        return None


def fake_delay_bar(bar,t=10,info=''):
    def delay_thread(bar,t,info):
        bar.set_rate(0,info)
        for i in range(int(t)):
            bar.set_rate(int(i/int(t)*100))
            time.sleep(1)
        bar.set_rate(100)
    threading.Thread(target=delay_thread,args=(bar,t,info)).start()




if __name__ == "__main__":
    b=Pbar(speed=15,info_len=20,bar_len=50)
    b.start_bar()
    fake_delay_bar(b,30,'正在获取ip...')
    ip=get_router_ip()


    if ip==None or len(ip.split('.'))!=4:
        b.print('获取ip失败')
        b.clear(True)
        exit(0)

    b.print('ip:'+ip)
    b.clear(True)

    b.start_bar()

    L=NoRootIPdelayMonitor(ip)
    R=NoRootIPdelayMonitor('www.baidu.com')
    L.start_monitor()
    R.start_monitor()
    max_delay=100
    max_time=0
    normal_time=0
    loop_time=0
    try:

        while 1:
            b.set_bar_moving('<={}=>'.format(loop_time))
            ld=L.get_delay()
            rd=R.get_delay()
            if ld==-1 or rd==-1:
                b.print('[!]network error on {} | {}ms|{}ms'.format(time.asctime(time.localtime(time.time())),ld,rd))
            loop_time+=1
            if ld>max_delay:
                max_time+=1
            if max_time>3:
                max_time=0
                max_delay*=2
            if ld<max_delay//2:
                normal_time+=1
            if normal_time>10:
                normal_time=0
                max_delay=max_delay//2
                if max_delay<5:
                    max_delay=5
            if loop_time>20:
                max_time=0
                normal_time=0
                loop_time=0
            if ld==-1:
                b.set_rate(100,'{}ms|{}ms'.format(ld,rd))
            else:
                b.set_rate(int(ld*100/max_delay),'{}ms|{}ms|max={}'.format(ld,rd,max_delay))
            time.sleep(0.5)
    except KeyboardInterrupt as ex:
        L.end_monitor()
        R.end_monitor()
        b.clear(True)

    
