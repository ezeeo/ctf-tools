#coding=utf-8
#import PyExecJS
#version 1.0
import execjs
import sys
import os
path=os.path.abspath('.')+'\\Library\\jj_and_aa\\jjencode.js'

def get_js():
    f = open(path, encoding='utf-8') # 打开JS文件
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr+line
        line = f.readline()
    return htmlstr
jsstr = get_js()
ctx = execjs.compile(jsstr) #加载JS文件

def encode(gv,text):
    return (ctx.call('jjencode', gv,text))  #调用js方法  第一个参数是JS的方法名，后面的data是js方法的参数

print('jjencode将JS代码转换成只有符号的字符串')
print('发布&说明页:http://utf-8.jp/public/jjencode.html')

while True:
    data=input('jjencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    gv=input('global variable name used by jjencode:')
    codestr = encode(gv,data)
    print(codestr)