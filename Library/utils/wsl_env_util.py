import sys
import os
import configparser
import subprocess
import platform

class WSL_ENV_CL:

    def __init__(self):
        if not self._check_os():
            print('[!]错误,系统类型不符合要求')
            print('[+]必须是win10或linux')
            exit(1)
        if not self._check_bash():
            print('[!]错误:未检测到bash')
            exit(1)


    def get_bashenv(self):
        return 'bash'

    def _check_os(self):
        '''检查系统类型'''
        if platform.system()=='Linux':return True
        elif platform.system()=='Windows' and platform.version().split('.')[0]=='10':return True
        else:return False


    def _check_bash(self):
        '''检查bash是否正常'''
        s=subprocess.Popen(["bash","--version"],bufsize=0,stdout=subprocess.PIPE,universal_newlines=True)
        result=''
        while True:
            nextline=s.stdout.readline().strip()
            result+=nextline
            if nextline=="" and s.poll()!=None:
                break
        if 'GNU bash' in result:return True
        return False





if __name__ == "__main__":
    print(WSL_ENV_CL()._check_bash())