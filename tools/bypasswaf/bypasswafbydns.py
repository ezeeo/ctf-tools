#conding=utf-8
#version 1.0


import sys
import os
path=os.path.abspath('.')
if 'tools' in path:
    path=path.split('tools',maxsplit=1)[0]+'Library\\utils'
else:
    path=path+'\\Library\\utils'
if not path in sys.path:
    sys.path.append(path)
#print(path)
from wsl_env_util import WSL_ENV_CL

bashenv=WSL_ENV_CL().get_bashenv()
bypasssh='./Library/bypass-firewalls-by-DNS-history/bypass-firewalls-by-DNS-history.sh'


def run(args):
    os.system(bashenv+' '+bypasssh+' '+args)

def banner():
    print('[+]这里是使用dns历史纪录协议绕过waf的工具')
    print('[+]使用了github里的bypass-firewalls-by-DNS-history')

def withexit_input(s):
    data=input(s).strip()
    if data=='exit()':exit(0)
    return data



def inputargs():
    target=withexit_input('domain(domain to bypass):')
    listsubdomains=withexit_input('listsubdomains(list with subdomains for extra coverage)(y/n):').strip().lower()
    checkall=withexit_input('checkall(Check all subdomains for a WAF bypass)(y/n):').strip().lower()

    args=''
    if target=='':
        print('[!]输入无效')
        return False
    else:
        args=args+'-d '+target
    if listsubdomains!='':
        args=args+' -l'
    if checkall!='':
        args=args+' -a'
    return args



if __name__ == "__main__":
    banner()
    args=inputargs()
    run(args)

