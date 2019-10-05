#conding=utf-8
#version 1.1
import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from py_env_util import PY_ENV_CL

pyenv=PY_ENV_CL(None,2).get_pyenv()

sqlmap_config='./Library/sqlmap/config.ini'

def read_config():
    global sqlmap_config
    if os.path.exists(sqlmap_config):
        f=open(sqlmap_config,'r',encoding='utf-8')
        config=f.read().strip().split('\n')[0]
        return config
    return None


def check_config(config):
    if os.path.exists(config):return True
    return False

def input_config():
    sqlmappath=input('input sqlmap path:')
    return sqlmappath

def set_config(sqlmappath):
    f=open(sqlmap_config,'w',encoding='utf-8')
    f.write(sqlmappath)
    f.close()
    


if __name__ == "__main__":
    if len(sys.argv)>1:
        fd=read_config()
        if fd==None:
            print('[-]config not found')
            exit(1)
        else:
            if not check_config(fd):
                print('[-]config data error')
                exit(1)
            sqlmap=fd
            args=' '.join(sys.argv[1:])
            os.system(pyenv+' '+sqlmap+' '+args)
            exit(0)

    fd=read_config()
    if fd==None:
        print('[-]config not found')
        fd=input_config()
        if not check_config(fd):
            print('[-]config data error')
            exit(0)
        set_config(fd)
        sqlmap=fd
    else:
        if not check_config(fd):
            print('[-]config data error')
            fd=input_config()
            if not check_config(fd):
                print('[-]config data error')
                exit(0)
            set_config(fd)
        sqlmap=fd

    print('[+]pyenv :',pyenv)
    print('[+]sqlmap:',sqlmap)

    print('input "exit()" to exit')
    while True:
        args=input('sqlmap args>')
        if args=='exit()':break
        os.system(pyenv+' '+sqlmap+' '+args)
    #input('press anykey to exit')