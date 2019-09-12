import sys

class Loader():
    def __init__(self,engine_info,Preemptive=False):
        if not isinstance(engine_info,dict) or len(engine_info)!=7:raise Exception('engine info format error->'+str(engine_info))
        self.einfo=engine_info
        self.preemptive=Preemptive#抢占式加载,会取消加载之前的同名引擎,默认否
        self.__engine=None

    def __get_engine(self):
        #for i in self.einfo['import_list']:
            #exec(i)
        exec("from "+self.einfo['file'][:-3]+" import "+self.einfo['name'])
        self.__engine=eval(self.einfo['name']+'()')
        #from testeng import TestEngine

    def __is_import(self):
        if self.einfo['name'] in sys.modules.keys():
            return True
        return False

    def __unimport(self):
        del sys.modules[self.einfo['name']]

    def LoadEngine(self):
        try:
            if self.__is_import():
                if self.preemptive:
                    self.__unimport()
                else:
                    raise Exception('Existence of engine with the same name and  load_mode is not preemptive')
            self.__get_engine()
            return self.__engine
        except Exception as ex:
            raise Exception('load engine error->'+str(self.einfo)+'->'+str(ex))