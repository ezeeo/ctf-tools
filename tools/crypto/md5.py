#coding=utf-8
#version 1.3
import os
import hashlib
import sys
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from pbar import Pbar

#计算文件md5
def GetFileMd5(filename):
    bar=Pbar(info_len=35,allow_skip_frame=True)
    bar.start_bar()

    if not os.path.exists(filename):
        bar.print('file not found -> '+filename)
        bar.clear(True)
        return False
    bar.set_rate(10,'checking file...')
    if not os.path.isfile(filename):
        bar.print('not a file -> '+filename)
        bar.clear(True)
        return False
    bar.set_rate(20,'checking file...done')
    myhash = hashlib.md5()

    file_size=os.path.getsize(filename)//1024#kb

    f = open(filename, 'rb')
    bar.set_rate(30,'0/{}k reading file...'.format(file_size))
    
    persent=file_size//100

    next_show=persent
    readed=0
    while True:
        b = f.read(8096)
        if not b :
            break
        readed+=8
        if readed>next_show:
            next_show+=persent
            bar.set_rate(int(readed/file_size*70)+30,'{}/{}k reading file...'.format(readed,file_size))

        myhash.update(b)
    f.close()
    bar.set_rate(100,'reading file...done')
    bar.clear()
    return myhash.hexdigest()

def get_str_md5(s):
    myhash = hashlib.md5()
    myhash.update(s.encode(encoding='utf-8'))
    return myhash.hexdigest()

def get_md5(s):
    if os.path.exists(s):
        m=GetFileMd5(s)
        if m==False:
            pass
        else:
            print(m)
    else:
        print(get_str_md5(s))


if __name__ == "__main__":
    if len(sys.argv)==2:
        get_md5(sys.argv[1])
        exit()
    while True:
        data=input('md5>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        get_md5(data)