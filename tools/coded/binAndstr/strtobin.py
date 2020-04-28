#coding=utf-8
#version 1.1
import sys
if sys.platform=='linux':
    import readline
    
def encode(s):
    return ' '.join([expansion(bin(ord(c)).replace('0b', '')) for c in s])
def expansion(s):
    if(len(s)<8):
        num=8-len(s)
        for i in range(num):
            s='0'+s
    return s

if len(sys.argv)==2:
    print('\n'+encode(sys.argv[1]).replace(' ',''))
    exit()

while True:
    data=input('convert str to bin>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(encode(data).replace(' ',''))