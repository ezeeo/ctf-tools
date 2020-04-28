#coding=utf-8
#import PyExecJS
#version 1.0
import sys
import os
if sys.platform=='linux':
    import readline
    
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/pyjsfuck'
else:
    path=path+'/Library/pyjsfuck'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from pyjsfuck import JSFuck
jsf = JSFuck()

print('JSFuck 可以让你只用 6 个字符[ ]( ) ! +来编写 JavaScript 程序')
print('输入js代码进行转换')

while True:
    data=input('jsfuck encode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = jsf.encode(data)
    print(codestr)