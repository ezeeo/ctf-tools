#coding=utf-8
#import PyExecJS
#version 1.1
import execjs
import sys
import os

def get_jscode(inp):
    if os.path.exists(inp):
        with open(inp,'r',encoding='utf-8') as f:
            data=f.read()
        return data
    return inp


if len(sys.argv)==2:
    data=get_jscode(sys.argv[1])
    print('\n'+execjs.eval(data))
    exit()

print('支持输入js代码或者文件路径')
while True:
    data=input('runjs>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    data=get_jscode(data)
    ctx = execjs.eval(data) #运行js
    print(ctx)