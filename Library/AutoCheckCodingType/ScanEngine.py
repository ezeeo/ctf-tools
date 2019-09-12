import sys
import os

class ScanEngine:
    def __new__(cls, *args, **kwargs):
        if not hasattr(ScanEngine, "_instance"):
            ScanEngine._instance = object.__new__(cls)
        if len(args)!=0:
            ScanEngine._instance.__init(args[0])
        else:
            ScanEngine._instance.__init()
        return ScanEngine._instance

    def __init(self,path='./CheckEngines'):
        if not os.path.exists(path):raise Exception('engine path not exists')
        self.path=path
        #path=os.path.abspath('.')+'\\Library\\createaword'
        if not path in sys.path:#便于import
            sys.path.append(path)
        self.black_list=['    def decode(self):']#禁止在引擎里出现的方法行(此方法不允许重写)

    def __scan_files(self,directory):
        '''扫描全部文件'''
        files=[]
        for file in os.listdir(directory):
            if file[-3:]=='.py' and file[0]!='_':
                files.append(directory+file)
        return files


    def __scan_engine(self):#扫描存在的文件
        '''扫描存在的引擎'''
        files=self.__scan_files(self.path+'/')
        engines=[]
        errors=[]
        for f in files:
            try:
                info=self.__read_engine_info(f)
                engines.append(info)
            except Exception as ex:
                errors.append(ex)
        return engines,errors
            


    def __read_engine_info(self,engine_file_path):
        '''读取检测引擎信息'''
        f=open(engine_file_path,'r',encoding='utf-8')
        Keyword=('name','version','output','describe')
        engine_info={}.fromkeys(Keyword)
        engine_info['import_list']=[]

        for line in f:
            l=line.strip()
            if l=='':continue
            elif l in self.black_list:raise Exception('in '+engine_file_path+'->Do not override this method('+line.strip()+')')
            elif len(l)>6 and 'class ' ==l[:6]:
                if engine_info['name'] not in l:
                    raise Exception('in '+engine_file_path+'->engine name and class name must be same')
                else:
                    break
            elif l[0]=='#':
                tmp=l[1:].split(' ',maxsplit=1)
                if len(tmp)!=2:#其他注释信息
                    continue
                if tmp[0] in Keyword:
                    if not engine_info[tmp[0]]:
                        engine_info[tmp[0]]=tmp[1]
                    elif tmp[0]=='describe':
                        engine_info[tmp[0]]+=tmp[1]
                    else:#重复
                        raise Exception('in '+engine_file_path+' info repeat->'+' '.join(tmp))
                else:continue
            elif len(l)>6 and (l[:4]=='from' or l[:6]=='import'):
                engine_info['import_list'].append(l)
        for line in f:
            if line[:-1] in self.black_list:raise Exception('in '+engine_file_path+'->Do not override this method('+line.strip()+')')
        f.close()
        #检查信息完全性
        for k in engine_info.keys():
            if engine_info[k]==None:raise Exception('in '+engine_file_path+' leak engine info->'+k)
        #设置文件名
        engine_info['file']=engine_file_path.split('/')[-1]
        if ' ' in engine_info['file']:raise Exception('in '+engine_file_path+' file name must not contain spaces')
        #设置扫描路径
        t=engine_file_path.split('/')
        t.pop(-1)
        engine_info['path']='/'.join(t)+'/'
        return engine_info


    def scan(self):
        try:
            self.engine_list,self.error_list=self.__scan_engine()
        except Exception as ex:
            return ex
        return True


if __name__ == "__main__":
    s=ScanEngine()
    s.scan()
    print(s.engine_list)
    print(s.error_list)
