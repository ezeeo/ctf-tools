# ctf-tools  

## 注意
更新会首先在自建服务器上进行更新，github更新可能仅在版本更新时会同步，模块更新时不会同步

## 运行需求
* 0.需要python版本3.4+  
* 1.确保python相关环境变量配置正确  
* 2.确保pip已经安装>10.0  
* 3.建议先运行install_module.py进行自动化所需模块的安装,现在如果缺少主程序所需的模块将会在首次启动自动安装  
* 4.自行添加脚本时将要pip安装的模块在文件开始处用#import xxx标识，参见jsfuckencode.py  
* 5.对于需要引用第三方无法通过pip安装的py脚本的程序，请添加如下代码，参见jsfuckencode.py  
```python
import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/xxx(python class 所在文件夹)'
else:
    path=path+'/Library/xxx(python class 所在文件夹)'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
```
* 6.添加的模块支不支持参数传入均可
* 7.一般参数传入需要处理的字符串,其他设定自行决定
* 8.模块的命名上下划线为保留字,用在同一个模块需要多个名字的时候，例如猪圈密码的命名:pigpencipherdecode_zhujuanmimadecode_猪圈密码解密.py
* 9.建议使用无BOM的utf-8编码
* 10.使用pytools.bat启动时会自动判断是否存在python3环境变量
* 11.output文件夹为公共的文件输出默认文件夹,建议文件输出到这
* 12.自行添加脚本时建议写上版本号#version xxx 参见自带的模块
* 13.如果某模块有需要安装python2包的,请使用
```python
from py_env_util import PY_ENV_CL,PY_PIP_CI
PY_PIP_CI(PY_ENV_CL('lib路径(Library目录下的)(可省略Library)(可为None)',python版本[2|3|'auto']).get_pyenv()).ensure('需要的模块名')
```
* 14.增加了外部源下载部分(extra lib)。有助于减少源服务器压力
* 15.兼容linux


## 使用说明
* 使用‘exit()’退出程序或者模块  
* 直接输入模块名以使用某模块(会进行名称的模糊匹配)  
* 模块的调用支持参数和$传入缓冲区数据,例如 strto $  
* 输入##会进入执行模式(将输入作为代码执行)  
* 以#起始将会被判断为指令  
可用的指令:  
```
#help  
#show modules | version  
#reload  
#lib check  
#lib in(install) | inwc(installwithconfirm) | inwp(installwithupdatepip)  
#inputfile [path] [mode(without_newline,without_space,without_all)]读取文件进入缓冲区  
#$ 输出缓冲区($表示缓冲区),#$=xxx 进行手动赋值，仅识别为字符串  
#search [modules name] 搜索当前名称下能匹配的模块  
#net up(update) [-cover] 不覆盖的更新,带选项为覆盖 | net upmain [-cover](更新主程序) | net uptools [-cover](更新模块)  
#get [module_path]来单独下载某个模块,#update [module/module path] 单独更新某个模块(可自动补全),module path可从./version_list中查看  
```
## 当前模块情况
| 模块路径 | 版本 | 
| ------ | ------ |
|cvestart.py            |                                                                 1.2
|NetworkSpeed.py         |                                                                1.1
|proxy.py                 |                                                               1.8
|wifiMonitor.py            |                                                              1.4
|winenvmatch.py             |                                                             1.1
|builder->b64toimg.py        |                                                            1.0
|builder->hexstreamtofile.py  |                                                           1.0
|builder->read-bpfile.py       |                                                          1.2
|builder->uploadfuzzdicbuilder.py|                                                        1.0
|builder->zlibdecompress.py       |                                                       1.0
|builder->一句话木马_createaword.py|                                                      2.1
|bypasswaf->abusesslbypasswaf_ssl过waf.py |                                               1.0
|bypasswaf->bypasswafbydns.py              |                                              1.0
|coded->ipconvert.py                        |                                             1.2
|coded->Baconcipher->bacondecode_培根解密.py |                                            1.1
|coded->Baconcipher->baconencode_培根加密.py  |                                           1.1
|coded->basexx->base16decode.py                |                                          1.1
|coded->basexx->base16encode.py                 |                                         1.0
|coded->basexx->base32decode.py                  |                                        1.0
|coded->basexx->base32encode.py                   |                                       1.0
|coded->basexx->base64decode.py                    |                                      1.3
|coded->basexx->base64encode.py                     |                                     1.0
|coded->bilibili->av2bv.py                           |                                    1.0
|coded->bilibili->bv2av.py                            |                                   1.0
|coded->binAndstr->bintostr.py                         |                                  1.2
|coded->binAndstr->filetonum.py                         |                                 1.0
|coded->binAndstr->hextostr.py                           |                               1.2
|coded->binAndstr->inttostr.py                             |                              1.2
|coded->binAndstr->strtobin.py                            |                               1.1
|coded->binAndstr->strtohex.py                             |                              1.1
|coded->brainfuck->bftools.py                               |                             1.0
|coded->html->htmlentitydecode_html实体解码.py               |                            1.0
|coded->html->htmlentityencode_html实体编码.py                |                           1.0
|coded->js->aaencode.py                                        |                          1.0
|coded->js->jjdecode.py                                         |                         1.0
|coded->js->jjencode.py                                          |                        1.0
|coded->js->jsfuckencode.py                                       |                       1.0
|coded->perl->ppencode.py                                          |                      1.0
|coded->ruby->rrencode.py                                           |                     0.0
|coded->str->jotherencode.py                                         |                    1.0
|coded->str->Quoted-printable->quotedprintabledecode_可打印字符解码.py|                           1.0
|coded->str->Quoted-printable->quotedprintableencode_可打印字符编码.py |                          1.0
|coded->str->uu->uudecode.py                                            |                 1.0
|coded->str->uu->uuencode.py                                             |                1.0
|coded->str->xx->xxdecode.py                                              |               1.1
|coded->str->xx->xxencode.py                                               |              1.1
|coded->url->urldecode.py                                                   |             1.0
|coded->url->urlencode.py                                                    |            1.0
|connecter->aria2c.py                                                         |           1.0
|connecter->curl.py                                                            |          1.1
|connecter->phpwebshelllinker.py                                                |         1.1
|crypto->fencecipher.py                                                          |        1.1
|crypto->md5.py                                                                   |       1.3
|crypto->pigpencipherdecode_zhujuanmimadecode_猪圈密码解密.py                      |      1.0
|crypto->rot13.py                                                                   |     1.0
|crypto->RC4->rc4decode.py                                                           |    1.0
|crypto->RSA->ctf-rsa-tool.py                                                         |   0.0
|crypto->RSA->read-pem.py                                                              |  1.2
|crypto->RSA->rsadecrypt.py                                                             | 1.0
|crypto->RSA->rsaencrypt.py                                                    |          1.0
|crypto->RSA->RSAfactorN_分解RSA公钥n.py                                        |         1.2
|repair->photo->bmpfix.py                                                        |        1.0
|repair->photo->pngfix.py                                                         |       1.0
|repair->zip->zipfakeencfix.py                                                     |      1.0
|runner->runbf.py                                                                   |     1.0
|runner->runbrainfuck.py                                                              |   1.0
|runner->runhtml.py                                                                  |    1.0
|runner->runjs.py                                                                     |   1.1
|scanner->local->autocheckcodingtype.py                                                |  1.2
|scanner->local->scanfilechange.py                                                |       1.0
|scanner->web->dirsearch.py                                                        |      1.2
|scanner->web->scansrcleak_扫描源码泄露.py                                          |             1.0
|scanner->web->scanweblogic.py                                                       |    1.1
|scanner->web->sqlmap.py                                                              |   1.1
|scanner->web->yun_api->subdomain.py                                                   |  1.2
|suggester->linuxexpsuggester.py                                                   |      0.0
|suggester->linuxsoftexpsuggester.py                                                |     2.0
|suggester->windowsexpsuggester.py                                                   |    1.1
|windows->clipboard.py                                                                |   0.0
