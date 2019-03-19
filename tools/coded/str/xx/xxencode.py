#coding=utf-8
#version 1.0

base="+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

#strtobin
def binencode(s):
    return ' '.join([expansion(bin(ord(c)).replace('0b', '')) for c in s])
def expansion(s):#每个的补全
    if(len(s)<8):
        num=8-len(s)
        for i in range(num):
            s='0'+s
    return s
#bintostr
def decode(s):
    return ''.join([base[i] for i in [int(b, 2) for b in s.split(' ')]])
def addspace(s):
    result=[]
    temp=''
    num=-1
    num2=0#字符数标记
    for i in s:
        num+=1
        if num==6:
            num=0
            num2+=1
            if num2==60:
                result.append(temp)
                temp=''
                num2=2
            else:
                temp+=' '
        temp+=i
    result.append(temp)
    return result

def sbinexpansion(sbin):#去除空格and整体补全
    sbin=sbin.replace(' ','')
    num=24-len(sbin)%24
    if num==24:
        return sbin
    sbin=sbin+'0'*num
    return sbin

def xxencode(s):
    num=len(s)%45##字符数
    num_list=[]
    for i in range(num//45):
        num_list.append('h')
    num_list.append(base[num])
    sbin=addspace(sbinexpansion(binencode(s)))
    num=0
    for i in sbin:
        print(num_list[num]+decode(i))
        num+=1


print('XXencode是一种二进制到文字的编码,在上世纪后期，IBM大型机中得到很广泛的应用。现在逐渐被Base64编码转换方法所取代了。')
print('输入要编码的字符串')

while True:
    data=input('xxencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    xxencode(data)