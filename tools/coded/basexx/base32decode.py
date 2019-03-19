#version 1.0
import base64
while True:
    data=input('base32decode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = base64.b32decode(data.encode('utf-8'))
    try:
        print(str(codestr,'utf-8'))
    except:
        print('except:encoding utf-8')
        print(codestr)