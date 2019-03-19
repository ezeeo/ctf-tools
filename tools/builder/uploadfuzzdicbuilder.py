#coding=utf-8
#version 1.0
import sys
import os

def get_py_env():
    pyenv='python'
    if os.path.exists('py_env.ini'):
        print('find py_env.ini')
        f=open('py_env.ini', 'r',encoding='UTF-8')
        pyenv=f.readline()
        pyenv="'"+pyenv+"'"
        f.close()
    return pyenv
pyenv=get_py_env()

if len(sys.argv)>1:
    arg=''
    for i in range(1,len(sys.argv)):
        arg=arg+' '+sys.argv[i]

    print(pyenv+' ./Library/upload-fuzz-dic-builder/upload-fuzz-dic-builder.py'+arg)
    #os.system(pyenv+' ./Library/upload-fuzz-dic-builder/upload-fuzz-dic-builder.py'+arg)
    exit()

notice='''
author: c0ny1<root@gv7.me>
github: https://github.com/c0ny1/upload-fuzz-dic-builder
date: 2018-11-04 23:16
description: 生成符合漏洞实际场景fuzz字典的脚本
注意:bp中使用时需要把urlencode关闭!
更多信息可以在tool_manager/Library/upload-fuzz-dic-builder中查看
'''
print(notice)
name=input('输入上传文件名(不要加.xxx):')
houzhui=input('输入可上传文件后缀(1个,不要加.):')
lan=input('输入后端语言(asp|php|jsp|all):')
wsys=input('输入中间件(iis|apache|tomcat|all):')
oos=input('输入操作系统(win|linux|all):')
path=input('输入输出文件路径和名称(默认在程序根目录下)')
arg=''
if name!='':
    arg+=' -n '+name
if houzhui!='':
    arg+=' -a '+houzhui
if lan!='':
    arg+=' -l '+lan
if wsys!='':
    arg+=' -m '+wsys
if oos!='':
    arg+=' --os '+oos
if path=='':
    arg+=" -o ./output/upload_fuzz_dic.txt"
else:
    arg+=" -o '"+path+"'"
#print(pyenv+' ./Library/upload-fuzz-dic-builder/upload-fuzz-dic-builder.py'+arg)
print('start:')
os.system(pyenv+' ./Library/upload-fuzz-dic-builder/upload-fuzz-dic-builder.py'+arg)