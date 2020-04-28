#encoding:utf-8
#version 1.0
import sys
import os
if sys.platform=='linux':
    import readline
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from py_env_util import PY_ENV_CL

pyenv=PY_ENV_CL(None,3).get_pyenv()


#base='G:\\python\\tool_manager'
base='.'
clistart = base+'/Library/scansrcleak/boom_framework/clistart.py'
request_path = base+'/Library/scansrcleak/boom_framework/request'
template_file=base+'/Library/scansrcleak/boom_framework/generator/template.txt'


def check_env():
    if not os.path.exists(clistart) or not os.path.exists(request_path) or not os.path.exists(template_file):
        print('[!]loss file, must have boom_framework in Library')
        exit()

def check_type(instr):
    if os.path.exists(instr):
        return 'file'
    else:
        return 'url'

def get_file_uri(file_path):
    '''
    从文件读取baseuri
    '''
    if not os.path.exists(file_path):
        print('\n[!]get uri fail ,file not exists')
        return False
    f=open(file_path,'r',encoding='gbk')
    line=f.readline()
    f.close()
    line=line.strip().split(' ')
    #检查格式
    if len(line)!=3:
        print("\n[!]file first line format error")
        return False
    if line[2]!='HTTP/1.1':#检查请求版本
        print('\n[!]Unsupported requests in line 1:must HTTP/1.1, but now is {}'.format(line[2]))
        return False
    #第一行验证通过
    name=line[1].split('/')[-1].split('?')[0].strip()#用于生成补全模板的uri
    print('success')
    return name


def get_input_uri(url):
    '''
    从输入读取baseuri
    '''
    if url[:4]=='http':
        url=url.split('//',maxsplit=1)[1]
    if len(url.split('/'))==1:
        return ''
    else:
        return url.split('/')[-1].split('?')[0].strip()

def get_base_uri(instr):
    if os.path.exists(instr):
        print('[+]File input detected')
        print('[+]try get base_uri...',end='')
        base_uri=get_file_uri(instr)
    else:
        print('[+]url input detected')
        print('[+]try get base_uri...',end='')
        base_uri=get_input_uri(instr)
    if base_uri==False:
        exit()

    if base_uri=='':
        print('\n[-]not detected base_uri...')
        print('[!]input web Language type or enter use default php')
        server_language_dict={'php':['php','php','php3','php4','php5','pht','phtml'],
        'asp':['asp','aspx'],
        'html':['htm','html'],
        'jsp':['jsp','htm']}
        Ltype=input('Language type(php,asp,html,jsp):')
        if Ltype=='exit()':exit()
        if Ltype in server_language_dict.keys():
            Ltype=server_language_dict[Ltype]
        else:
            Ltype=server_language_dict['php']
        Ltype=['index.'+i for i in Ltype]
        return Ltype
    else:
        print('success')
        Ltype=[]
        Ltype.append(base_uri)
        return Ltype

def gen_dict(base_uri):
    '''
    生成遍历字典
    '''
    print('[+]start gen dict...',end='')
    global template_file
    t=open(template_file,'r',encoding='gbk')
    f=open(template_file[:-8],'w',encoding='utf-8')
    for templ in t:
        if '§§' in templ:
            for b_uri in base_uri:
                f.write(templ.replace('§§',b_uri))
        else:
            f.write(templ)
    t.close()
    f.close()
    print('success')

def gen_request(instr):
    '''
    生成请求函数
    '''
    txt='''def index(requri):
    import warnings
    warnings.filterwarnings("ignore")
    a='{}'
    #print(a+requri)
    r=requests.get(a+requri,allow_redirects=False,verify=False)
    return r
    '''
    print('[+]start gen request...',end='')
    if os.path.exists(instr):
        s=open(instr,'r',encoding='gbk')
        t=open(request_path+'/temp.txt','w',encoding='gbk')
        data=s.read().split('\n')
        s.close()
        data[0]=data[0].split(' ')[0]+' /§§ '+data[0].split(' ')[2]
        data='\n'.join(data)
        t.write(data)
        t.close()
    else:
        instr=instr.split('//')
        if len(instr)==2:
            instr=instr[0]+'//'+instr[1].split('/')[0]+'/'
        elif len(instr)==1:
            instr='http://'+instr[0].split('/')[0]+'/'
        else:
            print('\n[!]url format error')
        txt=txt.format(instr)
        f=open(request_path+'/temp.py','w',encoding='utf-8')
        f.write(txt)
        f.close()
    print('success')

if __name__ == "__main__":
    print('scan src leak --- by yun')
    print('   ---use boom framework')
    check_env()
    instr=input('input url or file path:')
    if instr=='exit()':
        exit()
    gen_request(instr)
    gen_dict(get_base_uri(instr))
    if check_type(instr)=='url':
        arg=' u='+instr
    else:
        arg=' l=temp.txt'
    os.system(pyenv+' '+clistart+arg)
