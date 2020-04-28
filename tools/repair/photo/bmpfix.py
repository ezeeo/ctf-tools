#coding=utf-8
#version 1.0
import os,sys
if sys.platform=='linux':
    import readline

def check(file_name):
    print('check file...',end='')
    if not os.path.exists(file_name):
        print('file not exixts')
        return False
    head=[0x42,0x4D]
    biSize=0x28#index=14,表示位图信息头的大小
    biPlanes=0x1#index=26,固定为1
    b=b''
    with open(file_name,'rb') as f:
        b=f.read()
    ba=bytearray(b)
    print('exixts\ncheck format...',end='')
    if ba[0]!=head[0] and ba[1]!=head[1] and ba[14]!=biSize and ba[26]!=biPlanes:
        print('Mismatch')
        return False
    else:
        print('Match')
        ba[0]=head[0]
        ba[1]=head[1]
        ba[14]=biSize
        ba[26]=biPlanes
        return ba

def fix(file_name,ba):
    with open(file_name+'.bmp','wb') as f:
        f.write(ba)

if __name__ == "__main__":
    f=input('input bmp file path:')
    if f=='exit()':
        exit()
    if f[0]=='"' and f[-1]=='"':
        f=f[1:-1]
    ba=check(f)
    if ba==False:
        exit()
    else:
        fix(f,ba)