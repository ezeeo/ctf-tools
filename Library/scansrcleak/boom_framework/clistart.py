import os
import sys
import signal
import time

path=os.path.abspath('.')+'/Library/scansrcleak/boom_framework'
print('[+]path:'+path)
if not path+'/converter' in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path+'/converter')
if not path+'/transmitter' in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path+'/transmitter')

#响应信号
def exit_server(signum, frame):
    print('[!]get stop signal, now stop...')

    exit()
signal.signal(signal.SIGINT, exit_server)
signal.signal(signal.SIGTERM, exit_server)



class boom_task():

    def __init__(self,c,r,g,re,o,t):
        '''
        converter,request,generator,result_analyzer,obfuscator,transmitter
        '''
        if not c:
            self.converter=None
        elif os.path.exists(path+'/converter/'+c):
            self.converter=c
        else:raise Exception('Parameter error:converter not found')

        if os.path.exists(path+'/request/'+r):
            self.request=path+'/request/'+r
        else:raise Exception('Parameter error:request not found')

        if os.path.exists(path+'/generator/'+g):
            self.generator=path+'/generator/'+g
        else:raise Exception('Parameter error:generator not found')

        if not re:
            self.result_analyzer=None
        elif os.path.exists(path+'/result_analyzer/'+re):
            self.result_analyzer=path+'/result_analyzer/'+re
        else:raise Exception('Parameter error:result_analyzer not found')

        if not o:
            self.obfuscator=None
        elif os.path.exists(path+'/obfuscator/'+o):
            self.obfuscator=path+'/obfuscator/'+o
        else:raise Exception('Parameter error:obfuscator not found')

        if not t:
            raise Exception('must have transmitter')
        if os.path.exists(path+'/transmitter/'+t):
            self.transmitter=t
        else:raise Exception('Parameter error:transmitter not found')

        self.__check_and_set()
        
    def __check_and_set(self):
        #设置request
        if self.converter:
            exec('from {} import convert'.format(self.converter[:-3]))
            r=eval("convert('"+self.request.replace('/','/')+"',None)")#返回tuple,(调用语句,函数str)
            if r==False:
                raise Exception('convert request fail')
            else:
                self.request=(r[0],compile(r[1],'<string>', 'exec'))
        else:
            with open(self.request,'r',encoding='utf-8') as f:t=f.read()
            #获取调用str
            self.request=(self.__get_call_str(t.strip().split('\n')[0],True),compile(t,'<string>', 'exec'))
        #设置generator
        with open(self.generator,'r',encoding='utf-8') as f:t=f.read()
        self.generator=(self.__get_call_str(t.strip().split('\n')[0],False),compile(t,'<string>', 'exec'))

        if self.result_analyzer:
            with open(self.result_analyzer,'r',encoding='utf-8') as f:t=f.read()
            self.result_analyzer=(self.__get_call_str(t.strip().split('\n')[0],False),compile(t,'<string>', 'exec'))

        if self.obfuscator:
            with open(self.obfuscator,'r',encoding='utf-8') as f:t=f.read()
            self.obfuscator=(self.__get_call_str(t.strip().split('\n')[0],False).replace('()','({})'),compile(t,'<string>', 'exec'))

    #从首行提取调用字符串
    def __get_call_str(self,first_line,is_request):
        if first_line[:3]!='def' or first_line[-2:]!='):' or first_line.find('(')==-1:
            raise Exception('request method check fail')
        if first_line.count(',')!=0:
            if is_request:
                return first_line[4:first_line.find('(')]+ '('+','.join(['{}' for i in range(first_line.count(',')+1)])+')'
            else:
                return first_line[4:first_line.find('(')]+'({})'
        elif first_line.find('()')!=-1:
            return first_line[4:first_line.find('(')]+'()'
        else:
            return first_line[4:first_line.find('(')]+'({})'


    def run_task(self):
        exec('from {} import get_transmitter'.format(self.transmitter[:-3]))
        with open(path+'/transmitter/'+self.transmitter,'r',encoding='utf-8') as f:t=f.read()
        t=t.strip().split('\n')
        for l in t:
            if l[:4]=='from' or l[:7]=='import':
                eval(l)
            else:
                break
        
        trans=eval('get_transmitter(self.request,self.generator,self.result_analyzer,self.obfuscator)')
        result=trans.run()
        return result






if __name__ == "__main__":
    if len(sys.argv)==1:
        print('[-]no target...now exit')
        exit()
    elif len(sys.argv)>2:
        print('[!]argv num error...now exit')
        exit()
    else:
        arg=sys.argv[1].split('=',maxsplit=1)
        if len(arg)!=2:
            print('[!]arg format error...now exit')
            exit()
        if arg[0]=='u':
            url=arg[1].strip()
            raw_file=None
        elif arg[0]=='l':
            raw_file=arg[1].strip()
            url=None
        else:
            print('[!]arg method error...now exit')
            exit()

    if url:
        if url[:4]!='http':
            url='http://'+url
        c=None
        #设置请求
        r='temp.py'
    else:
        #设置请求转换器
        c='rawtorequests.py'
        r='temp.txt'

    #设置payload生成器
    g='srcleakgen.py'

    #设置请求结果分析器
    re='srcleakana.py'

    #设置混淆器
    o=None

    #设置传输器
    t='muti_thread_worker.py'
    #t='single_thread_worker.py'

    try:
        print('[+]set done...start init')
        print('[+]default thread=15')
        b=boom_task(c,r,g,re,o,t)
        print('[+]init on '+time.asctime(time.localtime(time.time())))
        print('[+]start task...')
        b.run_task()#启动
        print('\r[+]end on   '+time.asctime(time.localtime(time.time())))
    except Exception as ex:
        print('\n[!]error->'+str(ex))
        exit()
    