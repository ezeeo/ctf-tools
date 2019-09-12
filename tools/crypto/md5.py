#coding=utf-8
#version 1.1
import os
import hashlib
import sys

#计算文件md5
def GetFileMd5(filename):
    if not os.path.exists(filename):
        print('file not found -> '+filename)
        return False
    if not os.path.isfile(filename):
        print('not a file -> '+filename)
        return False
    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

if len(sys.argv)==2:
    m=GetFileMd5(sys.argv[1])
    if m==False:
        pass
    else:
        print(m)
    exit()


if __name__ == "__main__":
    while True:
        data=input('md5>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        m=GetFileMd5(data)
        if m==False:
            continue
        else:
            print(m)