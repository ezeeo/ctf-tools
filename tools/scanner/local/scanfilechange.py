#coding=utf-8
#version 1.0
import os
import hashlib
import sys
import shutil
import time
if sys.platform=='linux':
    import readline
    
#文件索引
def scan_files(directory,prefix=None,postfix=None):
    files_list=[]
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root,special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root,special_file))
            else:
                files_list.append(os.path.join(root,special_file))
    return files_list

def scan(s):#扫描存在的文件
    return scan_files(s)

#计算文件md5
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        print('list error:lost file -> '+filename)
        return ' '
    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_list_md5(file_list):
    md5_list=[]
    for filename in file_list:
        md5_list.append(GetFileMd5(filename))
    return md5_list

def write_file(name,file_list,md5_list):
    f = open(name, 'w',encoding='UTF-8')
    i=0
    for fil in file_list:
        if md5_list[i]==' ':
            print('a error md5 in file:'+fil+'now pass')
            continue
        f.write(fil+' '+md5_list[i]+'\n')
        i+=1
    f.close()
    print('write success')

def read_file(name):
    file_list=[]
    md5_list=[]
    f = open(name, 'r',encoding='UTF-8')
    while True:
        line=f.readline()
        if line=='' or line=='\n':
            break
        md5_list.append(line[-33:-1])
        file_list.append(line[:-34])
    f.close()
    return file_list,md5_list

#num为原始路径无关字符长度，即备份开始的那个文件夹之前的路径长
def monitor(path,file_list,md5_list,num,delayed):
    now_file_list=[]
    now_md5_list=[]
    i=0
    while True:
        now_file_list=scan(path)
        for fil in now_file_list:
            if fil not in file_list:

                #print(file_list)
                #input(fil)

                os.remove(fil)
                print('delete:'+fil)
        now_md5_list=get_list_md5(file_list)
        i=0
        for md5 in now_md5_list:
            if md5 not in md5_list:
                if not os.path.exists(os.path.dirname(file_list[i])):
                    print('recovery path:'+os.path.dirname(file_list[i]))
                    os.makedirs(os.path.dirname(file_list[i]))
                shutil.copyfile('./'+file_list[i][num:],file_list[i])
                #input('.\\'+file_list[i][num:])

                print('recovery:'+file_list[i])
            i+=1
        time.sleep(delayed)


gfile_list=[]
gmd5_list=[]

def main():
    global gfile_list
    global gmd5_list
    i=input('1.create md5list to file\n2.read md5list\n3.start monitor\n')
    if i=='1':
        path=input('scan target:')
        filename=input('save filename:')
        gfile_list=scan(path)

        print('file num='+str(len(gfile_list)))

        gmd5_list=get_list_md5(gfile_list)

        print('md5 num='+str(len(gmd5_list)))

        write_file(filename,gfile_list,gmd5_list)
        print('success')
    elif i=='2':
        filename=input('read md5 filename:')
        gfile_list,gmd5_list=read_file(filename)
        print('file num='+str(len(gfile_list)))
        print('md5 num='+str(len(gmd5_list)))
        print('success')
    elif i=='3':
        path=input('scan target:')
        num=input('path different len:')
        monitor(path,gfile_list,gmd5_list,int(num),1)

if __name__=='__main__':
    print('需要python3')
    print('此脚本用于监控文件夹的改变,并从备份文件进行恢复,以保证目录内容不会被更改')
    print('awd比赛用')
    print('备份文件夹需要存在在脚本同目录下')
    print('path different len 为原始路径无关字符长度，即备份开始的那个文件夹之前的路径长')
    print('如果监控的文件夹为E:/phpStudy/WWW/  且备份文件夹名称为WWW')
    print('则此参数值为len(E:/phpStudy/) 即12')
    while True:
        main()