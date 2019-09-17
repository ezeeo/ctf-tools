import os

def read_pyenv():
    pypath=''
    find=False
    if not os.path.exists('pytools.bat'):
        print('warning:start script pytools.bat not exists')
    else:
        f=open('pytools.bat', 'r',encoding='UTF-8')
        for line in f:
            if line[:16]=='set python_path=' and line.strip()!='set python_path=""':
                pypath=line[17:-2]
                find=True
                break
        f.close()
    if not find:return False
    return pypath



def write_pyenv(pypath):
    pytoolsbat=''
    f=open('pytools.bat', 'r',encoding='UTF-8')
    for line in f:
        if line[:16]=='set python_path=':
            line='set python_path="'+pypath+'"'
        pytoolsbat+=line+'\n'
    f=open('pytools.bat', 'w',encoding='UTF-8')
    f.write(pytoolsbat)
    f.close()