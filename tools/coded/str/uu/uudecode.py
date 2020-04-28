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
def bindecode(s):
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

def perexpansion(per):#格式化到6bit
    if len(per)>6:
        print('error')
        exit()
    elif len(per)==6:
        return per
    else:
        per='0'*(6-len(per))+per
        return per

def uudecode(s):
    sbin=binencode(s).replace(' ','')
    word_num=int(sbin[:8],2)-0x20#有多少个字符
    sbin=sbin[8:]
    outbin=''
    p=0#标记读取位置
    for i in range(len(sbin)//32):
        for j in range(4):#读4个字节，输出3个字节
            per=''#每一位
            #读8位
            for ii in range(8):
                per+=sbin[p]
                p=p+1
            if int(per,2)==0x60:#为0时设为0x60
                per='000000'
            else:
                per=perexpansion(bin((int(per,2)-0x20)).replace('0b', ''))
            outbin+=per
    #输出
    #print('--- ' +str(word_num)+'words ---')
    print(bindecode(addspace(outbin)))

while True:
    data=input('uudecode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    uudecode(data)