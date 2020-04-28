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
    print('exists\ncheck zip head...',end='')
    head=[0x50,0x4b,0x03,0x04]#zip文件头
    b=b''
    with open(file_name,'rb') as f:
        b=f.read()
    ba=bytearray(b)
    for i in range(len(head)):
        if ba[i]!=head[i]:
            print('error')
            return False
    print('pass\ncheck Global Encryption Flag 2byte...',end='')
    if ba[5]==0x00 and ba[6]==0x09:
        print('Encrypted')
        return ba
    elif ba[5]==0x00 and ba[6]==0x00:
        print('Unencrypted')
        return False
    else:
        print('zip format error')
        return False

def clean_flag(filename,ba):
    print('write to '+filename+'.zip...',end='')
    ba[6]=0
    with open(filename+'.zip','wb') as f:
        f.write(ba)
    print('done')

print('修复zip伪加密')
if __name__ == "__main__":
    f=input('input zip file path:')
    if f=='exit()':
        exit()
    if f[0]=='"' and f[-1]=='"':
        f=f[1:-1]
    ba=check(f)
    if ba==False:
        exit()
    else:
        clean_flag(f,ba)