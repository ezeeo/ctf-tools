#coding=utf-8
#version 1.0
import quopri
import sys

if len(sys.argv)==2:
    s=sys.argv[1]
    print()
    print(str(quopri.decodestring(s),encoding='utf-8'))
    print()
    exit()

while True:
    q=input('input Quoted-printable>')
    if q=='exit()':
        exit()
    elif q=='':
        continue
    print(str(quopri.decodestring(q),encoding='utf-8'))