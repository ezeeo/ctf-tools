#coding=utf-8
#version 1.1

import sys

def tab_to_8(binip):
    if len(binip)>8:
        raise Exception('lenth error')
    return '0'*(8-len(binip))+binip

def dot_to_bin(ip):
    ip=str(ip)
    if ip.count('.')!=3:
        return False
    ip=ip.split('.')
    return ''.join([tab_to_8(str(bin(int(i,base=10)))[2:]) for i in ip])

def int_to_dot(ip):
    ip=bin(ip)[2:]
    if len(ip)>32:
        return False
    ip='0'*(32-len(ip))+ip
    return '.'.join([str(int(ip[i*8:(i+1)*8],base=2)) for i in range(4)])

def dot_to_oct(dot_ip):
    ip=dot_ip.split('.')
    if len(ip)!=4:
        return False
    return '0'+'.'.join([oct(int(i))[2:] for i in ip])

def main(ip):
    out='dot: {}\nbin: {}\nhex: {}\nint: {}\noct: {}'
    if ip=='exit()':
        exit()
    elif ip[:2]=='0b' or ip[:2]=='0x' or ip.find('.')==-1:#二进制输入||十六进制输入||十进制输入
        ip=int(ip)
        dot_ip=int_to_dot(ip)
        if dot_ip==False:
            print('ip format error')
            return
    else:
        bin_ip=dot_to_bin(ip)
        if bin_ip==False:#格式不正确
            print('ip format error')
            return
        dot_ip=ip
        ip=int(bin_ip,base=2)
    #输出
    print(out.format(dot_ip,bin_ip,hex(int(bin_ip,base=2))[2:],ip,dot_to_oct(dot_ip)))


if len(sys.argv)==2:
    ip=sys.argv[1]
    print()
    main(ip)
    exit()

print('ps:输入二进制ip需要以0b开头,十六进制以0x开头')
if __name__ == "__main__":
    while True:
        ip=input('input ip:')
        main(ip)