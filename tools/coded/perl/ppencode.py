#coding=utf-8
#import PyExecJS
#version 1.0
import execjs
import sys
import os
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')+'/Library/ppencode/ppencode.js'

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

def encode(text):
    return (ctx.call('ppencode',text))  #调用js方法  第一个参数是JS的方法名，后面的data是js方法的参数

print('ppencode-Perl把Perl代码转换成只有英文字母的字符串')
print('发布&说明页:http://namazu.org/~takesako/ppencode/demo.html')

while True:
    data=input('ppencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = encode(data)
    print('\n'+codestr)