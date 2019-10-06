def value_snapshot(self,cover=False):
    '''对类对象中的_开头的变量进行备份,cover表示遇到冲突时是否覆盖'''
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

    #过滤掉过于动态对象
    R=[]
    for l in L:
        if eval('isinstance(self.'+l+',int)') or eval('isinstance(self.'+l+',float)') or eval('isinstance(self.'+l+',str)') or eval('isinstance(self.'+l+',tuple)'):
            R.append(l)
        
    for l in R:
        if l+'_backup' in self.__dir__() and cover==False:
            pass
        else:
            exec('self.'+l+'_backup=self.'+l)


def value_rollback(self,clean_list=False,clean_queue=False):
    '''对类对象中的_开头的变量进行还原,需要事先调用value_snapshot'''
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
    for l in L:
        if len(l)>7 and l[-7:]=='_backup' and l[:-7] in L:
            exec('self.'+l[:-7]+'=self.'+l)
    #处理list
    if clean_list:
        L=self.__dir__()
        R=[]
        for l in L:
            if len(l)>=2 and l[0]=='_' and l[1]!='_' and eval('isinstance(self.'+l+',list)')==True:
                R.append(l)
        for l in R:
            exec('self.'+l+'.clear()')
    #处理queue
    if clean_queue:
        from queue import Queue
        L=self.__dir__()
        R=[]
        for l in L:
            if len(l)>=2 and l[0]=='_' and l[1]!='_' and eval('isinstance(self.'+l+',Queue)')==True:
                R.append(l)
        for l in R:
            while not eval('self.'+l+'.empty()'):
                eval('self.'+l+'.get()')
    #print(R)




class test_snapshot:
    def __init__(self):
        self._a=123
        self._b=234
        self._c=False
        self._d='345'
        self._e=[]
        from queue import Queue
        self._f=Queue()
        self._f.put(123)

        value_snapshot(self)
    def rb(self):
        value_rollback(self,True,True)


if __name__ == "__main__":
    t=test_snapshot()
    print(t._a)
    print(t._b)
    print(t._c)
    print(t._d)
    t._a='111'
    t._b='222'
    t._c='333'
    t._d='444'
    print(t._a)
    print(t._b)
    print(t._c)
    print(t._d)
    t._e.append(111)
    t.rb()
    print(t._e)
    print(t._f.qsize())
    # print(t._a)
    # print(t._b)
    # print(t._c)
    # print(t._d)
    #print(t.__dir__())