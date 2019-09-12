#coding=utf-8
#version 1.1
import sys

def expansion(s):
    if len(s)==1:
        return '0'+s
    return s

def encode(s):
    return ''.join([expansion(hex(ord(c)).replace('0x', '')) for c in s])

if len(sys.argv)==2:
    print('\n'+encode(sys.argv[1]))
    exit()

while True:
    data=input('convert str to hex>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(encode(data))