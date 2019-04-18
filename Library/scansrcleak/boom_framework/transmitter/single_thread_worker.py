import requests
import string
from queue import Queue

import threading


class transmitter():
    '''
    单线程发http测试
    '''
    def __init__(self,req_func,gen_func,resultanalyzer_func=None,obf_func=None):
        '''
        传入转换后的请求函数,pyaload生成器,[结果分析函数和混淆函数]
        都是complie后的code class,均为元组(第一个值为函数名,第二个为函数)
        '''
        self.request_func=req_func
        self.generator_func=gen_func
        self.result_analyzer_func=resultanalyzer_func
        self.obfuscator_func=obf_func
        assert isinstance(self.request_func,tuple)
        assert isinstance(self.generator_func,tuple)
        if self.result_analyzer_func:assert isinstance(self.result_analyzer_func,tuple)
        if self.obfuscator_func:assert isinstance(self.obfuscator_func,tuple)
        self.result=Queue()
        
    def run(self):
        exec(self.request_func[1])
        exec(self.generator_func[1])
        if self.result_analyzer_func:exec(self.result_analyzer_func[1])
        if self.obfuscator_func:exec(self.obfuscator_func[1])
        #运行
        #统计参数个数
        var_count=self.request_func[0].count('{}')
        #去掉多余的{}
        if var_count>1:
            self.request_func=(self.request_func[0].replace(','.join(['{}' for i in range(var_count)]),'{}'),self.request_func[1])

        var_list=[i for i in string.ascii_lowercase][:var_count]
        ge=eval(self.generator_func[0])#得到payload生成器
        pay=ge.send(None)
        while True:
            if pay==None:
                try:
                    pay=ge.send(None)
                except StopIteration as ex:
                    break
                continue
            
            if len(pay)!=len(var_list):raise Exception('generator not match request in Variable number')
            #混淆,以序列形式传入混淆器
            if self.obfuscator_func:
                payl=eval(self.obfuscator_func[0].format('pay'))
            else:
                payl=pay
            exec('('+','.join(var_list)+',)=payl')#解包
            #形成请求调用语句

            func=self.request_func[0].format(','.join(var_list))
            r=''
            try:
                r=eval(func)#执行函数
            except Exception as ex:
                r=str(ex)
            finally:
                #print('[+]get '+str(r))
                self.result.put((func,r))
            #传入结果分析器
            if self.result_analyzer_func:
                eval(self.result_analyzer_func[0].format('payl,r'))
            
            pay=ge.send(r)#回调生成器,用来控制下次生成的数据
            if pay==None:
                try:
                    pay=ge.send(r)
                except StopIteration as ex:
                    break
                

        return self.result


def get_transmitter(req_func,gen_func,resultanalyzer_func,obf_func):#必须要一个这个名称的函数,并且返回的对象具有run方法
    trans=transmitter(req_func,gen_func,resultanalyzer_func,obf_func)
    return trans