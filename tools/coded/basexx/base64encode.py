#version 1.0
import base64,sys
if sys.platform=='linux':
    import readline

while True:
    data=input('base64encode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    codestr = base64.b64encode(data.encode('utf-8'))
    print(str(codestr,'utf-8'))