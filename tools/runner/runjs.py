#coding=utf-8
#import PyExecJS
#version 1.0
import execjs
import sys

if len(sys.argv)==2:
    print('\n'+execjs.eval(sys.argv[1]))
    exit()

while True:
    data=input('runjs>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    ctx = execjs.eval(data) #运行js
    print(ctx)