import os,sys

def read_pyenv():
    if sys.platform=='win32':
        if not os.path.exists('pytools.bat'):
            print('warning:start script pytools.bat not exists')
        else:
            return read_win_pyenv()
    elif sys.platform=='linux':
        if not os.path.exists('pytools.sh'):
            print('warning:start script pytools.sh not exists')
        else:
            return read_linux_pyenv()
    else:
        raise Exception('no support')

def read_win_pyenv():
    find=False
    f=open('pytools.bat', 'r',encoding='UTF-8')
    for line in f:
        if line[:16]=='set python_path=' and line.strip()!='set python_path=""':
            pypath=line[17:-2]
            find=True
            break
    f.close()
    if find:
        return pypath
    return False

def read_linux_pyenv():
    find=False
    f=open('pytools.sh', 'r',encoding='UTF-8')
    for line in f:
        if line[:12]=='python_path=' and line.strip()!='python_path=""':
            pypath=line[13:-2]
            find=True
            break
    f.close()
    if find:
        return pypath
    return False


def write_pyenv(pypath):
    if sys.platform=='win32':
        write_win_pyenv(pypath)
    elif sys.platform=='linux':
        write_linux_pyenv(pypath)
    else:
        raise Exception('no support')


def write_win_pyenv(pypath):
    pytoolsbat=''
    f=open('pytools.bat', 'r',encoding='UTF-8')
    for line in f:
        if line[:16]=='set python_path=':
            line='set python_path="'+pypath+'"\n'
        pytoolsbat+=line
    f=open('pytools.bat', 'w',encoding='UTF-8')
    f.write(pytoolsbat)
    f.close()

def write_linux_pyenv(pypath):
    pytoolsbat=''
    f=open('pytools.sh', 'r',encoding='UTF-8')
    for line in f:
        if line[:12]=='python_path=':
            line='python_path="'+pypath+'"\n'
        pytoolsbat+=line
    f=open('pytools.sh', 'w',encoding='UTF-8')
    f.write(pytoolsbat)
    f.close()