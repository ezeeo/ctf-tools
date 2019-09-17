#conding=utf-8
#version 1.1

import os,sys

def init_curl():
    if sys.platform=='win32':
        path='./Library/abuse-ssl-bypass-waf/curl/I386/CURL.EXE'
    else:
        path='curl'
    return path

curl=init_curl()

def withexit_input(*s,**d):
    data=input(*s,**d).strip()
    if data=='exit()':exit(0)
    return data

def run(args):
    os.system('""'+curl+'" '+args+'"')

def main():
    while 1:
        args=withexit_input('curl>')
        run(args)


if __name__ == "__main__":
    if len(sys.argv)>1:
        run(' '.join(sys.argv[1:]))
    else:
        main()
