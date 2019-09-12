#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
'''
 ____       _     _     _ _   __  __           _
|  _ \ __ _| |__ | |__ (_) |_|  \/  | __ _ ___| | __
| |_) / _` | '_ \| '_ \| | __| |\/| |/ _` / __| |/ /
|  _ < (_| | |_) | |_) | | |_| |  | | (_| \__ \   <
|_| \_\__,_|_.__/|_.__/|_|\__|_|  |_|\__,_|___/_|\_\

'''
import logging
import sys
import requests
h=''

logging.basicConfig(filename='Weblogic.log',
                    format='%(asctime)s %(message)s',
                    filemode="w", level=logging.INFO)

VUL=['CVE-2018-2894']
headers = {'user-agent': 'ceshi/0.0.1'}

def islive(ur,port):
    url=h + str(ur)+':'+str(port)+'/ws_utc/resources/setting/options/general'
    r = requests.get(url, headers=headers,verify=False)
    return r.status_code

def run(url,port,index,hh):
    h=hh
    if islive(url,port)!=404:
        logging.info('[+]The target weblogic has a JAVA deserialization vulnerability:{}'.format(VUL[index]))
        print('[+]The target weblogic has a JAVA deserialization vulnerability:{}'.format(VUL[index]))
    else:
        logging.info('[-]Target weblogic not detected {}'.format(VUL[index]))
        print('[-]Target weblogic not detected {}'.format(VUL[index]))

if __name__=="__main__":
    url = sys.argv[1]
    port = int(sys.argv[2])
    run(url,port,0)
