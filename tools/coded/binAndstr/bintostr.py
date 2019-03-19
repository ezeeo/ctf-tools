#coding=utf-8
#version 1.0
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
while True:
    data=input('convert bin to str>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(decode(addspace('0'+data.replace(' ',''))))