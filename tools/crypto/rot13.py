#coding=utf-8
#version 1.0
import sys
if sys.platform=='linux':
    import readline

def rot13(message):
    first = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    trance = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
    return message.translate(str.maketrans(first, trance))
while True:
    data=input('rot13>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(rot13(data))