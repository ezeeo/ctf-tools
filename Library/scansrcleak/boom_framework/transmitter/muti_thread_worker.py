import requests
import string
from queue import Queue
import threading
from concurrent.futures import ThreadPoolExecutor
import time


class transmitter_thread():
    '''
    多线程发http,无反馈,不能生成器不能获得请求的结果
    '''
    def __init__(self,req_func,resultanalyzer_func=None,obf_func=None):
        '''
        传入转换后的请求函数,pyaload,[结果分析函数和混淆函数]
        除payload都是complie后的code class,均为元组(第一个值为函数名,第二个为函数)
        '''
        self.request_func=req_func
        self.payload_queue=Queue()
        self.result_analyzer_func=resultanalyzer_func
        self.obfuscator_func=obf_func
        assert isinstance(self.request_func,tuple)
        if self.result_analyzer_func:assert isinstance(self.result_analyzer_func,tuple)
        if self.obfuscator_func:assert isinstance(self.obfuscator_func,tuple)
        self.result=Queue()
        self.lock=threading.Lock()
        self.end_payload=False#标志payload是否都传送完毕
        self.loop=threading.Thread(target=self.run)
        self.loop.start()


    #添加任务
    def add_payloads(self,payload):
        if isinstance(payload,list):
            for p in payload:
                self.payload_queue.put(p)
        else:
            self.payload_queue.put(payload)
        #print('+',end='')

    def join(self):
        self.lock.acquire()
        self.end_payload=True
        self.lock.release()
        self.loop.join()


    def run(self):
        exec(self.request_func[1])

        if self.result_analyzer_func:exec(self.result_analyzer_func[1])
        if self.obfuscator_func:exec(self.obfuscator_func[1])
        #运行
        #统计参数个数
        var_count=self.request_func[0].count('{}')
        #去掉多余的{}
        if var_count>1:
            self.request_func=(self.request_func[0].replace(','.join(['{}' for i in range(var_count)]),'{}'),self.request_func[1])

        var_list=[i for i in string.ascii_lowercase][:var_count]
        end_p=False
        while True:
            self.lock.acquire()
            end_p=self.end_payload
            self.lock.release()
            if not self.payload_queue.empty():
                pay=self.payload_queue.get()
            else:
                if end_p:
                    return
                else:
                    time.sleep(0.01)
                    continue
            
            #print(self.payload_queue.qsize())

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
            #传入结果分析器,
            if self.result_analyzer_func:
                eval(self.result_analyzer_func[0].format('payl,r'))


class transmitter():
    '''
    多线程发http,无反馈,生成器不能获得请求的结果
    '''
    def __init__(self,req_func,gen_func,resultanalyzer_func=None,obf_func=None,thread_num=20):
        self.request_func=req_func
        self.generator_func=gen_func
        self.result_analyzer_func=resultanalyzer_func
        self.obfuscator_func=obf_func
        assert isinstance(self.request_func,tuple)
        assert isinstance(self.generator_func,tuple)
        if self.result_analyzer_func:assert isinstance(self.result_analyzer_func,tuple)
        if self.obfuscator_func:assert isinstance(self.obfuscator_func,tuple)
        self.result=Queue()
        self.thread_num=thread_num

    def run(self):
        print('[+]starting thread...',end='')
        threads=[transmitter_thread(self.request_func,self.result_analyzer_func,self.obfuscator_func) for i in range(self.thread_num)]
        print('done')

        exec(self.generator_func[1])
        ge=eval(self.generator_func[0])#得到payload生成器
        tmp_pay=[]
        pay_end=False#是否生成结束
        while True:
            for payload in ge:
                if payload==None:
                    continue
                elif isinstance(payload,str):
                    raise Exception('paylaod must tuple')
                tmp_pay.append(payload)
                ge.send(None)#多线程模式无反馈
                if len(tmp_pay)>=5*len(threads):break
            else:
                pay_end=True
            #写入任务
            #print('<send payload ',end='')
            if not pay_end:
                for i in range(len(threads)):
                    threads[i].add_payloads(tmp_pay[i*5:(i+1)*5])
                tmp_pay.clear()
                #print(str(len(threads)*5)+'>',end='')
            else:
                #print(str(len(tmp_pay))+'>',end='')
                t_index=0
                for pay in tmp_pay:
                    threads[t_index].add_payloads(pay)
                    t_index+=1
                    t_index=t_index%len(threads)
                break
        for i in range(len(threads)):
            threads[i].join()
            



def get_transmitter(req_func,gen_func,resultanalyzer_func,obf_func):#必须要一个这个名称的函数,并且返回的对象具有run方法
    trans=transmitter(req_func,gen_func,resultanalyzer_func,obf_func,15)
    return trans