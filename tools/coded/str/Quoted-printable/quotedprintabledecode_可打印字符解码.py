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
    success=False
    try:
        print(str(quopri.decodestring(q),encoding='utf-8'))
        success=True
    except Exception as ex:
        print('except in encode utf-8')
    if not success:
        try:
            print(str(quopri.decodestring(q),encoding='unicode'))
            success=True
        except Exception as ex:
            print('except in encode unicode')
    if not success:
        try:
            print(str(quopri.decodestring(q),encoding='gbk'))
            success=True
        except Exception as ex:
            print('except in encode gbk')
    if not success:
        try:
            print(str(quopri.decodestring(q),encoding='utf8'))
            success=True
        except Exception as ex:
            print('except in encode utf8')
    if not success:
        print(quopri.decodestring(q))
    