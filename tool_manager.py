#!/usr/bin/env python
#coding=utf-8
import sys
import os
import string
#from enum import Enum
if sys.platform=='linux':
    import readline

from Library.utils.file_scanner import scan_files
from Library.utils.file_input import inputfile
from Library.utils.exec_mode import exec_mode
from Library.utils.start_py_env import read_pyenv,write_pyenv
from Library.utils.network_usage import check_use_net
from Library.utils.help_info import help_info
from Library.utils.pbar import Pbar
from Library.utils.run_sys_agent import agent_system
from Library.utils.wsl_env_util import WSL_ENV_CL
from Library.utils.env_variable_util import ENVIRONMENT_VARIABLE_UTIL_WIN
from Library.utils.auto_input import autokbex_input

version='0.78'
pypath='python'

def init_pyenv():
    if sys.version[0]!='3':
        print('error:You must start with Python 3')
        exit(1)
    #设置pypath
    global pypath
    if len(sys.argv)==1:#正常启动
        print('normal start')
        pass
    elif len(sys.argv)==2:
        if sys.argv[1]=='#':#从文件读取
            find=read_pyenv()
            if find==False:
                print('error:can not find pyenv in pytools.bat')
                exit()
            pypath=find
        else:#写入指定的pypath
            pypath=sys.argv[1]
            write_pyenv(pypath)


def init_lib():
    from install_module import bar_status
    bar_status()


def init_ext_lib():
    from Library.utils.extra_lib_download import ext_downloader,shuld_download_data
    try:
        ext_downloader(shuld_download_data).download_ext()
    except Exception as ex:
        print('error:extra lib download fail->'+str(ex))


init_pyenv()
print('pypath:'+pypath)

init_lib()
init_ext_lib()

try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except:
    print('Detection of missing essential modules,now install...')
    os.system(pypath+' ./install_module.py')
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process




def scan():#扫描存在的文件
    tool_list=scan_files('./tools/',postfix=".py")
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
        help_info(version)
    elif code_main=='show':
        show(s[5:],tool_list)
    elif code_main=='lib':
        lib(s[4:])
    elif code_main=='inputfile':
        global buffer
        buffer=inputfile(s[10:])
    elif code_main=='search':
        search(s[7:])
    elif code_main=='net':
        net(s[4:])
    elif code_main=='get'or code_main=='update':
        net(s)
    elif code_main=='cmd':
        cmd(s)
        print()
    elif code_main=='bash':
        try:
            env=WSL_ENV_CL().get_bashenv()
        except Exception as ex:
            print('[!]error in get wsl env ->',str(ex))
            return
        bash(s,env)
        print()
    else:
        print('>>>Illegal instructions<<<')

def cmd(s):
    if sys.platform!='win32':
        print('[!]platform error')
    os.system('title cmd')
    s=s.strip()
    if len(s)==3:
        while 1:
            cmd=autokbex_input('cmd>',handle_kbex=lambda :'exit()',exitsign=None).strip()
            if cmd=='':continue
            if cmd=='exit()':
                return
            try:
                os.system(cmd)
            except KeyboardInterrupt as ex:
                pass
    else:
        try:
            os.system(s[3:])
        except KeyboardInterrupt as ex:
            pass
        

def bash(s,env):
    os.system('title bash')
    s=s.strip()
    if len(s)==4:
        while 1:
            cmd=autokbex_input('bash>',handle_kbex=lambda :'exit()',exitsign=None).strip()
            if cmd=='':continue
            if cmd=='exit()':
                return
            try:
                os.system(env+' -c "'+cmd+'"')
            except KeyboardInterrupt as ex:
                pass
            
    else:
        try:
            os.system(env+' -c "'+s[4:]+'"')
        except KeyboardInterrupt as ex:
            pass
        


#调用installer.exe进行网络操作
def net(s):
    global tool_list
    global version_dict
    global guess_list
    if not check_use_net():
        print('info:network disable ->check on pytools.bat->::net=0, if net=1 ,it will enabled')
        return

    op=s.split(' ')
    if len(op)==1:
        if op[0]=='up' or op[0]=='update':
            os.system('installer.exe update')
        elif op[0]=='upmain':
            os.system('installer.exe get_main')
        elif op[0]=='uptools':
            os.system('installer.exe get_tools')
        elif op[0]=='getv' or op[0]=='get_version_list':
            os.system('installer.exe get_version_list')
            return
        else:
            print('>>>no such code<<<')
            return
    elif len(op)==2 and op[1]=='-cover':
        if op[0]=='up' or op[0]=='update':
            os.system('installer.exe update_with_cover')
        elif op[0]=='upmain':
            os.system('installer.exe update_main')
        elif op[0]=='uptools':
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
        return

    print('---reload---')
    tool_list,version_dict=scan()
    guess_list=get_guesslist(tool_list)
    print('---reload success get '+str(len(tool_list))+' tools---')


#搜索匹配的模块
def search(instr):
    global guess_list
    print()
    guessing(instr,guess_list,True)
    print()



#show something
def show(argv,tool_list):
    global version_dict
    if argv=='modules':
        maxlen=100
        for i in tool_list:
            mname=i[8:].replace('\\','->').replace('/','->')
            v=version_dict[i]
            snum=maxlen-len(mname)-len(v)-sum(n not in string.printable for n in mname)
            if snum<0:
                mname=mname[abs(snum):]
            print(mname+' '*(snum)+v)
    elif argv=='winenv':
        for k,v in WINenvs.getall().items():
            for l in v:
                print(k.center(37),'|',l)

    elif argv=='version':
        print('tool_manager->'+version)
        print('install_module->',end='')
        sys.stdout.flush()
        os.system(pypath+' ./install_module.py version')
        if check_use_net():
            print('installer->',end='')
            sys.stdout.flush()
            os.system('installer.exe version')
        else:
            print('installer->?(disable net)')
        f=open('pytools.bat','r',encoding='utf-8')
        line=f.readline()
        f.close()
        print('pytools.bat->'+line[2:])
    else:
        print('>>>Illegal instructions<<<')


#install module的调用
def lib(argv):
    if argv=='check':
        os.system(pypath+' ./install_module.py status')
    elif argv=='in' or argv=='install':
        os.system(pypath+' ./install_module.py')
    elif argv=='inwc' or argv=='installwithconfirm':
        os.system(pypath+' ./install_module.py withconfirm')
    elif argv=='inwp' or argv=='installwithupdatepip':
        os.system(pypath+' ./install_module.py withupdatepip')
    else:
        print('>>>Illegal instructions<<<')

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
    if not os.path.exists('output'):
        os.mkdir('output')
    return complete


def run_tool(path_num,tool_list,pypath,code,buffer):
    if pypath=='':
        print('\nusing-->'+tool_list[path_num])
    else:
        print('\nusing-->'+tool_list[path_num][8:-3].replace('\\','->').replace('/','->'))
    try:
        if sys.platform=='win32':
            if pypath=='':
                now_title=tool_list[path_num]
            else:
                now_title=tool_list[path_num][8:-3].replace('\\','-').replace('/','-')
            os.system('title '+now_title)

        if pypath=='':
            os.system(code.replace(code.split(' ')[0],tool_list[path_num]).replace('$','"'+buffer+'"'))
        else:
            os.system(pypath+' '+code.replace(code.split(' ')[0],tool_list[path_num]).replace('$','"'+buffer+'"'))


    except KeyboardInterrupt as ex:
        pass


#------------------------------start------------------------------
print('version '+version)
if check_file()==False:
    a=autokbex_input('warning:Lack some file , continue?(Some functions will not be available.)[y/n]').lower()
    if a=='n':
        print('bye')
        exit(0)
    elif a=='y':
        print('continue...')
    else:
        print('error input...now exit')
        exit()
tool_list,version_dict=scan()
guess_list=get_guesslist(tool_list)
if sys.platform=='win32':
    WINenvs=ENVIRONMENT_VARIABLE_UTIL_WIN(allow_suffixs=('exe',))
print('use #help to view help')
print('------success get '+str(len(tool_list))+' tools------')
if os.path.exists('installer.exe'):
    if check_use_net():
        bar=Pbar()
        bar.start_bar()
        bar.set_rate(None,'get server message...')
        code,result=agent_system('installer.exe serverinfo')
        bar.clear(True)
        if code==0:
            print('Server message:')
            print(result.strip())
        else:
            print('[!]error in get server message. info:')
            print(result.strip())
    else:
        print('info:network disable ->check on pytools.bat->::net=0, if net=1 ,it will enabled')
else:
    print('warning:Lack network access file->installer.exe')

buffer=''
now_title='pytools'
if sys.platform=='win32':
    os.system('title pytools')


if __name__ == '__main__':
    while True:
        if sys.platform=='win32' and now_title!='pytools':
            os.system('title pytools')
        
        code=autokbex_input('>',handle_kbex=lambda :None)
        if code==None:
            print('\r[!]input exit() to exit')
            continue
        code=code.strip()
        if code=='':
            continue
        elif code[0]=='#':
            if code=='##':
                print()
                try:
                    exec_mode()
                except :
                    print('>>>exec error<<<')
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
                print('---reload success get '+str(len(tool_list))+' tools---')
            else:
                try:
                    code_analysis(code[1:],tool_list)
                except Exception as ex:
                    print('[!]error ->',str(ex))
            continue

        #处理->等
        code=code.split(' ',maxsplit=1)
        code[0]=code[0].split('->')[-1].split('.')[0]
        code=' '.join(code)
        
        path_num=guessing(code.split(' ')[0],guess_list)
        if path_num==-1:
            #尝试索引环境变量
            if sys.platform=='win32':
                all_win_env=WINenvs.getall_name()
                path_num=guessing(code.split(' ')[0],all_win_env)
        else:
            run_tool(path_num,tool_list,pypath,code,buffer)
            now_title=''
            print()
            continue
        if path_num==-1:
            print('>>>Similarity is too low<<<\n')
        else:
            if autokbex_input('[-]matcah external program -> '+all_win_env[path_num]+' ,run it?(y/n)').strip().lower()=='y':
                run_tool(path_num,all_win_env,'',code,buffer)
                now_title=''
            print()
            continue
        