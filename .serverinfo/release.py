import sys
import os
import shutil
path=os.path.abspath('..')

sys.path.append(path+'\\Library\\utils')
from extra_lib_download import shuld_download_data
base_path=os.path.abspath('..')

remove_list=['/Library/linux-soft-exploit-suggester/files_exploits.csv','/Library/Windows-Exploit-Suggester/*.xls','/Library/utils/aria2c.exe']
remove_list=[base_path+r for r in remove_list]

from matcher import Matcher
def cvl():
    from create_version_list import main
    main()

def extended_matching(removelist):
    result=[]
    for l in removelist:
        if '*' in l:
            path=l[:l.rfind('/')+1]
            name=l[l.rfind('/')+1:]
            files=os.listdir(path)
            for f in files:
                if Matcher(name,[]).is_match(f):
                    result.append(path+f)
        else:
            result.append(l)
    return result


def move_file(removelist):
    for l in removelist:
        t=base_path+'/output/'+l.split('/')[-1]
        if os.path.exists(t):
            os.remove(t)
        if os.path.exists(l):
            shutil.move(l,t)
        

def roolback_file(removelist):
    for l in removelist:
        t=base_path+'/output/'+l.split('/')[-1]
        if os.path.exists(l):
            os.remove(l)
        if os.path.exists(t):
            shutil.move(t,l)


def del_file():
    dir_del=['__pycache__']
    file_del=['*.pyc']
    ms=[Matcher(f,[]) for f in file_del]

    files_list=[]
    for root, sub_dirs, files in os.walk(base_path+'/Library'):
        for d in sub_dirs:
            if d in dir_del:
                os.removedirs(os.path.join(root,d))

        for special_file in files:
            f=os.path.join(root,special_file)
            for M in ms:
                if M.is_match(special_file):
                    os.remove(f)
                    break





if __name__ == "__main__":
    cvl()
    L=extended_matching(remove_list)
    #del_file()
    move_file(L)
    input('[+]进入部署模式.请开始同步到云端.按任意键回滚到正常模式')
    roolback_file(L)