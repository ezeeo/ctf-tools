#coding=utf-8
#version 1.0
import os
import re
import sys
if sys.platform=='linux':
    import readline
def write(hexs):
    if len(hexs)%2!=0:
        hexs+='0'
    ba=[]
    print('convert...',end='')
    for i in range(len(hexs)//2):
        ba.append(int(hexs[i*2:(i+1)*2],base=16))
    print('done\nwriting...',end='')
    ba=bytearray(ba)
    with open('./output/hexstream','wb') as f:
        f.write(ba)
    print('done')


if __name__ == "__main__":
    hexstream=input('input hex stream:')
    if hexstream=='exit()':
        exit()
    if os.path.exists(hexstream):
        f=open(hexstream,'r')
        hexstream=f.read()
        f.close()
    hexstream=hexstream.lower()
    if hexstream[0]=='0' and hexstream[1]=='x':
        hexstream=hexstream[2:]

    if not re.match('[0-9a-f]',hexstream):
        print('must hex stream')
        exit()
    write(hexstream)