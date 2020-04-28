#encoding:utf-8
#version 1.0
from zlib import *
import os,sys
if sys.platform=='linux':
    import readline
    
def decompresszlib(file_path):
    if not os.path.exists(file_path):
        print('[!]file not exists')
        exit()
    print('[+]reading...',end='')
    f=open(file_path,'rb')
    data = f.read()
    f.close()
    print('done\n[+]decompress...',end='')
    data = decompress(data)
    print('done\n[+]writing...',end='')
    f=open(file_path+'.dec','wb')
    f.write(data)
    f.close()
    print('done')


if __name__ == "__main__":
    file_path=input('input zlibcompress file:')
    if file_path=='exit()':
        exit()
    decompresszlib(file_path)