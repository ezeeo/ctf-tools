#coding=utf-8
#import PyExecJS
#version 1.0
import execjs
import os,sys
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')+'/Library/jotherencode/jother-1.0.rc.js'

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
def encode(data, mode='jother'):
    if mode=='jother':
        return (ctx.call('Jother', data))  #调用js方法  第一个参数是JS的方法名，后面的data是js方法的参数
    elif mode=='jothercmd':
        return (ctx.call('JotherCmd', data))  #调用js方法  第一个参数是JS的方法名，后面的data是js方法的参数
    else:
        return 'arg error'

print('jother是一种运用于javascript语言中利用少量字符构造精简的匿名函数方法对于字符串进行的编码方式')
print('其中8个少量字符包括：! + ( ) [ ] { }。只用这些字符就能完成对任意字符串的编码')
print('输入要编码的字符串')

while True:
    data=input('jother encode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = encode(data)
    print(codestr)