#encoding=utf-8
#name MetaEngine
#version 1.5
#output normal
#describe 元类

from abc import ABC,abstractmethod
class MetaEngine(ABC):
    '''元类,建议调用构造函数以支持解码数据和多返回，注意如果需要使用自有解码器需要在调用父类init之后调用add_decode_func添加解码函数'''
    def __init__(self,data=''):
        '''如果需要用到多返回，则必须调用此构造函数'''
        assert isinstance(data,str)
        self.data=data
        self.possibility=0#是此编码的可能性0-1
        self.describe=''#随意
        self.result=''#解码后的数据
        self.txttable=''

        self.now_decode_mode=None#默认没有解码器，或者可以是下面list中的一个
        self.decode_as_list=[]#以什么方式decode
        self.decode_func={}.fromkeys(self.decode_as_list)#解码函数,一输入一输出
        self.use_muti_return=False#是否使用多返回(复杂模式)
        self.muti_mode_return={}#多模式返回

        self.__init_decode_func()#创建解码函数


    def add_decode_func(self,name,func):
        '''添加解码器'''
        self.decode_as_list.append(name)
        self.decode_func[name]=func

    def __init_decode_func(self):
        '''初始化解码器，所有的解码函数应该在这里创建，对应关系使用表驱动，注意解码函数不要破坏原有变量'''
        def hex_decode(x):
            if isinstance(x,str):
                if x[:2]=='0x':
                    x=x[2:]
                x=x.strip().upper()
                tmp_txttable=self.txttable
                tmp_data=self.data
                self.txttable='0123456789ABCDEF'
                self.data=x
                if not self.check_in_txttable(desc=False):
                    self.txttable=tmp_txttable
                    self.data=tmp_data
                    return None
                self.txttable=tmp_txttable
                self.data=tmp_data
                if len(x)%2!=0:x='0'+x
                result=[]
                for i in range(len(x)//2):
                    try:
                        result.append(chr(int(x[2*i:2*i+2],base=16)))
                    except :
                        return None
                return ''.join(result)
            else:return None
        self.decode_as_list.append('hexdecode')
        self.decode_func['hexdecode']=hex_decode


        def url_decode(x):
            if isinstance(x,str):
                try:
                    from urllib import parse
                    result= parse.unquote(x)
                    if result==x:
                        return None
                    else:
                        return result
                except:
                    return None
            else:return None
        self.decode_as_list.append('urldecode')
        self.decode_func['urldecode']=url_decode


    def decode(self):
        '''使用所有内置解码器进行解码,警告:此方法不允许重写'''
        result={}
        for decoder in self.decode_as_list:
            rs=self.decode_func[decoder](self.data)
            if rs!=None:
                result[decoder]=rs

        return result

    def set_data(self,data):
        '''设置要检测的数据'''
        assert isinstance(data,str)
        self.__clear()
        self.data=data

    @abstractmethod#虚函数
    def check(self):
        '''需要写的核心地方，必须重新实现'''
        pass


    def add_return(self,clean_result=True):
        '''添加一个多模式返回的结果,是否清除数据(possibility,describe,result)可选'''
        if self.use_muti_return!=True:
            raise Exception('必须显式的启用多模式返回，或者使用auto_muti_return装饰器')
        if self.now_decode_mode==None:
            raise Exception('解码模式名不能为空')
        self.muti_mode_return[self.now_decode_mode]=self.normal_return()



    #普通模式标准返回
    def normal_return(self):
        '''普通模式标准返回'''
        if isinstance(self.possibility,float):self.possibility=round(self.possibility,2)
        if self.possibility>1:self.possibility=1
        return (0 if self.possibility<0 else self.possibility,self.describe,self.result)

    def __clear(self):
        self.possibility=0#是此编码的可能性0-1
        self.describe=''#随意
        self.result=''#解码后的数据

    def check_in_txttable(self,ex_allow=None,desc=True):
        '''检查data里的数据是不是都在txttable里，desc是否添加描述'''
        try:
            tmp=self.txttable
            if ex_allow:
                if isinstance(tmp,list):
                    if isinstance(ex_allow,list):
                        tmp+=ex_allow
                    elif isinstance(ex_allow,str):
                        tmp+=[e for e in ex_allow]
                    else:
                        pass
                elif isinstance(tmp,str):
                    if isinstance(ex_allow,list):
                        tmp+=''.join(ex_allow)
                    elif isinstance(ex_allow,str):
                        tmp+=ex_allow
                    else:
                        pass
                else:
                    pass
                
        except :
            return False
        if not tmp:
            return False
        for d in self.data:
            if d not in tmp:
                if desc==True:self.describe+=d+' is not allow'
                return False
        self.describe+='char check pass'
        return True

def auto_return(func):
    '''使用这个装饰器可以让你的检测函数不用去手动写返回语句了，直接return就好'''
    def wrapper(me_instance):
        func(me_instance)
        return me_instance.normal_return()
    return wrapper


def auto_muti_return(func):
    '''使用这个装饰器可以让你的检测函数不仅支持auto_return功能，还将增加使用自带的解码器解码后的检测结果，如果解码是有成功的情况将会自动返回多个结果'''
    def wrapper(me_instance):
        me_instance.use_muti_return=True
        decode_datas=me_instance.decode()
        if len(decode_datas)==0:
            #不能解码为其他数据
            func(me_instance)
            return me_instance.normal_return()
        else:
            me_instance.now_decode_mode='raw'
            func(me_instance)
            me_instance.add_return(me_instance)

            for decode_name in decode_datas.keys():
                me_instance.now_decode_mode=decode_name
                me_instance.set_data(decode_datas[decode_name])
                func(me_instance)
                me_instance.add_return(me_instance)
            muti_result_tmp=me_instance.muti_mode_return
            me_instance.muti_mode_return={}#清空当前处理的结果，避免对下次造成影响
            return muti_result_tmp
    return wrapper