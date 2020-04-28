#encoding:utf-8
#version 1.0
import os
import base64   
import sys
if sys.platform=='linux':
    import readline
    
def get(instr):
    if os.path.exists(instr):
        f=open(instr,'r',encoding='utf-8')
        s=f.read()
        f.close()
    else:
        s=instr
    if s[:22]=='data:image/jpg;base64,':
        s=s[22:]
    elif s[:10]=='data:image':
        s=s[strs.find(','):]
    return s

def write(strs):
    img = base64.b64decode(strs)
    f = open('./output/b64.jpg','wb')
    f.write(img)
    f.close()
    print('[+]save to ./output/b64.jpg')
    o=input('open?')
    if o=='Y' or o=='y':
        os.system('start ./output/b64.jpg')

if len(sys.argv)==2:
    strs = sys.argv[1] # 读取命令行中输入的参数，即base64字符串
    strs=get(strs)
    write(strs)
    

if __name__ == "__main__":
    instr=input('input b64 or file path:')
    if instr=='exit()':exit()
    instr=get(instr)
    write(instr)