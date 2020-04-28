#coding=utf-8
#version 1.0
import sys
if sys.platform=='linux':
    import readline

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

def sbinexpansion(sbin):#去除空格and整体补全
    sbin=sbin.replace(' ','')
    num=24-len(sbin)%24
    if num==24:
        return sbin
    sbin=sbin+'0'*num
    return sbin

def uuencode(s):
    sbin=sbinexpansion(binencode(s))
    outbin=''
    perline=''#每一行的输出字符
    perline_num=0
    p=0#标记读取位置
    for i in range(len(sbin)//24):
        for j in range(4):#读3个字节，输出四个字节
            per='00'#每一位
            #读6位
            for ii in range(6):
                per+=sbin[p]
                p=p+1
            if int(per)==0:#为0时设为0x60
                per='01100000'
                perline_num-=1
            else:
                per=expansion(bin(int(per,2)+0x20).replace('0b', ''))
            outbin+=per
        perline_num+=3
        if perline_num==45:#达到一行上限，输出
           print('M'+decode(addspace(outbin)))
           outbin=''
           perline_num=0
    #输出不足一整行的部分
    print(chr(perline_num+0x20)+decode(addspace(outbin)))

print('UUencode是一种二进制到文字的编码！它不是MIME编码中一员。最早在unix 邮件系统中使用，全称：Unix-to-Unix encoding')
print('输入要编码的字符串')

while True:
    data=input('uuencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    uuencode(data)