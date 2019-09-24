def check_init_arg(self):
    '''动态获取类的参数列表(以且仅以一个下划线开头的不可调用对象)，调用对应的检测函数(_check+参数名)(接收一个值传入)，检查参数正确性，建议仅在init时候调用'''
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
            errlog.append('[!]error:未找到对应检测器->'+l)
        else:
            try:
                r=eval('self._check'+l+'(self.'+l+')')
            except Exception as ex:
                errlog.append('[!]error:检测器运行异常->'+l+'->'+str(ex))
                continue
            if r==True:pass
            else:
                errlog.append('[!]error:参数检测未通过->'+l)
    for e in errlog:print(e)
    if len(errlog)!=0:return False
    return True