#coding=utf-8
#version 1.1

import os,sys
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
from env_variable_util import ENVIRONMENT_VARIABLE_UTIL
from tool_input import withexit_input



print('[+]此模块索引环境变量里的可执行文件')
print('[+]输入名称返回绝对路径,例如输入python,返回c:\\pythohn3\python.exe')
print('[+]输入#输出所有环境变量匹配信息')

E=ENVIRONMENT_VARIABLE_UTIL()
while 1:
    d=withexit_input('win env match>')
    if d=='#':
        for k,v in E.getall().items():
            for l in v:
                print(k.center(37),'|',l)
    else:
        for p in E.get_abspath(d):print(p)

