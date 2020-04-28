#coding=utf-8
#version 1.2
import sys
if sys.platform=='linux':
    import readline
    
def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])
def addspace(s):
    result=''
    num=-1
    for i in s:
        num+=1
        if num==8:
            num=0
            result+=' '
        result+=i
    return result


if len(sys.argv)==2:
    data=sys.argv[1]
    data=bin(int(data))[2:]
    if len(data)%8!=0:
        data='0'*(8-len(data)%8)+data
    print(decode(addspace(data.replace(' ',''))))
    exit()

while True:
    data=input('convert int to str>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    data=bin(int(data))[2:]
    if len(data)%8!=0:
        data='0'*(8-len(data)%8)+data
    print(decode(addspace(data.replace(' ',''))))