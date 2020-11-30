#coding=utf-8
#version 1.3

import os,sys
import time
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
from env_variable_util import ENVIRONMENT_VARIABLE_UTIL_WIN
from auto_input import autokbex_input



print('[+]此模块索引环境变量里的可执行文件')
print('[+]输入名称返回绝对路径,例如输入python,返回c:\\pythohn3\python.exe')
print('[+]输入#输出所有环境变量匹配信息')

E=ENVIRONMENT_VARIABLE_UTIL_WIN(allow_suffixs=('*',),dir_black_list=tuple())
ex_match=autokbex_input('[+]立即启用额外匹配模式?(y/n)(进行忽略大小写和后缀的匹配)(会导致无法使用索引建立中的快速索引功能)').strip().lower()=='y'
if not ex_match:
    print('[+]额外匹配模式将在索引建立完成后启用')
else:
    print('[+]额外匹配模式已启用')
while 1:
    d=autokbex_input('win env match>')
    if not ex_match and E._indexing_down_get():
        ex_match=True
        print('[+]额外匹配模式已启用')
    stime=time.time()
    if d=='#':
        for k,v in E.getall().items():
            for l in v:
                print(k.center(37),'|',l)
    else:
        R=E.get_abspath(d,ex_match)
        t=int(1000*(time.time()-stime))
        print('@time',t,'ms')
        for p in R:
            print(p)

