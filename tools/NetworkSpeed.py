#coding=utf-8
#version 1.1

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
from network_speed_monitor import NetworkSpeedMonitor



if __name__ == "__main__":
    M=NetworkSpeedMonitor()
    cards=M.getcards()
    print('cards:',','.join(cards))
    if len(cards)!=1:
        while 1:
            card=input('choose card:')
            if card in cards:
                break
            else:
                print('no such card')
                continue
    else:
        card=cards[0]
    print('card:',card)
    try:
        last_len=0
        while 1:
            u=M.getup()
            d=M.getdown()
            t='\r↑ {}K/s ↓ {}K/s'.format(u,d)
            r=t+' '*(last_len-len(t))
            print(r,end='')
            last_len=len(t)
            time.sleep(1)
    except KeyboardInterrupt as ex:
        M._end=True

