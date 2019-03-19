#coding=utf-8
#version 1.2
#import requests
import requests
import os
import json
api_key=''
server_url='http://14.116.192.220:8888/{key}/subdomain?target='
error_num=0
max_error_num=5

def init():
    global api_key
    if os.path.exists('./tools/scanner/web/yun_api/apikey'):
        f=open('./tools/scanner/web/yun_api/apikey','r',encoding='utf-8')
        api_key=f.readline().strip()
        f.close()
    else:
        return False
    if api_key!='':
        return True

def subdomain(url):
    global error_num,max_error_num
    try:
        res=requests.get(url)
        j=json.loads(res.text)
        if j['state']=='error':
            print('error:'+j['message'])
            exit()
        elif j['state']=='queuing':
            print('\rIn a waiting queue '+j['num'],end='')
            return False
        elif j['state']=='searching':
            print('\rsearching              ',end='')
            return False
        elif j['state']=='success':
            print('\n')
            for i in j['result']:
                print(i)
            print()
            return True
    except Exception as e:
        error_num+=1
        if error_num>=5:
            print('\ntoo many errors...now exit')
            exit()
        return False


if __name__=='__main__':
    if not init():
        print('error in init missing apikey')
        exit()
    else:
        print('apikey='+api_key)
    server_url=server_url.format(key=api_key)
    while True:
        target=input('input subdomain search target:')
        if target=='exit()':
            exit()
        url=server_url+target
        while not subdomain(url):pass
