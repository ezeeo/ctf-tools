#conding=utf-8
#version 2.0

import requests
import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
#print(path)
from py_env_util import PY_ENV_CL

pyenv=PY_ENV_CL('linux-soft-exploit-suggester',2).get_pyenv()
expsuggesterpy='./Library/linux-soft-exploit-suggester/linux-soft-exploit-suggester.py'

from download_util import Aria2_Downloader
from pbar import Pbar

def run(args):
    os.system(pyenv+' '+expsuggesterpy+' '+args)

def banner():
    print('[+]这里是使用linux软件包提权的建议工具')
    print('[+]使用了github里的linux-soft-exploit-suggester')
    a='''  Get Package List:
debian/ubuntu: dpkg -l > package_list
redhat/centos: rpm -qa > package_list'''
    print('[+]首先需要'+a)


def withexit_input(s):
    data=input(s).strip()
    if data=='exit()':exit(0)
    return data

def inputargs():
    softlist_path=withexit_input('软件包列表文件路径:')
    if not os.path.exists(softlist_path):
        print('[+]错误:文件不存在')
        return
    args='--db ./Library/linux-soft-exploit-suggester/files_exploits.csv '
    args+='--file '+softlist_path
    
    return args


def update_db():
    if not os.path.exists('./Library/linux-soft-exploit-suggester/files_exploits.csv'):
        print('[!]未找到数据库...开始下载')
        url='https://raw.githubusercontent.com/offensive-security/exploit-database/master/files_exploits.csv'
        D=Aria2_Downloader('./Library/linux-soft-exploit-suggester')
        D.download(url,'files_exploits.csv')
        set_locat_ver(get_web_ver())
        print('[+]下载数据库完成')
    else:
        print('[+]检查数据库更新...')
        bar=Pbar()
        bar.start_bar()
        bar.set_rate(0,'检查更新中...')
        if get_local_ver()<get_web_ver():
            bar.print('[+]发现数据库更新')
            bar.hidden(False)
            del_db()
            url='https://raw.githubusercontent.com/offensive-security/exploit-database/master/files_exploits.csv'
            D=Aria2_Downloader('./Library/linux-soft-exploit-suggester')
            print('[+]开始下载最新数据库')
            D.download(url,'files_exploits.csv')
            set_locat_ver(get_web_ver())
            print('[+]更新数据库完成')
        else:
            bar.hidden(False)
            print('[+]未找到更新')
        bar.clear()


def del_db():
    if os.path.exists('./Library/linux-soft-exploit-suggester/files_exploits.csv'):
        os.remove('./Library/linux-soft-exploit-suggester/files_exploits.csv')


def get_web_ver():
    #获取release数量
    r=requests.get('https://github.com/offensive-security/exploitdb')
    release_num=int(r.text.split('/offensive-security/exploitdb/releases')[1].split('releases')[0].split('num text-emphasized')[1].split('\n')[1].strip())
    return release_num


def get_local_ver():
    if os.path.exists('./Library/linux-soft-exploit-suggester/db_ver.ini'):
        with open('./Library/linux-soft-exploit-suggester/db_ver.ini','r',encoding='utf-8') as f:
            ver=int(f.readline().strip())
        return ver
    else:
        return 0

def set_locat_ver(v):
    with open('./Library/linux-soft-exploit-suggester/db_ver.ini','w',encoding='utf-8') as f:
        f.write(str(v))

if __name__ == "__main__":
    banner()
    update_db()
    args=inputargs()
    run(args)