#coding=utf-8
import os
import sys
try:
    import pip
except:
    print('error in install : must have module pip')
    exit()

from subprocess import call
from time import sleep

from Library.utils.pbar import Pbar
from Library.utils.start_py_env import read_pyenv
from Library.utils.file_scanner import scan_files

version='1.4'
pypath='python'


def scan():#扫描存在的文件
    return scan_files('./tools/',postfix=".py")
def requisite_pip_module():#请求安装的
    file_list=scan()
    result=['fuzzywuzzy','python-Levenshtein']
    if sys.platform=='linux':
        result.append('readline')
    for path in file_list:
        f = open(path, 'r',encoding='UTF-8')
        while True:
            line=f.readline()
            if line=='':
                break
            if line[0]!='#':
                break
            elif line[:7]!='#import':
                continue
            else:
                result.append(line[8:-1])
        f.close()
    return list(set(result))

def should_install_modules(module_list):#需要安装的
    from pip._internal.utils.misc import get_installed_distributions
    mo=get_installed_distributions()
    modules=[]
    for i in mo:
        modules.append(str(i).split(' ')[0])
    #print(modules)
    should=[]
    for i in module_list:
        if i not in modules:
            should.append(i)
    return should

def auto_install(module_list,confirm):#安装
    for mo in module_list:
        #print('pip install '+mo)
        if confirm==True:
            input('now install ' + mo + ', press any key to continue\n'+pypath+' -m pip install '+mo)
        os.system(pypath+' -m pip install '+mo)

def default(confirm):
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
        print('---------------end---------------')
        exit(0)
    print('should install num '+str(len(li)))
    if confirm==True:
        print(li)
        input('please confirm pip is installed press any key to continue')
    print('---------------start installing---------------')
    auto_install(li,confirm)
    print('---------------end---------------')

def show_status():
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
    else:
        print('should install num '+str(len(li)))
        print(li)
    print('---------------end---------------')

def withupdatepip():
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
        print('---------------end---------------')
        exit(0)
    print('upgrade pip')
    os.system(pypath+' -m pip install --upgrade pip')
    print('should install num '+str(len(li)))
    print('---------------start installing---------------')
    auto_install(li,False)
    print('---------------end---------------')


def bar_status():
    bar=Pbar(speed=30,bar_fill='#',bar_moving='<=-=>',move_mode='lr',smooth=True,allow_skip_frame=True)
    bar.start_bar()
    bar.set_rate(None,'get pip list...')

    li=requisite_pip_module()
    all_num=len(li)
    li=should_install_modules(li)
    should_down_num=len(li)

    for i in range(1,all_num+1):

        #bar.set_speed((100-i)//3+60)
        bar.set_rate(int(i/all_num*100),'checking lib...{}/{}'.format(i,all_num+1))

    if len(li)==0:
        bar.set_rate(100,'lib check pass')
    else:
        bar.set_rate(None,'lib check fail')
        bar.print('[-]warn:should install num '+str(len(li)))
    bar.clear(True)



if __name__ =='__main__':
    pypath=read_pyenv()
    if pypath==False:pypath='python'
    if len(sys.argv)==1:
        default(False)
    elif sys.argv[1]=='version':
        print(version)
    elif sys.argv[1]=='status':#显示状态
        show_status()
    elif sys.argv[1]=='withupdatepip':
        withupdatepip()
    elif sys.argv[1]=='withconfirm':
        default(True)
    elif sys.argv[1]=='bar_status':#使用进度条显示状态
        bar_status()