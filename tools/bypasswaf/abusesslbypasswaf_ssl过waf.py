#conding=utf-8
#version 1.0

import sys
import os
if sys.platform=='linux':
    import readline
    
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
#print(path)
from py_env_util import PY_ENV_CL
from auto_input import autokbex_input

pyenv=PY_ENV_CL('abuse-ssl-bypass-waf',2).get_pyenv()
abusepy='./Library/abuse-ssl-bypass-waf/abuse-ssl-bypass-waf.py'


def run(args):
    os.system(pyenv+' '+abusepy+' '+args)

def banner():
    print('[+]这里是使用ssl协议绕过waf的工具')
    print('[+]使用了github里的abuse-ssl-bypass-waf')


def inputargs():
    target=autokbex_input('target(the host ip or domain):')
    regex=autokbex_input('regex(hit waf keyword or regex)')
    threads=autokbex_input('thread(numbers of multi threads):')

    args=''
    if target=='':
        print('[!]输入无效')
        return False
    else:
        args=args+'-target '+target
    if regex!='':
        args=args+' -regex '+regex
    if threads!='':
        args=args+' -thread '+threads
    return args



if __name__ == "__main__":
    banner()
    args=inputargs()
    run(args)
