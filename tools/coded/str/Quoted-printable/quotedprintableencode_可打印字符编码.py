#coding=utf-8
#version 1.0
import quopri
import sys
if sys.platform=='linux':
    import readline
    
if len(sys.argv)==2:
    s=sys.argv[1]
    print()
    print(str(quopri.encodestring(s.encode('utf-8')),encoding='utf-8'))
    print()
    exit()

while True:
    q=input('input str>')
    if q=='exit()':
        exit()
    elif q=='':
        continue
    print(str(quopri.encodestring(q.encode('utf-8')),encoding='utf-8'))