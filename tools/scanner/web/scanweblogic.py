#coding=utf-8
#version 1.1
#import certifi
#import chardet
#import idna
#import urllib3
#import requests
import sys
import os
import shutil

weblogicscan='./Library/WeblogicScan/WeblogicScan.py'

def scan(ip,port,use_https):
    fd=os.system('python '+weblogicscan+' '+ip+' '+port+' '+use_https)
    move_log()
    return fd

def move_log():
    if os.path.exists('Weblogic.log'):
        if os.path.exists('.\output\Weblogic.log'):
            os.remove('.\output\Weblogic.log')
        shutil.move('Weblogic.log','.\output\Weblogic.log')

def read_log():
    file_path='.\output\Weblogic.log'
    if not os.path.exists(file_path):return ''
    with open(file_path,'r',encoding='utf-8') as f:
        data=f.read().strip()
    return data


if len(sys.argv)>=3:
    if len(sys.argv)==3:
        fd=scan(sys.argv[1],sys.argv[2],'http')
    else:
        fd=scan(sys.argv[1],sys.argv[2],sys.argv[3])
    if fd!=0:
        log=read_log()
        print('[!]注意:执行的返回值不为0')
        if log!='':
            print(log)
    exit(fd)



if __name__ == "__main__":
    print('weblogic多个漏洞扫描')
    ip=input('ip:')
    port=input('port:')
    https=input('use https (y/n):')
    fd=scan(ip,port,https)
    if fd!=0:
        log=read_log()
        print('[!]注意:执行的返回值不为0')
        if log!='':
            print(log)
