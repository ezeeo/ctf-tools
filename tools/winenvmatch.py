#coding=utf-8
#version 1.0

import os,sys
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

E=ENVIRONMENT_VARIABLE_UTIL()
while 1:
    for p in E.get_abspath(withexit_input('win env match>')):print(p)

