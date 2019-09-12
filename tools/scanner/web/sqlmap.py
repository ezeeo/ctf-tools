#conding=utf-8
#version 1.1
import sys
import os
pyenv='python'
sqlmap_config='./Library/sqlmap/config.ini'

def read_config():
    global sqlmap_config
    if os.path.exists(sqlmap_config):
        f=open(sqlmap_config,'r',encoding='utf-8')
        config=f.read().strip().split('\n')
        if len(config)==2:
            return config
    return None


def check_config(config):
    if os.path.exists(config[1]):return True
    return False

def input_config():
    env=input('input python env:')
    sqlmappath=input('input sqlmap path:')
    return (env,sqlmappath)

def set_config(env,sqlmappath):
    f=open(sqlmap_config,'w',encoding='utf-8')
    f.write(env+'\n'+sqlmappath)
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
            pyenv=fd[0]
            sqlmap=fd[1]
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
        set_config(fd[0],fd[1])
        pyenv=fd[0]
        sqlmap=fd[1]
    else:
        if not check_config(fd):
            print('[-]config data error')
            fd=input_config()
            if not check_config(fd):
                print('[-]config data error')
                exit(0)
            set_config(fd[0],fd[1])
        pyenv=fd[0]
        sqlmap=fd[1]

    print('[+]pyenv :',pyenv)
    print('[+]sqlmap:',sqlmap)

    print('input "exit()" to exit')
    while True:
        args=input('sqlmap args>')
        if args=='exit()':break
        os.system(pyenv+' '+sqlmap+' '+args)
    #input('press anykey to exit')