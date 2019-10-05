#encoding:utf-8
#version 1.2
#import paramiko

import os
import sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
from py_env_util import PY_ENV_CL,PY_PIP_CI

python2_env=PY_ENV_CL('cves',2).get_pyenv()
python3_env=PY_ENV_CL('cves',3).get_pyenv()
PY_PIP_CI(python2_env).ensure('paramiko')

#base='C:\\Tools\\pytools'
base='.'
cvebase = base+'/Library/cves/'

guess_list=[]#cache


def scan_files(directory,prefix=None,postfix=None):
    files_list=[]
    
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root,special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root,special_file))
            else:
                files_list.append(os.path.join(root,special_file))
                          
    return files_list


def scan():#扫描存在的文件
    return scan_files(cvebase,prefix='cve',postfix=".py")

def get_py_env():
    global python2_env,python3_env
    if os.path.exists(cvebase+'py2_env.ini'):
        with open(cvebase+'py2_env.ini','r',encoding='utf-8') as f:
            python2_env=f.read().strip()
    else:
        python2_env=input('[!]python2 环境不存在,请输入python2可执行文件目录:')
        with open(cvebase+'py2_env.ini','w',encoding='utf-8') as f:
            f.write(python2_env)
    if os.path.exists(cvebase+'py3_env.ini'):
        with open(cvebase+'py3_env.ini','r',encoding='utf-8') as f:
            python3_env=f.read().strip()
    else:
        python3_env=input('[!]python3 环境不存在,请输入python3可执行文件目录:')
        with open(cvebase+'py3_env.ini','w',encoding='utf-8') as f:
            f.write(python3_env)


def check_py23(file_path):
    with open(file_path,'r',encoding='utf-8') as f:
        data=f.read()
    if 'print(' in data or 'print (' in data:
        return 3
    return 2 

#文件猜测
def guessing(userinput,cve_guess_list):
    max_matching=0
    i=-1
    path_num=-1
    for item in cve_guess_list:
        i+=1
        if cve_guess_list[i].find('_')!=-1:#有多个命名
            temp=cve_guess_list[i].split('_')
            tempmax=0
            for alias in temp:
                match=fuzz.ratio(userinput,alias)
                if match>tempmax:
                    tempmax=match
            match=tempmax
        else:
            match=fuzz.ratio(userinput,item)
        if match>max_matching:
            max_matching=match
            path_num=i
    #print('max match num='+str(max_matching))
    if max_matching<50:
        return -1
    return path_num

#获得猜测列表
def get_guesslist(cve_list):
    guess=[]
    for item in cve_list:
        guess.append(os.path.splitext(os.path.basename(item))[0])
    return guess

def match(all_cve,name):
    global guess_list
    if guess_list==[] or len(all_cve)!=len(guess_list):
        guess_list=get_guesslist(all_cve)
    index=guessing(name,guess_list)
    if index==-1:return False
    return all_cve[index]


if len(sys.argv)==2:
    #get_py_env()
    allcve=scan()
    file_name=match(allcve,sys.argv[1])
    if file_name==False:
        print('[!]匹配失败')
        exit(1)
    now_env=eval('python'+str(check_py23(file_name))+'_env')
    while 1:
        print(os.path.basename(file_name),'-> ',end='')
        args=input('input args:')
        if args=='exit()':
            exit(0)
        elif args=='':
            continue
        os.system(now_env+' '+file_name+' '+args)


if __name__ == "__main__":
    print('本模块用于调用cve 的poc')
    #get_py_env()
    allcve=scan()
    print('[+]get',len(allcve),'poc')
    for i in allcve:print('[+]'+os.path.split(i)[1])
    
    while True:
        data=input('cve>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        file_name=match(allcve,data)
        if file_name==False:
            print('[!]匹配失败')
            continue
        
        now_env=PY_ENV_CL(file_name).get_pyenv()
        print('now env:',now_env)
        while 1:
            print(os.path.basename(file_name),'-> ',end='')
            args=input('input args:')
            if args=='exit()':
                break
            elif args=='':
                continue
            os.system(now_env+' '+file_name+' '+args)