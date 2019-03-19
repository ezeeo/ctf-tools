#coding=utf-8
import os
import sys
try:
    import pip
except:
    print('error in install : must have module pip')
    exit()
from pip._internal.utils.misc import get_installed_distributions
from subprocess import call
from time import sleep

version='1.2'
pypath='python'

def get_pyenv():
    global pypath
    if not os.path.exists('pytools.bat'):
        print('warning:start script pytools.bat not exists')
    else:       
        f=open('pytools.bat', 'r',encoding='UTF-8')
        for line in f:
            if line[:16]=='set python_path=' and line.strip()!='set python_path=""':
                pypath=line[17:-2]
                break
        f.close()



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


def scan():#扫描存在的文件
    return scan_files('.\\tools\\',postfix=".py")
def requisite_pip_module():#请求安装的
    file_list=scan()
    result=['fuzzywuzzy','python-Levenshtein']
    for path in file_list:
        f = open(path, 'r',encoding='UTF-8')
        while True:
            line=f.readline()
            if line=='':
                break
            if line[0]!='#':
                break
            elif line[:7]!='#import':
                continue
            else:
                result.append(line[8:-1])
        f.close()
    return list(set(result))

def should_install_modules(module_list):#需要安装的
    mo=get_installed_distributions()
    modules=[]
    for i in mo:
        modules.append(str(i).split(' ')[0])
    #print(modules)
    should=[]
    for i in module_list:
        if i not in modules:
            should.append(i)
    return should

def auto_install(module_list,confirm):#安装
    for mo in module_list:
        #print('pip install '+mo)
        if confirm==True:
            input('now install ' + mo + ', press any key to continue')
        os.system(pypath+' -m pip install '+mo)

def default(confirm):
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
        print('---------------end---------------')
        exit(0)
    print('should install num '+str(len(li)))
    if confirm==True:
        print(li)
        input('please confirm pip is installed press any key to continue')
    print('---------------start installing---------------')
    auto_install(li,confirm)
    print('---------------end---------------')

def show_status():
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
    else:
        print('should install num '+str(len(li)))
        print(li)
    print('---------------end---------------')

def withupdatepip():
    print('---------------start---------------')
    li=requisite_pip_module()
    print('request module num '+str(len(li)))
    li=should_install_modules(li)
    if len(li)==0:
        print('no modules should install')
        print('---------------end---------------')
        exit(0)
    print('upgrade pip')
    os.system(pypath+' -m pip install --upgrade pip')
    print('should install num '+str(len(li)))
    print('---------------start installing---------------')
    auto_install(li,False)
    print('---------------end---------------')

if __name__ =='__main__':
    get_pyenv()
    if len(sys.argv)==1:
        default(False)
    elif sys.argv[1]=='version':
        print(version)
    elif sys.argv[1]=='status':#显示状态
        show_status()
    elif sys.argv[1]=='withupdatepip':
        withupdatepip()
    elif sys.argv[1]=='withconfirm':
        default(True)