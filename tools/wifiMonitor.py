#coding=utf-8
#version 1.3

import os,sys,time
import threading
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
    b=Pbar(speed=15,)
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
    try:

        while 1:
            ld=L.get_delay()
            rd=R.get_delay()
            if ld==-1 or rd==-1:
                b.print('[!]network error on {} | {}ms|{}ms'.format(time.asctime(time.localtime(time.time())),ld,rd))
            if rd==-1:
                b.set_rate(100,'{}ms|{}ms'.format(ld,rd))
            else:
                b.set_rate(int(rd/10),'{}ms|{}ms'.format(ld,rd))
            time.sleep(0.5)
    except KeyboardInterrupt as ex:
        L.end_monitor()
        R.end_monitor()
        b.clear(True)

    
