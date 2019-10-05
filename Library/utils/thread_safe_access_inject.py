#向类中注入线程安全访问变量的方法(_get,_set)(仅下划线开头的变量)


def inject_get_set(self,Lock_name='_Lock',get_pattern='{}_get',set_pattern='{}_set',cover=False):
    '''向类中注入线程安全访问变量的方法(_get,_set)(仅下划线开头的变量),Lock_name表示希望Lock对象的名称,pattern表示getset方法的名称模板,{}部分表示原始变量名,cover表示遇到冲突时是否覆盖'''
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

    import threading
    exec('self.'+Lock_name+'=threading.Lock()')

    #注入get,set
    template_get='''def _template_get(self):
    self.{}.acquire()
    t=self.{}
    self.{}.release()
    return t'''
    template_set='''def _template_set(self,v):
    self.{}.acquire()
    self.{}=v
    self.{}.release()'''
    import types
    errlog=[]
    for l in L:
        f=compile(template_get.format(Lock_name,l,Lock_name),'<string>','exec')
        exec(f)
        if 'self.'+get_pattern.format(l) in self.__dir__() and cover==False:
            pass
        else:
            exec('self.'+get_pattern.format(l)+'= types.MethodType(_template_get, self)')

        f=compile(template_set.format(Lock_name,l,Lock_name),'<string>','exec')
        exec(f)
        if 'self.'+set_pattern.format(l) in self.__dir__() and cover==False:
            pass
        else:
            exec('self.'+set_pattern.format(l)+'= types.MethodType(_template_set, self)')

    for e in errlog:print(e)
    if len(errlog)!=0:return False
    return True



class test_inj:
    def __init__(self):
        self._a=123
        self._bb123_1=124
        self._yyyy=False
        self._qwuirgq='12341'
        inject_get_set(self)


if __name__ == "__main__":
    t=test_inj()


    print(t._a_get())
    t._a_set('123123')
    print(t._a_get())

    

