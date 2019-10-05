#扫描py文件,根据匹配规则获取其中的函数以及调用方式

#鸡贼的获取变量名的字符串https://www.zhihu.com/question/42768955#
# import re
# import traceback

# pattren = re.compile(r'[\W+\w+]*?get_variable_name\((\w+)\)')
# __get_variable_name__ = []
# def get_variable_name(x):
#     global __get_variable_name__
#     if not __get_variable_name__:
#         __get_variable_name__ = pattren.findall(traceback.extract_stack(limit=2)[0][3])
#     return __get_variable_name__.pop(0)
#鸡贼的获取变量名的字符串#

import os,sys

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)


from matcher import Matcher
class pyfunc_scanner:
    def __init__(self,file_path):
        from init_arg_checker import check_init_arg

        self._file_path=file_path

        if not check_init_arg(self):
            raise Exception('[!]error:参数检测不通过')
        self._readfile()


    def _check_file_path(self,_file_path):
        if os.path.exists(_file_path) and os.path.isfile(_file_path):return True
        return False


    
    def _readfile(self):
        with open(self._file_path,'r',encoding='utf-8') as f:
            self._file_data=f.read()
        self._file_data_line=self._file_data.split('\n')

    def _basic_match_scan(self,pattren,allow_space):
        '''获取满足匹配的行号'''
        R=[]
        M=Matcher(substr=pattren,asterisk_match_len_blacklist=tuple())
        for i,l in enumerate(self._file_data_line):
            t=l
            if allow_space:
                t=l.strip()
            #匹配
            if M.is_match(t):
                #加入结果(行号)
                R.append(i)
        return R

    def _get_func_name(self,s):
        '''从一行获取函数名'''
        s=s.strip()
        s=s.split(' ')
        s=[i.strip() for i in s]
        while '' in s:
            s.remove('')
        if 'def' in s:
            s.remove('def')
        s=''.join(s)
        s=s.split('(')[0]
        return s

    def _get_func_args(self,s):
        '''从一行获取函数参数'''
        args=[i.strip() for i in s.split('(')[1].split(')')[0].strip().split(',')]
        while '' in args:
            args.remove('')
        return tuple(a.split('=')[0] for a in args)



    def _get_func_info(self,s0,s1,s2):
        '''从当前一行和下一行获取注释'''
        info=''
        if '#' in s0:
            info+=s0.split('#',maxsplit=1)[1]
        if '#' in s1:
            info+=s1.split('#',maxsplit=1)[1]
        if '#' in s2:
            info+=s2.split('#',maxsplit=1)[1]
        if s2.count("'''")==2:
            info+=s2.strip().replace("'''",'').strip()
        if s2.strip().startswith('print(') and s2.strip().endswith(')'):
            t=s2.strip()[6:-1]
            if (t[0]=='"' or t[0]=="'") and (t[-1]=='"' or t[-1]=="'"):
                t=t[1:-1]
            info+=t
        

        return info


    def _ana_func(self,flist):
        R=[]
        for i in flist:
            if i<=0:t0=''
            else:t0=self._file_data_line[i-1]
            t1=self._file_data_line[i]
            if i+1>=len(self._file_data_line):t2=''
            else:t2=self._file_data_line[i+1]
            R.append((self._get_func_name(t1),self._get_func_args(t1),self._get_func_info(t0,t1,t2)))
        return R



    def scan_func(self,pattren,allow_space):
        R=self._basic_match_scan(pattren,allow_space)
        R=self._ana_func(R)
        return R

class pyfunc_loader:
    def __init__(self,file_path,func_list):
        from init_arg_checker import check_init_arg

        self._file_path=file_path
        self._func_list=func_list

        if not check_init_arg(self):
            raise Exception('[!]error:参数检测不通过')
        
        

    def _check_file_path(self,_file_path):
        if os.path.exists(_file_path) and os.path.isfile(_file_path):
            self._file_name=os.path.split(self._file_path)[1]
            self._file_path=os.path.split(self._file_path)[0]
            return True
        return False


    def _check_func_list(self,_func_list):
        if not isinstance(_func_list,list):return False
        for i in _func_list:
            if not isinstance(i,tuple):return False
            if len(i)!=3:return False
        return True

    def load(self):

        if not self._file_path in sys.path:
            sys.path.append(self._file_path)
        R=[]
        for f in self._func_list:
            exec('from '+self._file_name[:-3]+' import '+f[0])
            func=eval(f[0])
            R.append((f[0],f[1],f[2],func))
        return R

class pyfunc_runner:
    def __init__(self,file_path,func_list):
        from init_arg_checker import check_init_arg

        self._file_path=file_path
        self._func_list=func_list

        if not check_init_arg(self):
            raise Exception('[!]error:参数检测不通过')

    def _check_file_path(self,_file_path):
        if os.path.exists(_file_path) and os.path.isfile(_file_path):
            self._file_name=os.path.split(self._file_path)[1]
            self._file_path=os.path.split(self._file_path)[0]
            return True
        return False


    def _check_func_list(self,_func_list):
        if not isinstance(_func_list,list):return False
        for i in _func_list:
            if not isinstance(i,tuple):return False
            if len(i)!=4:return False
        return True

    def _find_func(self,funcname):
        func=None
        for f in self._func_list:
            if funcname==f[0]:
                func=f
                break
        if func==None:
            raise Exception('无此函数')
        return func

    def _get_run_arg(self,funcname,kargs):
        func=self._find_func(funcname)
        args=[]
        for a in func[1]:
            if a in kargs.keys():
                if isinstance(kargs[a],str):
                    args.append(a+"='"+kargs[a]+"'")
                else:
                    args.append(a+"="+str(kargs[a]))
        if len(args)!=len(func[1]):
            return (False,args)
        else:return (True,args)
        
    def _completion_input(self,funcname,args):
        func=self._find_func(funcname)
        for k in func[1]:
            if k not in [a.split('=',maxsplit=1)[0] for a in args]:
                #需要输入
                c=input('输入缺少的参数->'+k+':')
                if c.isdigit():
                    args.append(k+"="+c)
                else:
                    args.append(k+"='"+c+"'")
        return args



    def run(self,funcname,completion_input=True,**kargs):
        r=self._get_run_arg(funcname,kargs)
        if r[0]==True:
            r=r[1]
        elif completion_input:
            r=self._completion_input(funcname,r[1])
        else:
            raise Exception('参数不匹配'+tuple(r[1])+'!='+kargs.keys())
        #运行
        func=self._find_func(funcname)
        return eval("func[3]("+','.join(r)+")")



class pyfunc_util:
    def __init__(self,file_path,pattren):
        self._S=pyfunc_scanner(file_path)
        self._Funcs3=self._S.scan_func(pattren,False)
        self._L=pyfunc_loader(file_path,self._Funcs3)
        self._Funcs4=self._L.load()
        self._R=pyfunc_runner(file_path,self._Funcs4)

    def run(self,funcname,completion_input=True,**kargs):
        return self._R.run(funcname,completion_input,**kargs)

    def get_func(self,funcname):
        return self._R._find_func(funcname)

    def get_funclist(self):
        return self._Funcs3

if __name__ == "__main__":
    #S=pyfunc_scanner('D:\\ctf-tool\\Library\\createaword\\jspcreater.py')
    #S.scan_func('def jsp_*(*)*:',False)
    p='..\\createaword\\phpcreater.py'
    # S=pyfunc_scanner(p)
    # s=S.scan_func('def php_*(*)*:',False)

    # L=pyfunc_loader(p,s)
    # F=L.load()
    # #for f in F:
    # #    print(f)

    # R=pyfunc_runner(p,F)
    # print(R.run('php_guogou',pwd='c'))
    p=pyfunc_util(p,'def php_*(*)*:')
    print(p.run('php_muti_base64',pwd='cccccccc',num=4))