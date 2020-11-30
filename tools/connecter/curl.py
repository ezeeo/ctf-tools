#conding=utf-8
#version 1.1

import os,sys
if sys.platform=='linux':
    import readline


path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from auto_input import autokbex_input


def init_curl():
    if sys.platform=='win32':
        path='./Library/abuse-ssl-bypass-waf/curl/I386/CURL.EXE'
    else:
        path='curl'
    return path

curl=init_curl()


def run(args):
    os.system('""'+curl+'" '+args+'"')

def main():
    while 1:
        args=autokbex_input('curl>')
        run(args)


if __name__ == "__main__":
    if len(sys.argv)>1:
        run(' '.join(sys.argv[1:]))
    else:
        main()
