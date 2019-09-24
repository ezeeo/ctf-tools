#coding=utf-8
#version 2.1
import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library\\utils'
else:
    path=path+'\\Library\\utils'
if not path in sys.path:
    sys.path.append(path)
from get_func_from_pyfile import pyfunc_util
from tool_input import withexit_input

allow_mode=('php','jsp','asp','aspx')

def load_funcs(mode):
    if mode not in allow_mode:
        print('[!]暂未支持此语言')
        return False
    p=path.split('Library')[0]+'Library/'+'createaword/{}creater.py'.format(mode)
    F=pyfunc_util(p,'def {}_*(*)*:'.format(mode))
    return F


def select_mode():
    for i,mode in enumerate(allow_mode):
        print(i+1,':',mode)
    mode=withexit_input('选择语言模式:')
    if not mode.isdigit():
        print('[!]请输入数字')
        return False
    mode=int(mode)
    if mode<=0 or mode>len(allow_mode):
        print('[!]请输入合法范围的数字')
        return False
    return allow_mode[mode-1]


def select_func(F):
    funcs=F.get_funclist()
    for i,func in enumerate(funcs):
        print(i+1,':',func[0],func[2])

    fno=withexit_input('选择马(数字/all):')
    if fno.lower()=='all':return 'all'
    if not fno.isdigit():
        print('[!]请输入数字')
        return False
    fno=int(fno)
    if fno<=0 or fno>len(funcs):
        print('[!]请输入合法范围的数字')
        return False
    return funcs[fno-1]

def run_func(F,func,pwd=None):
    if 'pwd' in func[1]:
        if pwd==None:
            pwd=withexit_input('输入链接密码:')
        return F.run(func[0],pwd=pwd)
    else:
        return F.run(func[0])

def main():
    mode=select_mode()
    if mode==False:
        return False
    F=load_funcs(mode)
    if F==False:return False
    func=select_func(F)
    if func==False:return False
    elif func=='all':
        pwd=withexit_input('输入链接密码:')
        for f in F.get_funclist():
            print('-'*50)
            print(run_func(F,f,pwd))
        print('-'*50)
    else:
        print(run_func(F,func))


if __name__ == "__main__":
    while True:
        main()