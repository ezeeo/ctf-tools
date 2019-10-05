#coding=utf-8
#import Js2Py
#version 1.0
import js2py
import os
path=os.path.abspath('.')+'/Library/jj_and_aa/aaencode.js'

jsdata=open(path,'r',encoding= 'utf8').read()
encode=js2py.eval_js(jsdata) #转换JS文件

print('aaencode可以将JS代码转换成常用的网络表情，也就是我们说的颜文字js加密')
print('发布&说明页:http://utf-8.jp/public/aaencode.html')

while True:
    data=input('aaencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = encode(data)
    print(codestr)

