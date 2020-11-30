#获取直播真实地址
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

from file_scanner import scan_files
from py_env_util import PY_ENV_CL

print('[+]使用项目https://github.com/wbt5/real-url')


def scan_file():
    return scan_files('./Library/webcast_real_url',postfix='.py')


def read_files(flist):
    result=[]
    for l in flist:
        with open(l,'r',encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    result.append((l,line[1:].strip()))
                    break
    return result

def show_files(flist):
    for index,f in enumerate(flist):
        print(index+1,'->',f[1])


if __name__ == "__main__":
    pypath=PY_ENV_CL(None,3).get_pyenv()
    r=read_files(scan_file())
    print('[+]找到',len(r),'个转换脚本')
    show_files(r)
    while 1:
        uin=input('WebcastRealUrl-index>').strip()
        if uin=='':continue
        if uin=='exit()':exit(0)
        index=int(uin)
        target=r[index-1]
        os.system(pypath+' '+target[0])



