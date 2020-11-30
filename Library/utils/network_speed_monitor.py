import os
import sys
import time
import threading

import psutil
import requests
try:
    from .thread_safe_access_inject import inject_get_set
    from .init_arg_checker import check_init_arg,recv_init_args
except ImportError as ex:
    path=os.path.abspath('.')
    if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
        path=path.split('tools',maxsplit=1)[0]+'Library/utils'
    else:
        path=path+'/Library/utils'
    if not path in (p.replace('\\','/') for p in sys.path):
        sys.path.append(path)

    from thread_safe_access_inject import inject_get_set
    from init_arg_checker import check_init_arg,recv_init_args


class NetworkSpeedMonitor:
    '''网速监控'''
    __is_init=False
    #单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.__is_init:return
        self._ncard={}#n:[up,down]

        self._up_speed=0
        self._down_speed=0
        
        n,s=self._find_ncard()
        self._default_card=n[0]
        self._ncard=self._ncard.fromkeys(n)
        for n in self._ncard.keys():
            self._ncard[n]=[0,0,s[n][0],s[n][1]]

        self._end=False

        inject_get_set(self)

        self._loop=threading.Thread(target=self._monitor_loop)
        self._loop.start()
        self.__is_init=True

    def _find_ncard(self):
        tmpn=[]
        bs={}
        old=psutil.net_io_counters(pernic=True)
        for k,v in old.items():
            if v[0]==0 or v[1]==0:
                continue
            else:
                tmpn.append(k)
        if len(tmpn)==0:
            raise Exception('no network')
        elif len(tmpn)==1:
            bs[tmpn[0]]=(old[tmpn[0]][0],old[tmpn[0]][1])
            return tmpn,bs
        else:
            while 1:
                time.sleep(1)
                r=[]
                new=psutil.net_io_counters(pernic=True)
                for n in tmpn:
                    try:
                        if new[n][0]!=old[n][0] or new[n][1]!=old[n][1]:
                            r.append(n)
                    except Exception as ex:
                        pass
                if len(r)==0:
                    continue
                elif len(r)==1:
                    bs[r[0]]=(new[r[0]][0],new[r[0]][1])
                    return r,bs
                else:
                    for a in r:
                        bs[a]=(new[a][0],new[a][1])
                    return r,bs


    def _monitor_loop(self):
        while 1:
            if self._end:return
            try:
                r=psutil.net_io_counters(pernic=True)
            except Exception as identifier:
                time.sleep(1)
                continue
            self._up_speed=0
            self._down_speed=0
            for n in self._ncard.keys():
                try:
                    self._ncard[n][0]=round((r[n][0]-self._ncard[n][2])/1000,1)
                    self._ncard[n][1]=round((r[n][1]-self._ncard[n][3])/1000,1)
                    self._ncard[n][2]=r[n][0]
                    self._ncard[n][3]=r[n][1]
                    self._up_speed+=self._ncard[n][0]
                    self._down_speed+=self._ncard[n][1]
                except Exception as ex:
                    pass
            time.sleep(1)
            

    def getup(self,card=None):
        if card==None:
            return self._up_speed
        else:
            return self._ncard[card][0]

    def getdown(self,card=None):
        if card==None:
            return self._down_speed
        else:
            return self._ncard[card][1]

    def getcards(self):
        return tuple(self._ncard.keys())

    def getdefault(self):
        return self._default_card






class RouterSpeedMonitor:
    def __init__(self,router_ip:str,router_port:int,router_type:str,username:str,password:str,cookies:dict):
        exec(recv_init_args(self))
        check_init_arg(self)
        print('init pass')
        
    def _check_router_type(self,t):
        allow={'mercury':('D268G','D19G')}#支持的版本
        if t not in allow and t!=None:
            return False

        r=requests.get('http://'+self._router_ip)
        if r.status_code!=200:
            return False
        
        tmp=r.text.split('</title>',maxsplit=1)[0].split('<title>')[1].strip()
        for a in allow:
            if tmp in allow[a]:
                if t==a:
                    return True
                elif t==None:
                    self._router_type=a
                    return True
                else:
                    return False
        return False

    def _login(self):
        pass

    def get_speed(self):

        url='http://127.0.0.1:8888/stok=98860cc1316a69584adba37abbd9383c/ds'
        headers={
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'Content-Type':'application/json; charset=UTF-8',
            'Origin':'http://127.0.0.1:8888',
            'Sec-Fetch-Site':'same-origin',
            'Sec-Fetch-Mode':'cors',
            'Referer':'http://127.0.0.1:8888/',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9'
        }
        jar=requests.cookies.RequestsCookieJar()
        jar.set('log','0')
        jar.set('csrftoken','euaKonAPp68xlAu1dBgWqkoisfWtYkaif2k4asDhcdhl3d0PkrAVOLkHkdR7az4T')

        r=requests.post(url,cookies=jar,data='{"network":{"name":"wan_status"},"method":"get"}',headers=headers)
        return r.text



if __name__ == "__main__":
    # M=NetworkSpeedMonitor()
    # while(1):
    #     print(M.getup(),M.getdown())
    #     time.sleep(1)
    R=RouterSpeedMonitor('192.168.0.1',80,None,None,'6-156-15',cookies=None)
    print(R.get_speed())

