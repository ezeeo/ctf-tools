#version 1.3
import base64
import sys

print('在附加参数调用时可选两参数为[数据] [次数]')

if len(sys.argv)==2:#传入数据
    print(str(base64.b64decode((sys.argv[1]+'==').encode('utf-8')),'utf-8'))
    exit()

if len(sys.argv)==3:#传入数据和轮数
    num=int(sys.argv[2])
    tmp=sys.argv[1]
    for i in range(num):
        tmp=str(base64.b64decode((tmp+'==').encode('utf-8')),'utf-8')
    print(tmp)


while True:
    data=input('base64decode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    data+='=='
    codestr = base64.b64decode(data.encode('utf-8'))
    try:
        print(str(codestr,'utf-8'))
    except:
        print('except:encoding utf-8')
        print(codestr)
        print()
    