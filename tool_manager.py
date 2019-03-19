#!/usr/bin/env python
#coding=utf-8
import sys
import os
from enum import Enum

version='0.66'
pypath='python'

def init_pyenv():
    #设置pypath
    global pypath
    if len(sys.argv)==1:
        pass#正常启动
    elif len(sys.argv)==2:
        if sys.argv[1]=='#':#从文件读取
            if not os.path.exists('pytools.bat'):
                print('error:start script pytools.bat not exists')
                exit()
            find=False
            f=open('pytools.bat', 'r',encoding='UTF-8')
            for line in f:
                if line[:16]=='set python_path=':
                    pypath=line[17:-2]
                    find=True
                    break
            f.close()
            if find==False:
                print('error:can not find pyenv in pytools.bat')
                exit()
        else:
            pypath=sys.argv[1]
            pytoolsbat=''
            f=open('pytools.bat', 'r',encoding='UTF-8')
            for line in f:
                if line[:16]=='set python_path=':
                    line='set python_path="'+pypath+'"'
                pytoolsbat+=line+'\n'
            f=open('pytools.bat', 'w',encoding='UTF-8')
            f.write(pytoolsbat)
            f.close()

init_pyenv()
try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except:
    print('Detection of missing essential modules,now install...')
    os.system(pypath+' .\\install_module.py')
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process


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

def scan():#扫描存在的文件
    tool_list=scan_files('.\\tools\\',postfix=".py")
    version_list=[]
    for tool in tool_list:
        Find=False
        with open(tool,'r',encoding='utf-8') as f:
            for line in f:
                if line=='':
                    break
                if line[0]!='#':
                    break
                elif line[:8]=='#version':
                    version_list.append(line[8:].strip())
                    Find=True
                    break
        if Find==False:
            version_list.append('null')

    return tool_list,dict(zip(tool_list,version_list))
#文件猜测
def guessing(userinput,tool_list,is_print=False):
    max_matching=0
    i=-1
    path_num=-1
    for item in tool_list:
        i+=1
        if tool_list[i].find('_')!=-1:#有多个命名
            temp=tool_list[i].split('_')
            tempmax=0
            for alias in temp:
                match=fuzz.ratio(userinput,alias)
                if match>tempmax:
                    tempmax=match
            match=tempmax
        else:
            match=fuzz.ratio(userinput,item)
        if is_print==True and match>=50:
            print(tool_list[i])
        if match>max_matching:
            max_matching=match
            path_num=i
    #print('max match num='+str(max_matching))
    if max_matching<50:
        return -1
    return path_num
#获得猜测列表
def get_guesslist(tool_list):
    guess=[]
    for item in tool_list:
        guess.append(os.path.splitext(os.path.basename(item))[0])
    return guess

#命令分析
def code_analysis(s,tool_list):
    code_main=s.split(' ')[0]
    if code_main=='help':
        help()
    elif code_main=='show':
        show(s[5:],tool_list)
    elif code_main=='lib':
        lib(s[4:])
    elif code_main=='inputfile':
        inputfile(s[10:])
    elif code_main=='search':
        search(s[7:])
    elif code_main=='net':
        net(s[4:])
    elif code_main=='get'or code_main=='update':
        net(s)
    else:
        print('>>>Illegal instructions<<<')

#调用installer.exe进行网络操作
def net(s):
    global tool_list
    global version_dict
    global guess_list
    if os.path.exists('installer.exe'):
        op=s.split(' ')
        if len(op)==1:
            if op[0]=='up' or op[0]=='update':
                os.system('installer.exe update')
            elif op[0]=='upmain':
                os.system('installer.exe get_main')
            elif op[1]=='uptools':
                os.system('installer.exe get_tools')
            else:
                print('>>>no such code<<<')
                return
        elif len(op)==2 and op[1]=='-cover':
            if op[0]=='up' or op[0]=='update':
                os.system('installer.exe update_with_cover')
            elif op[0]=='upmain':
                os.system('installer.exe update_main')
            elif op[1]=='uptools':
                os.system('installer.exe update_tools')
            else:
                print('>>>no such code<<<')
                return
        elif len(op)==2 and (op[0]=='get' or op[0]=='update'):#获取单个模块
            target=''
            if op[0]=='update':
                num=guessing(op[1],guess_list)
                if num==-1:
                    print('>>>no such module<<<')
                    return
                target=tool_list[num]
            else:
                target=op[1]
            os.system('installer.exe '+op[0]+' '+target)
        else:
            print('>>>no such code<<<')
        print('---reload---')
        tool_list,version_dict=scan()
        guess_list=get_guesslist(tool_list)
        print('---reload success get '+str(len(tool_list))+' code block---')
    else:
        print('error:lost file->installer.exe')

#搜索匹配的模块
def search(instr):
    global guess_list
    print()
    guessing(instr,guess_list,True)
    print()


def help():
    print('tool_namager version '+version)
    print('使用‘exit()’退出程序或者模块')
    print('直接输入模块名以使用某模块(会进行名称的模糊匹配)')
    print('模块的调用支持参数和$传入缓冲区数据,例如 strto $')
    print('输入##会进入执行模式(将输入作为代码执行)')
    print('以#起始将会被判断为指令')
    print('可用的指令:')
    print('#help')
    print('#show modules | version')
    print('#reload')
    print('#lib check')
    print('#lib in(install) | inwc(installwithconfirm) | inwp(installwithupdatepip)')
    print('#inputfile [path] [mode(without_newline,without_space,without_all)]读取文件进入缓冲区')
    print('#$ 输出缓冲区($表示缓冲区),#$=xxx 进行手动赋值，仅识别为字符串')
    print('#search [modules name] 搜索当前名称下能匹配的模块')
    print('#net up(update) [-cover] 不覆盖的更新,带选项为覆盖 | net upmain [-cover](更新主程序) | net uptools [-cover](更新模块)')
    print('#get [module_path]来单独下载某个模块,#update [module/module path] 单独更新某个模块(可自动补全),module path可从./version_list中查看')
#show something
def show(argv,tool_list):
    global version_dict
    if argv=='modules':
        
        for i in tool_list:
            print(i[8:].replace('\\','->')+' '*(80-len(i))+'\t\t'+version_dict[i])
    elif argv=='version':
        print('tool_manager->'+version)
        print('install_module->',end='')
        sys.stdout.flush()
        os.system(pypath+' .\\install_module.py version')
        print('installer->',end='')
        sys.stdout.flush()
        os.system('installer.exe version')
        f=open('pytools.bat','r',encoding='utf-8')
        line=f.readline()
        f.close()
        print('pytools.bat->'+line[2:])
    else:
        print('>>>Illegal instructions<<<')


#install module的调用
def lib(argv):
    if argv=='check':
        os.system(pypath+' .\\install_module.py status')
    elif argv=='in' or argv=='install':
        os.system(pypath+' .\\install_module.py')
    elif argv=='inwc' or argv=='installwithconfirm':
        os.system(pypath+' .\\install_module.py withconfirm')
    elif argv=='inwp' or argv=='installwithupdatepip':
        os.system(pypath+' .\\install_module.py withupdatepip')
    else:
        print('>>>Illegal instructions<<<')

#读取文件到buffer
filereadmode = {
    "none":lambda s:s,
    "without_newline":lambda s:s.replace('\n','').replace('\r',''),
    "without_space":lambda s:s.replace(' ',''),
    "without_all":lambda s:s.replace('\n','').replace('\r','').replace('\n','').replace(' ','')
}
buffer=''
def inputfile(path_mode):
    arg=path_mode.split(' ')
    path=arg[0]
    mode=''
    if path=='':
        print('>>>no input path<<<')
        return
    global buffer
    if len(arg)>2:
        print('>>>too more args<<<')
        return
    elif len(arg)==2:
        mode=arg[1]
    try:
        f=open(path,'r',encoding='UTF-8')
        if mode in filereadmode:
            buffer=filereadmode[mode](f.read())
        else:
            buffer=f.read()
    except:
        print('>>>a except in inputfile()<<<')
        pass
    
#执行模式
def exec_mode():
    #exec('global buffer')
    while True:
        data=input('exec>')
        if data=='exit()':
            return
        elif data=='':
            continue
        else:
            if data.find('=')==-1 or data.find('==')!=-1:
                data='print('+data+')'
                pass
            exec(data.replace('$','buffer'))

#检查文件是否完全
def check_file():
    complete=True
    if not os.path.exists('installer.exe'):
        print('warning:Lack network access file->installer.exe')
        complete=False
    if not os.path.exists('HtmlAgilityPack.dll'):
        print('warning:Lack html parse file->HtmlAgilityPack.dll')
        complete=False
    if not os.path.exists('install_module.py'):
        print('warning:Lack pip install access file->install_module.py')
        complete=False
    if not os.path.exists('readme.txt'):
        print('info:Lack readme file->readme.txt')
    if not os.path.exists('pytools.bat'):
        print('info:Lack quick start file->pytools.bat')
    return complete

#------------------------------start------------------------------
print('version '+version)
if check_file()==False:
    a=input('warning:Lack some file , continue?(Some functions will not be available.)[y/n]')
    if a=='N' or a=='n':
        print('bye')
        exit(0)
    elif a=='Y' or a=='y':
        print('continue...')
    else:
        print('error input...now exit')
        exit()
tool_list,version_dict=scan()
guess_list=get_guesslist(tool_list)
print('use #help to view help')
print('------success get '+str(len(tool_list))+' code block------')
if os.path.exists('installer.exe'):
    print('Server message:')
    os.system('installer.exe serverinfo')
else:
    print('warning:Lack network access file->installer.exe')

if __name__ == '__main__':
    while True:
        code=input('>')
        if code=='exit()':
            exit(0)
        elif code=='':
            continue
        elif code[0]=='#':
            if code=='##':
                print()
                try:
                    exec_mode()
                except :
                    print('>>>Illegal code<<<')
                print()
            elif len(code)>=2 and code[0]=='#' and code[1]=='$':
                    if len(code)>=3 and code[2]=='=':
                        buffer=code[3:]
                    else:
                        print()
                        print(buffer)
            elif code=='#reload':
                print('---start scan---')
                tool_list,version_dict=scan()
                guess_list=get_guesslist(tool_list)
                print('---reload success get '+str(len(tool_list))+' code block---')
            else:
                code_analysis(code[1:],tool_list)
            continue
        path_num=guessing(code.split(' ')[0],guess_list)
        if path_num==-1:
            print('>>>Similarity is too low<<<\n')
            continue
        print('\nusing-->'+tool_list[path_num][8:-3].replace('\\','->'))
        os.system(pypath+' '+code.replace(code.split(' ')[0],tool_list[path_num]).replace('$','"'+buffer+'"'))
        print()