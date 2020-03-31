import sys
import os
import configparser
import subprocess
import json


try:
    from matcher import Matcher
    from pbar import Pbar
except Exception as identifier:
    path=os.path.dirname( __file__)
    if not path in (p.replace('\\','/') for p in sys.path):
        sys.path.append(path)
    from matcher import Matcher
    from pbar import Pbar



class PY_ENV_CL:
    '''checker and loader'''
    def __init__(self,lib_path,ver='auto'):
        if ver not in (2,3,'auto'):
            raise Exception('版本错误')
        self._py_ver=ver
        if lib_path!=None:
            self._lib_path=lib_path
            if os.path.exists(self._lib_path) and os.path.isfile(self._lib_path):
                self._mode='file'
            else:
                self._mode='dir'
                ex=[False,False]
                ex[0]=self._check_path_exists()
                self._standard_path()
                ex[1]=self._check_path_exists()
                if sum(ex)==2:
                    pass
                elif sum(ex)==0:
                    raise Exception('路径不存在')
                elif ex[0]==True and ex[1]==False:
                    #raise Exception('debug')
                    self._lib_path=lib_path
                self._clean_to_dir()
            if not self._check_path_exists():raise Exception('debug')
        self._check_py_ver()
        self._conf_path=os.path.dirname( __file__)+'/env_conf.ini'
        #self._conf_path='D:/ctf-tool/Library/utils/env_conf.ini'
        self._config=self._read_default_conf()
        self._check_conf()



    def get_pyenv(self):
        e=self._config.get("python", "python{}_path".format(self._py_ver)).strip()
        if ' ' in e:
            return '"'+e+'"'
        else:
            return e

    def get_pyver(self):
        return self._py_ver


    def _read_default_conf(self):
        '''读取'''
        config = configparser.ConfigParser()
        if not self._check_conf_exists():
            if not config.has_section("python"):  # 检查是否存在section
                config.add_section("python")
        else:
            config.read(self._conf_path,encoding="utf-8")
            if not config.has_section("python"):  # 检查是否存在section
                config.add_section("python")
        return config

    def _write_conf(self):
        self._config.write(open(self._conf_path, "w",encoding='utf-8'))



    def _user_input_config(self):
        path=input('[!]输入python{}路径:'.format(self._py_ver))
        if self._check_input_path(path):
            return path
        else:
            yn=input('[!]警告:检测到路径不可用，是否继续?(y/n)').strip().lower()
            if yn=='y':
                return path
            else:
                exit(1)

            

    def _check_conf(self):
        '''检查配置文件正确性，不正确则用户输入'''
        if not self._config.has_option("python", "python{}_path".format(self._py_ver)):
            self._config.set("python", "python{}_path".format(self._py_ver),self._user_input_config())
        else:
            path=self._config.get("python", "python{}_path".format(self._py_ver))
            if not self._check_input_path(path,'读入'):
                print('[!]警告:读入的配置文件存在异常，路径不可用')
                self._config.set("python", "python{}_path".format(self._py_ver),self._user_input_config())
        self._write_conf()



    def _check_input_path(self,path,mode='输入'):
        '''检查输入的python路径是否正常'''
        #检查环境变量
        for p in os.environ['Path'].split(';'):
            if 'python{}'.format(self._py_ver) in p or 'Python{}'.format(self._py_ver) in p:
                return True
        #检查可执行性
        p = subprocess.Popen([path,'--version'], shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data=[]
        while True:
            d=p.stdout.readline()
            if not d:
                break
            data.append(d)
        
        p.stdout.close()
        p.wait()
        #os.waitpid(p.pid, 0)
        if b'\n'.join(data).startswith('Python {}'.format(self._py_ver).encode('utf-8')):
            return True
        #检查文件
        abs_path=os.path.abspath(path)
        if os.path.exists(path) or os.path.exists(abs_path):
            if os.path.isfile(path) or os.path.isfile(abs_path):
                pass
            else:
                print('[!]警告:检测到输入的是目录')
                if abs_path[-1] not in ('/','\\'):abs_path+='/'
                if os.path.exists(abs_path+'python.exe'):pass
                else:
                    print('[!]错误:未检测到目录下的python.exe')
                    return False
            return True
        else:
            
            return False


    def _clean_to_dir(self):
        '''path转成目录'''
        if not os.path.isdir(self._lib_path):
            if '/' in self._lib_path or sys.platform=='linux':
                index=self._lib_path.rfind('/')
            else:
                index=self._lib_path.rfind('\\')
            if index==-1:
                self._lib_path='./'
            else:
                self._lib_path=self._lib_path[:index]


    def _detect_py_ver(self,filename):
        '''判断一个文件是py2还剩py3'''
        if not os.path.exists(filename):
            raise Exception('文件不存在')
        with open(filename,'r',encoding='utf-8') as f:
            data=f.read()

        if 'print "' in data or "print '" in data or 'exec ' in data or 'xrange' in data or 'raw_input' in data:
            return 2
        elif 'print(' in data or 'print (' in data or 'exec(' in data:
            return 3
        else:
            M=Matcher('*except *,*:*',tuple())
            if True in (M.is_match(l) for l in data.split('\n')):
                return 2
            M.set_substr('*except * as *:*')
            if True in (M.is_match(l) for l in data.split('\n')):
                return 3
            return False


    def  _check_py_ver(self):
        '''判断所用lib版本'''
        if self._py_ver=='auto':
            file_list=self._scan_py()
            for file_path in file_list:
                r=self._detect_py_ver(file_path)
                if r==False:
                    continue
                self._py_ver=r
                return
            #获取版本失败,用户输入
            self._user_input_pyver()
                

    def _user_input_pyver(self):
        while 1:
            v=input('[!]请输入lib所用的python版本(2/3):').strip()
            if v in ('2','3'):
                break
            else:
                print('[!]只能输入(2/3)')
        self._py_ver=int(v)

    def _scan_files(self,directory,prefix=None,postfix=None):
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


    def _scan_py(self):
        '''扫描存在的文件'''
        if self._mode=='dir':
            return self._scan_files(self._lib_path,postfix=".py")
        else:
            return [self._lib_path]


    def _check_conf_exists(self):
        '''配置文件存在于utils里，统一管理'''
        
        return os.path.exists(self._conf_path)



    def _check_path_exists(self):
        '''检查lib目录是否存在'''
        return os.path.exists(self._lib_path)


    def _standard_path(self):
        '''全部变成相对路径'''
        def process_subpath(p):
            if p[:2] in ('.\\','./'):
                p=p[2:]
            elif p[0] in ('\\','/'):
                p=p[1:]
            if '/' in p or sys.platform=='linux':
                p='./Library/'+p
            else:
                p='.\\Library\\'+p
            return p


        if len(self._lib_path)<10:#可能是部分路径(即只有Library之后的部分)
            self._lib_path=process_subpath(self._lib_path)
        elif self._lib_path[:10] in ('.\\Library\\','./Library/'):#标准的相对路径
            pass
        elif 'Library' in self._lib_path:#可能是绝对路径
            self._lib_path=self._lib_path.split('Library',maxsplit=1)[1]
            if '/' in self._lib_path or sys.platform=='linux':
                self._lib_path='./Library'+self._lib_path
            else:
                self._lib_path='.\\Library'+self._lib_path
        else:#部分路径
            self._lib_path=process_subpath(self._lib_path)


class PY_PIP_CI:
    '''checker and installer'''
    def __init__(self,pyenv):
        self._pyenv=pyenv
        self._pip_list=self._get_py_piplist()
        #self._bat_path='D:/ctf-tool/Library/utils/tmp.bat'


    def ensure(self,pipname):
        '''保证指定的pip已经安装,字符串或列表'''
        if isinstance(pipname,str):
            if pipname not in self._pip_list:
                fd=self._install(pipname)
                if fd==False:
                    print('[!]错误:pip软件包'+pipname+'安装失败')
                    exit(1)
        elif isinstance(pipname,tuple) or isinstance(pipname,list):
            #开进度条
            bar=Pbar(show_percent_num=False,smooth=True,allow_skip_frame=False,vsync=True)
            pnum=len(pipname)+1
            for i,p in enumerate(pipname):
                bar.set_rate(int(i+1//pnum*100),'check '+p+'...')
                if p not in self._pip_list:
                    fd=self._install(p)
                    if fd==False:
                        bar.print('[!]错误:pip软件包'+pipname+'安装失败')
                        bar.clear(True)
                        exit(1)
            bar.set_rate(100,'all done')
            bar.clear(True)
        else:
            print('[!]错误:不支持的参数类型')
            exit(1)


    def _install(self,pipname):
        fd=os.system('set PYTHONIOENCODING=UTF-8 &&' + self._pyenv+' -m pip install '+pipname)
        if fd!=0:
            return False
        return True



    def _get_py_piplist(self):
        '''获取当前python环境的pip列表'''
        #self._create_bat()
        #s=subprocess.Popen(['cmd','/C',".\\Library\\utils\\tmp.bat"],bufsize=0,stdout=subprocess.PIPE,universal_newlines=True)
        s=subprocess.Popen(['cmd','/C',"set PYTHONIOENCODING=UTF-8&&{} {}/get_py_pip_list.py".format(self._pyenv,os.path.dirname( __file__))],bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE,universal_newlines=True)
        result=''
        while True:
            nextline=s.stdout.readline().strip()
            result+=nextline
            if nextline=="" and s.poll()!=None:
                break
        result=result.split('|')[1]
        #print(result)
        j=json.loads(result.strip())
        #self._clean_bat()
        return j


    def _create_bat(self):
        bat='''chcp 65001
set PYTHONIOENCODING=UTF-8
{} ./Library/utils/get_py_pip_list.py'''.format(self._pyenv)
        with open('./Library/utils/tmp.bat','w',encoding='utf-8') as f:
            f.write(bat)


    def _clean_bat(self):
        if os.path.exists('./Library/utils/tmp.bat'):
            os.remove('./Library/utils/tmp.bat')


if __name__ == "__main__":
    piplist=PY_PIP_CI('c:/Python27/python.exe')
    print(piplist._pip_list)
    #print(PY_ENV_CL(None,3).get_pyenv())
    #print(PY_ENV_CL(None,2).get_pyenv())
