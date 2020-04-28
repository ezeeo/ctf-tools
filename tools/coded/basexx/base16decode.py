#coding:utf-8
#version 1.1
import base64,sys
if sys.platform=='linux':
    import readline
    
while True:
    data=input('base16decode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    try:
        codestr = base64.b16decode(data.encode('utf-8'))
        print(str(codestr,'utf-8'))
    except:
        codestr = base64.b16decode(data.encode('ascii'))
        print(str(codestr,'ascii'))
        
