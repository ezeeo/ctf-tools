#coding=utf-8
#version 1.0
import os


def fix(file_name):
    if not os.path.exists(file_name):
        print('file not exixts')
        return False
    head=[137,80,78,71,13,10,26,10]#png文件头
    b=b''
    with open(file_name,'rb') as f:
        b=f.read()
    ba=bytearray(b)
    for i in range(len(head)):
        ba[i]=head[i]
    with open(file_name+'.png','wb') as f:
        f.write(ba)
    return True


if __name__ == "__main__":
    path=input('input png filepath:')
    if path=='exit()':
        exit()
    if path[0]=='"' and path[-1]=='"':
        path=path[1:-1]
    if fix(path):
        print('done')
    else:
        print('error')