#conding=utf-8
#version 1.1
#2import python-xlrd

import sys
import os
import time
import shutil
path=os.path.abspath('.')
if 'tools' in path:
    path=path.split('tools',maxsplit=1)[0]+'Library\\utils'
else:
    path=path+'\\Library\\utils'
if not path in sys.path:
    sys.path.append(path)
from py_env_util import PY_ENV_CL,PY_PIP_CI

pyenv=PY_ENV_CL('Windows-Exploit-Suggester',2).get_pyenv()
expsuggesterpy='./Library/Windows-Exploit-Suggester/Windows-Exploit-Suggester.py'
PY_PIP_CI(pyenv).ensure('xlrd')


def run(args):
    os.system(pyenv+' '+expsuggesterpy+' '+args)

def banner():
    print('[+]这里是使用windows内核信息提权的建议工具')
    print('[+]使用了github里的Windows-Exploit-Suggester')
    print('[+]首先需要目标机的systeminfo文件')
    print('[+]支持自动检测数据库过期情况')
    

def withexit_input(s):
    data=input(s).strip()
    if data=='exit()':exit(0)
    return data

def inputargs():
    systeminfo_path=withexit_input('systeminfo文件路径:')
    if not os.path.exists(systeminfo_path):
        print('[+]错误:文件不存在')
        return
    args='--database '+get_db()
    args+=' --systeminfo '+systeminfo_path
    
    return args


def scan_db():
    files=os.listdir('./Library/Windows-Exploit-Suggester/')
    xlsfile=[]
    for f in files:
        if f.endswith('xls'):
            xlsfile.append(f)
    return xlsfile


def update_db():
    run('--update')
    #移动文件
    filename= (time.strftime("%Y-%m-%d", time.localtime()))+'-mssb.xls'
    shutil.move(filename,'./Library/Windows-Exploit-Suggester/'+filename)


def clean_db():
    xlsfile=scan_db()
    if len(xlsfile)==1:return
    newest=xlsfile[0]
    for f in xlsfile:
        if int(f[:-9].replace('-',''))>int(newest[:-9].replace('-','')):newest=f
    #删除不是最新的
    xlsfile.remove(newest)
    for f in xlsfile:
        os.remove('./Library/Windows-Exploit-Suggester/'+f)

def get_db():
    db=scan_db()
    if len(db)==0:
        print('[!]错误:未检测到数据库文件,即将下载...')
        update_db()
    elif len(db)>1:
        clean_db()
    db=scan_db()
    if db[0]!=(time.strftime("%Y-%m-%d", time.localtime()))+'-mssb.xls':
        yn=input('[-]警告:数据库可能不是最新的,是否更新?(y/n)').strip().lower()
        if yn=='y':
            print('[+]更新数据库...')
            update_db()
            clean_db()
            db=scan_db()
    return './Library/Windows-Exploit-Suggester/'+db[0]
    



if __name__ == "__main__":
    banner()
    args=inputargs()
    run(args)