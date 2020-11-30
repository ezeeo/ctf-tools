#encoding:utf-8
#version 1.0

import os
import sys
if sys.platform=='linux':
    import readline
    
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from download_util import Aria2_Downloader
from auto_input import autokbex_input

def download():
    url=autokbex_input('url:')
    while 1:
        path=autokbex_input('path(默认为output):')
        if path=='':path='output'
        if os.path.exists(path):
            if os.path.isdir(path):
                break
            else:
                print('[!]路径必须是文件夹')
        else:
            print('[!]路径不存在')
    file_name=autokbex_input('filename:')
    t_num=autokbex_input('thread num(默认6):')
    if t_num=='':
        Dld=Aria2_Downloader(path)
    elif t_num.isdigit():
        Dld=Aria2_Downloader(path,int(t_num))
    else:
        print('[!]需要输入数字')
    Dld.download(url,file_name)

if __name__ == "__main__":
    download()


