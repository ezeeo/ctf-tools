#coding=utf-8
#version 1.0

import os,time,sys
if sys.platform=='linux':
    import readline
base_path=os.path.abspath('.')+'/output/runhtml/'

def create_tmp_path():
    if not os.path.exists(base_path):
        os.mkdir(base_path)


def write_html(data):
    fname=time.asctime(time.localtime(time.time())).replace(' ','_').replace(':','-')+'.html'
    with open(base_path+fname,'w',encoding='utf-8') as f:
        f.write(data)
    return fname

def open_html(name):
    tmp=base_path+name
    tmp=tmp.replace('/','\\')
    tmp='"'+tmp+'"'
    os.system(tmp)

html_head='''<!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8"> 
        <title></title>
        </head>
        <body><div>
'''
html_tail='''
</div></body></html>
'''

def delhtmls():
    for f in os.listdir(base_path):
        os.remove(base_path+f)

if __name__ == "__main__":
    create_tmp_path()
    headyn=input('auto add html head?(y/n)').strip().lower()
    if headyn=='y':
        print('[+]auto add html head and tail')
        headyn=True
    else:
        headyn=False
    while 1:
        data=input('data:')
        if data=='':
            continue
        if data=='exit()':
            break
        if headyn:
            data=html_head+data+html_tail
        open_html(write_html(data))
    delhtmls()