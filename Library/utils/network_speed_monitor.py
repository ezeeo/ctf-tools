import os
import sys
import time
import threading

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from thread_safe_access_inject import inject_get_set

import psutil


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
                raise Exception('no network')
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

if __name__ == "__main__":
    M=NetworkSpeedMonitor()
    while(1):
        print(M.getup(),M.getdown())
        time.sleep(1)
