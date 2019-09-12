#coding=utf-8
#version 1.1
import sys
import os
import shutil
import datetime

pyenv='python'
dirsearch='./Library/dirsearch-master/dirsearch.py'
dir_path='./Library/dirsearch-master/'


def move_reports():
    for i in os.listdir(dir_path+'reports'):
        if os.path.isdir(dir_path+'reports/'+i):
            if os.path.exists('./output/dirsearch/report/'+i):
                shutil.rmtree('./output/dirsearch/report/'+i)
            shutil.move(dir_path+'reports/'+i,'./output/dirsearch/report/'+i)

def find_errors_log():
    '''查找最新的错误日志文件'''
    newly_logfile=''#最新的日志文件
    newly_logdate=None#最新的日志文件日期
    for i in os.listdir(dir_path+'logs'):
        if i[:7]=='errors-' and i[-3:]=='log':
            t='20'+i[7:-4]
            t=datetime.datetime.strptime(t, "%Y-%m-%d_%H-%M-%S")
            if newly_logdate==None:
                newly_logdate=t
                newly_logfile=i
            elif t>newly_logdate:
                newly_logdate=t
                newly_logfile=i
    return newly_logfile

def read_errors_log(file_name):
    if file_name=='':return ''
    file_path=dir_path+'logs/'+file_name
    if not os.path.exists(file_path):return ''
    with open(file_path,'r',encoding='utf-8') as f:
        data=f.read().strip()
    return data

def del_errors_log():
    for i in os.listdir(dir_path+'logs'):
        os.remove(dir_path+'logs/'+i)


def Post_processing(fd):
    '''执行的后处理'''
    if fd!=0:
        print('[!]dirsearch可能执行出错,返回值为:'+str(fd))
    move_reports()
    data=read_errors_log(find_errors_log())
    if data!='':
        print('[!]错误日志如下')
        print(data)
    del_errors_log()


def clear():
    if os.sys.platform=='win32':
        os.system('cls')
    else:
        os.system('clear')

if __name__ == "__main__":
    if len(sys.argv)>1:
        args=' '.join(sys.argv[1:])
        #clear()
        fd=os.system('start /WAIT '+pyenv+' '+dirsearch+' '+args+' /K')
        Post_processing(fd)
        exit(fd)

    print('[+]  pyenv  :',pyenv)
    print('[+]dirsearch:',dirsearch)

    print('input "exit()" to exit')
    while True:
        args=input('dirsearch args>')
        if args=='exit()':break
        elif args.strip()=='':continue
        #clear()
        fd=os.system('start /WAIT '+pyenv+' '+dirsearch+' '+args+' /K')
        Post_processing(fd)
