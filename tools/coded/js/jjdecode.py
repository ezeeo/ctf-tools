#coding=utf-8
#import Js2Py
#version 1.0
import js2py
import os
path=os.path.abspath('.')+'/Library/jj_and_aa/jjdecode.js'

jsdata=open(path,'r',encoding= 'utf8').read()
decode=js2py.eval_js(jsdata) #转换JS文件

while True:
    data=input('jjdecode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = decode(data)
    print('\n'+codestr)