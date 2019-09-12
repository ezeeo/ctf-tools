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

headers = {'user-agent': 'ceshi/0.0.1'}

def islive(ur,port):
    url=h + str(ur)+':'+str(port)+'/uddiexplorer/'
    r = requests.get(url, headers=headers,verify=False)
    return r.status_code

def run(url,port,hh):
    h=hh
    if islive(url,port)==200:
        u=h + str(url)+':'+str(port)+'/uddiexplorer/'
        logging.info('[+]The target Weblogic UDDI module is exposed! The path is: {} Please verify the SSRF vulnerability!'.format(u))
        print('[+]The target Weblogic UDDI module is exposed!\n[+]The path is: {}\n[+]Please verify the SSRF vulnerability!'.format(u))
    else:
        logging.info("[-]The target Weblogic UDDI module default path does not exist!")
        print("[-]The target Weblogic UDDI module default path does not exist!")

if __name__=="__main__":
    url = sys.argv[1]
    port = int(sys.argv[2])
    run(url,port)
