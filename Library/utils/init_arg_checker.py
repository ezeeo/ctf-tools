
def check_init_arg(self,strict_mode=False,display_log=True):
    '''动态获取类的参数列表(以且仅以一个下划线开头的不可调用对象)，调用对应的检测函数(_check+参数名)(接收一个值传入)，检查参数正确性，建议仅在init时候调用,strict_mode启用时强制要求所有变量具有检测器'''
    L=self.__dir__()
    R=[]
    #过滤
    for l in L:
        if len(l)>=2 and l[0]=='_' and l[1]!='_':
            R.append(l)
    L=[]
    #过滤掉可调用对象
    for l in R:
        if not callable(eval('self.'+l)):
            L.append(l)
    #调用对应检测器
    errlog=[]
    for l in L:
        if '_check'+l not in self.__dir__():
            if strict_mode:
                errlog.append('[!]error:未找到对应检测器->'+l)
            else:
                continue
        else:
            try:
                r=eval('self._check'+l+'(self.'+l+')')
            except Exception as ex:
                errlog.append('[!]error:检测器运行异常->'+l+'->'+str(ex))
                continue
            if r==True:pass
            else:
                errlog.append('[!]error:参数检测未通过->'+l)
    if display_log:
        for e in errlog:print(e)
    if len(errlog)!=0:
        if display_log:return False
        else:return errlog
    return True

import inspect

def recv_init_args(self):
    ''''返回一个ast，需要exec执行，类的init中调用如下
    
    exec(recv_init_args(self))
    '''
    if '__init__' not in self.__dir__():
        raise Exception('must run in __init__')
    sig=inspect.signature(self.__init__)
    code=''
    for k in sig.parameters:
        code+=('self._'+k+'='+k+'\n')
    return compile(code,'<string>','exec')



if __name__ == "__main__":
    class tttt:
        def __init__(self,a,b,c):
            exec(recv_init_args(self))

    tmp=tttt('1','2','3')
    print(tmp._a)
    print(tmp._b)
    print(tmp._c)