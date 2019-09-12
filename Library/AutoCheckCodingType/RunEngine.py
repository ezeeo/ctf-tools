#encoding=utf-8
import os
from LoadEngine import Loader

class Runner():
    def __init__(self,engine_info,immediately_initeng=False):
        if not isinstance(engine_info,dict) or len(engine_info)!=7:raise Exception('engine info format error->'+str(engine_info))
        self.einfo=engine_info
        self.data=''
        self.result=None
        self.__engine=None
        self.__loader=Loader(self.einfo)
        if immediately_initeng:
            self.__get_engine()

    #设置需要判别的数据
    def setdata(self,data):
        if not isinstance(data,str):return False
        try:
            if not self.__engine:self.__get_engine()
            self.data=data
            self.__engine.set_data(self.data)
        except Exception as ex:
            return 'set data error->'+self.einfo['file']+'->'+self.einfo['name']+'->'+str(ex)
        return True


    #获取引擎
    def __get_engine(self):
        if not self.__engine:
            try:
                self.__engine=self.__loader.LoadEngine()
            except Exception as ex:
                raise Exception('get engine error->'+self.einfo['file']+'->'+self.einfo['name']+'->'+str(ex))
            

    #运行check
    def __run_check(self):
        if not self.__engine:
            self.__get_engine()
        try:
            result=self.__engine.check()
            return result
        except Exception as ex:
            raise Exception('run engine error->'+self.einfo['file']+'->'+self.einfo['name']+'->'+str(ex))
        
    #读取结果文件
    def __read_result_file(self,file_path):
        if file_path[:2]=='./' or file_path[:2]=='.\\':
            file_path=file_path[2:]
        if not os.path.exists(self.einfo['path']+file_path):
            raise Exception('result file not exists->'+self.einfo['file']+'->'+self.einfo['name']+'->'+self.einfo['path']+file_path)
        possible=False
        desp=[]
        result=[]
        f=open(self.einfo['path']+file_path,'r',encoding='utf-8')
        first=f.readline().strip()
        if first=='True':
            possible=True
        elif first=='False':
            pass
        else:
            try:
                possible=float(first)
            except :
                possible='Format warnings'
        if isinstance(possible,str):#非规范格式
            result.append(first)
            for line in f:
                result.append(line.strip())
           
        else:#规范格式读取
            for line in f:
                if line.strip()=='':continue
                if line[0]=='#':
                    desp.append(line.strip())
                else:
                    result.append(line.strip())
        f.close()

        return (possible,'\n'.join(desp),'\n'.join(result))

    #设置运行结果
    def __set_result(self,tmp_result):
        if self.einfo['output']=='normal':
            #print(tmp_result)
            self.result=tmp_result
        elif self.einfo['output']=='file':
            self.result=self.__read_result_file(tmp_result)
        elif self.einfo['output']=='console':
            self.result=None

    def run(self):
        if not self.data:return False
        try:
            tmp_result=self.__run_check()
            self.__set_result(tmp_result)
            return True
        except Exception as ex:
            return str(ex)