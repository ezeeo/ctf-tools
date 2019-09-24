0.需要python版本3.4+
1.确保python相关环境变量配置正确
2.确保pip已经安装
3.建议先运行install_module.py进行自动化所需模块的安装,现在如果缺少主程序所需的模块将会在首次启动自动安装
4.自行添加脚本时将要pip安装的模块在文件开始处用#import xxx标识，参见jsfuckencode.py
5.对于需要引用第三方无法通过pip安装的py脚本的程序，请添加如下代码，参见jsfuckencode.py

import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library\\xxx(python class 所在文件夹)'
else:
    path=path+'\\Library\\xxx(python class 所在文件夹)'
if not path in sys.path:
    sys.path.append(path)

6.添加的模块支不支持参数传入均可
7.一般参数传入需要处理的字符串,其他设定自行决定
8.模块的命名上下划线为保留字,用在同一个模块需要多个名字的时候，例如猪圈密码的命名:pigpencipherdecode_zhujuanmimadecode_猪圈密码解密.py
9.建议使用无BOM的utf-8编码
10.使用pytools.bat启动时会自动判断是否存在python3环境变量
11.output文件夹为公共的文件输出默认文件夹,建议文件输出到这
12.自行添加脚本时建议写上版本号#version xxx 参见自带的模块
13.如果某模块有需要安装python2包的,请使用
from py_env_util import PY_ENV_CL,PY_PIP_CI
PY_PIP_CI(PY_ENV_CL('lib路径(Library目录下的)(可省略Library)',python版本(2/3/auto).get_pyenv()).ensure('需要的模块名')
14.增加了外部源下载部分(extra lib)。有助于减少源服务器压力