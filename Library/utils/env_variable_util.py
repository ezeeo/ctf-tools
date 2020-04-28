#扫描环境变量目录，获取可以直接访问目标的绝对路径

import os
import sys
import time
import threading

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from matcher import Matcher
from thread_safe_access_inject import inject_get_set

class ENVIRONMENT_VARIABLE_UTIL:
    '''生成环境变量里的可直接识别内容和其绝对路径的匹配表,单例模式,默认只匹配exe后缀,async_index标志是否启用异步索引,启用后无需索引结束即可进行匹配(较慢)'''
    __is_init=False
    #单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance


    def __init__(self,allow_suffixs=('exe',),dir_black_list=('C:\\WINDOWS*',),async_index=True):
        if self.__is_init:return

        self._allow_suffixs=['.'+i if i[0]!='.' else i for i in allow_suffixs]
        self._dir_black_list=dir_black_list

        self._paths=os.environ['Path'].split(';')
        self._all_files=[]
        self._all_dirs=[]

        self._match_dict={}#带后缀的与绝对路径匹配的字典
        self._bname_dict={}#不带后缀的与带后缀的匹配的字典(仅文件名)

        
        self._scan_path()
        

        self._indexing_down=False#标志索引是否结束,未结束的时候会使用慢速匹配
        inject_get_set(self)

        if async_index:
            T=threading.Thread(target=self._gen_match_dict)
            T.start()
        else:
            self._gen_match_dict()

        self.__is_init=True



    def _clear_paths(self):
        while '' in self._paths:
            self._paths.remove('')
        tmp=[]
        for p in self._paths:
            if os.path.exists(p):
                tmp.append(p)

        self._paths=list(set(tmp))
        #匹配黑名单
        if len(self._dir_black_list)==0:return
        Ms= [Matcher(b,asterisk_match_len_blacklist=tuple()) for b in self._dir_black_list]
        tmp=[]
        for p in self._paths:
            if True not in (M.is_match(p) for M in Ms):
                tmp.append(p)
        self._paths=list(set(tmp))



    def _scan_path(self):
        self._clear_paths()
        for p in self._paths:
            for pp in os.listdir(p):
                abspath=os.path.join(p,pp)
                if os.path.isdir(abspath):
                    self._all_dirs.append(abspath)
                elif os.path.isfile(abspath):
                    if os.path.splitext(pp)[1] in self._allow_suffixs:
                        self._all_files.append(abspath)
        self._all_dirs=list(set(self._all_dirs))
        self._all_files=list(set(self._all_files))

    def _gen_match_dict(self):
        self._indexing_down_set(False)
        #stime=time.time()

        names=set()
        for p in self._all_files:
            names.add(os.path.basename(p))
        
        #print('time:',int((time.time()-stime)*1000),'ms')
        #stime=time.time()

        for name in names:
            match_list=[]
            for p in self._all_files:
                if name==os.path.basename(p):
                    match_list.append(p)
            self._match_dict[name]=tuple(match_list)

        #print('time:',int((time.time()-stime)*1000),'ms')
        #stime=time.time()

        base_names=set()
        for name in names:
            base_names.add(os.path.splitext(name)[0])
        for name in base_names:
            match_list=[]
            for n in names:
                if os.path.splitext(n)[0]==name:
                    match_list.append(n)
            self._bname_dict[name]=tuple(match_list)

        #print('time:',int((time.time()-stime)*1000),'ms')
        self._indexing_down_set(True)

    def _fast_get_abspath(self,s):
        '''使用索引的查找'''
        if s in self._bname_dict.keys():
            result=[]
            for ss in self._bname_dict[s]:
                result.extend(self._match_dict[ss])
            return tuple(result)
        elif s in self._match_dict.keys():
            return self._match_dict[s]
        else:
            return tuple()

    def _slow_get_abspath(self,s):
        '''不使用索引的查找'''
        result=[]
        for p in self._all_files:
            tmp=os.path.basename(p)
            if s==tmp or s==os.path.splitext(tmp)[0]:
                result.append(p)
        return tuple(set(result))


    def get_abspath(self,s):
        '''输入环境变量里的可直接识别内容,获取其绝对路径'''
        if self._indexing_down_get():
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

if __name__ == "__main__":
    E=ENVIRONMENT_VARIABLE_UTIL(show_bar=False)
    E=ENVIRONMENT_VARIABLE_UTIL()
    E=ENVIRONMENT_VARIABLE_UTIL()
    #E.init()
    while True:
        print(E.get_abspath(input('name:')))
    print()
