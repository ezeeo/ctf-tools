#扫描环境变量目录，获取可以直接访问目标的绝对路径

import os
import sys
import time
import threading


try:
    from .matcher import Matcher
    from .thread_safe_access_inject import inject_get_set
    from .run_sys_agent import Interactive_system
except ImportError as ex:

    path=os.path.abspath('.')
    if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
        path=path.split('tools',maxsplit=1)[0]+'Library/utils'
    else:
        path=path+'/Library/utils'
    if not path in (p.replace('\\','/') for p in sys.path):
        sys.path.append(path)
        
    from matcher import Matcher
    from thread_safe_access_inject import inject_get_set
    from run_sys_agent import Interactive_system


class BASE_ENVIRONMENT_VARIABLE_UTIL:
    '''生成环境变量里的可直接识别内容和其绝对路径的匹配表,单例模式,默认匹配全部后缀,黑名单支持*和.匹配符,async_index标志是否启用异步索引,启用后无需索引结束即可进行匹配(较慢)，支持了异步的目录扫描,需要自己定义self._env_path和_scan_path方法'''
    __is_init=False
    #单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance


    def __init__(self,allow_suffixs=('*',),dir_black_list=tuple(),async_scan=True,async_index=True):
        if self.__is_init:return

        self._allow_suffixs=['.'+i if i[0]!='.' else i for i in allow_suffixs]
        #self._allow_suffixs=allow_suffixs
        self._dir_black_list=dir_black_list

        #self._env_path=[]

        self._all_files=[]
        self._all_dirs=[]

        self._match_dict={}#带后缀的与绝对路径匹配的字典
        self._bname_dict={}#不带后缀的与带后缀的匹配的字典(仅文件名)
        self._lbname_dict={}#不区分大小写与不带后缀的匹配字典


        self._scan_down=False#标志扫描文件夹是否结束
        self._indexing_down=False#标志索引是否结束,未结束的时候会使用慢速匹配
        self._indexed_name=set()#已索引结束的name

        inject_get_set(self)
        if async_scan:
            S=threading.Thread(target=self._scan_path)
            S.start()
        else:
            self._scan_path()
        if async_index:
            G=threading.Thread(target=self._gen_match_dict)
            G.start()
        else:
            self._gen_match_dict()

        self.__is_init=True



    def _clear_paths(self):
        while '' in self._env_paths:
            self._env_paths.remove('')
        # tmp=[]
        # for p in self._env_paths:
        #     if os.path.exists(p):
        #         tmp.append(p)

        # self._env_paths=list(set(tmp))
        #匹配黑名单
        if len(self._dir_black_list)==0:return
        Ms= [Matcher(b,asterisk_match_len_blacklist=tuple()) for b in self._dir_black_list]
        tmp=[]
        for p in self._env_paths:
            if True not in (M.is_match(p) for M in Ms):
                tmp.append(p)
        self._env_paths=list(set(tmp))



    def _gen_match_dict(self):
        self._indexing_down_set(False)
        #等待scan结束
        while not self._scan_down_get():
            time.sleep(0.1)


        names=set()
        base_names=set()
        lnames=set()
        tmp_all_files=[]
        for p in self._all_files:
            n=os.path.basename(p)
            names.add(n)
            b=os.path.splitext(n)[0]
            base_names.add(b)
            l=b.lower()
            lnames.add(l)
            tmp_all_files.append((p,n,b,l))


        for name in names:
            match_list=[]
            for p in tmp_all_files:
                if name==p[1]:
                    match_list.append(p[0])
            self._match_dict[name]=tuple(set(match_list))
            self._indexed_name.add(name)
            #print('indexed',name)

        for name in base_names:
            match_list=[]
            for n in tmp_all_files:
                if n[2]==name:
                    match_list.append(n[1])
            self._bname_dict[name]=tuple(set(match_list))
            self._indexed_name.add(name)

        for lname in lnames:
            match_list=[]
            for n in tmp_all_files:
                if n[3]==lname:
                    match_list.append(n[2])
            self._lbname_dict[lname]=tuple(set(match_list))
            self._indexed_name.add(lname)

        self._indexing_down_set(True)


    def _fast_get_abspath(self,s):
        '''使用索引的查找'''
        #print('fast')
        if not self._indexing_down_get():
            if s in self._lbname_dict:
                SL=self._lbname_dict[s]
            else:
                SL=[s,]
        else:
            if s.lower() in self._lbname_dict:
                SL=self._lbname_dict[s.lower()]
            else:
                SL=[s,]
        result=[]
        for s in SL:
            if s in self._bname_dict:
                for ss in self._bname_dict[s]:
                    result.extend(self._match_dict[ss])
            elif s in self._match_dict:
                result.extend(self._match_dict[s])
            else:
                continue
                #return tuple()
        return tuple(result)

    def _slow_get_abspath(self,s):
        '''不使用索引的查找'''
        #等待scan结束,scan未结束时无法使用任何功能
        #print('slow')
        while not self._scan_down_get():
            time.sleep(0.1)
        result=[]
        for p in self._all_files:
            tmp=os.path.basename(p)
            if s.lower()==tmp.lower() or s.lower()==os.path.splitext(tmp)[0].lower():
                result.append(p)
        return tuple(set(result))


    def get_abspath(self,s,ex_match=False):
        '''输入环境变量里的可直接识别内容,获取其绝对路径,ex_match表示扩展识别'''
        if ex_match:
            s=os.path.splitext(os.path.basename(s))[0].lower()
        if self._indexing_down_get():
            return self._fast_get_abspath(s)
        elif s in self._indexed_name and not ex_match:
            #print('hint!!!')
            return self._fast_get_abspath(s)
        else:
            return self._slow_get_abspath(s)


    def getall(self):
        result={}
        while not self._indexing_down_get():
            time.sleep(0.0001)
        for s in self._bname_dict.keys():
            result[s]=self.get_abspath(s)
        return result

    def getall_name(self):
        while not self._indexing_down_get():
            time.sleep(0.0001)
        return list(self._bname_dict.keys())





class ENVIRONMENT_VARIABLE_UTIL_WIN(BASE_ENVIRONMENT_VARIABLE_UTIL):
    '''生成环境变量里的可直接识别内容和其绝对路径的匹配表,单例模式,默认只匹配exe后缀,黑名单支持*和.匹配符,async_index标志是否启用异步索引,启用后无需索引结束即可进行匹配(较慢)\n更新支持了异步的目录扫描'''


    def __init__(self, allow_suffixs=('*',), dir_black_list=tuple(), async_scan=True, async_index=True):
        self._env_paths=os.environ['Path'].split(';')
        super().__init__(allow_suffixs=allow_suffixs, dir_black_list=dir_black_list, async_scan=async_scan, async_index=async_index)


    def _scan_path(self):
        self._scan_down_set(False)
        self._clear_paths()
        M=Matcher(asterisk_match_len_blacklist=tuple())
        for p in self._env_paths:
            try:
                ls=os.listdir(p)
            except Exception as ex:
                continue
            for pp in ls:
                abspath=os.path.join(p,pp)
                if os.path.isdir(abspath):
                    self._all_dirs.append(abspath)
                elif os.path.isfile(abspath):
                    for suf in self._allow_suffixs:
                        M.set_substr(suf)
                        if M.is_match(os.path.splitext(pp)[1]):
                            self._all_files.append(abspath)
                    # if os.path.splitext(pp)[1] in self._allow_suffixs:
                    #     self._all_files.append(abspath)
        self._all_dirs=list(set(self._all_dirs))
        self._all_files=list(set(self._all_files))
        self._scan_down_set(True)







class ENVIRONMENT_VARIABLE_UTIL_WSL(BASE_ENVIRONMENT_VARIABLE_UTIL):

    def __init__(self, allow_suffixs=('*'), dir_black_list=tuple(), async_scan=True, async_index=True):
        self._host_bash=Interactive_system('bash')
        self._host_bash.platform='linux'

        self._env_paths=self._get_env_path()

        super().__init__(allow_suffixs=allow_suffixs, dir_black_list=dir_black_list, async_scan=async_scan, async_index=async_index)

    def _get_env_path(self):
        r=self._host_bash.clear(with_enter=True).input_data('set',wait_result=True).getresult()
        p=[]
        for t in (l.split('=')[1].strip()[1:-1].split(':') for l in r.split('\n') if l.startswith('PATH')):
            p.extend(t)
        return list(set(p))


    def _list_dir(self,p):
        dt=self._host_bash.clear(with_enter=True,max_time=1).input_data('ls -lA "'+p+'"',wait_result=True,max_time=2).getresult()
        if not dt.startswith('total'):
            raise FileNotFoundError('no such dir')
        yield 'init'
        for l in dt.strip().split('\n')[1:]:
            if l[0]=='-':
                yield (0,l.split(' ')[-1])
            elif l[0]=='d':
                yield (1,l.split(' ')[-1])

    def _scan_path(self):
        self._scan_down_set(False)
        self._clear_paths()
        M=Matcher(asterisk_match_len_blacklist=tuple())
        for p in self._env_paths:
            try:
                ls=self._list_dir(p)
                assert next(ls)=='init'
            except FileNotFoundError as ex:
                continue
            except Exception as ex:
                print('debug')
                continue
            for pp in ls:
                abspath=os.path.join(p,pp[1]).replace('\\','/')
                if pp[0]==1:
                    self._all_dirs.append(abspath)
                elif pp[0]==0:
                    for suf in self._allow_suffixs:
                        M.set_substr(suf)
                        if '.' not in pp:
                            s=''
                        else:
                            s=pp[1].split('.')[1]
                        if M.is_match(s):
                            self._all_files.append(abspath)
                    # if os.path.splitext(pp)[1] in self._allow_suffixs:
                    #     self._all_files.append(abspath)
        self._all_dirs=list(set(self._all_dirs))
        self._all_files=list(set(self._all_files))
        self._scan_down_set(True)





if __name__ == "__main__":
    #stime=time.time()
    E=ENVIRONMENT_VARIABLE_UTIL_WIN(allow_suffixs=('exe',),dir_black_list=tuple(),async_scan=True,async_index=True)

    #E=ENVIRONMENT_VARIABLE_UTIL_WSL(allow_suffixs=('*',),dir_black_list=('/mnt/*',),async_scan=True,async_index=True)

    #print(int(1000*(time.time()-stime)))
    #E=ENVIRONMENT_VARIABLE_UTIL()
    #E=ENVIRONMENT_VARIABLE_UTIL()
    #E.init()
    #print(E.getall_name())
    
    while True:
        #print(E.get_abspath(input('name:')))
        stime=time.time()
        r=E.get_abspath('python3')
        t=int(1000*(time.time()-stime))
        print(r)
        if t<10:
            print('')
        print(t,'ms')
        #time.sleep(0.001)
        time.sleep(1)
    print()
