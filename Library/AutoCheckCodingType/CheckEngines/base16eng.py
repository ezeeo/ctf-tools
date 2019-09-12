#encoding=utf-8
#name Base16eng
#version 1.0
#output normal
#describe 检测是不是base16

from _MetaEng import MetaEngine,auto_muti_return
import sys
import string
import base64

class Base16eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable='ABCDEF'+string.digits#长度为偶数
        self.describe=''
        self.result=''
    
    def __check_up(self):#默认状态A-F为大写
        '''检测是不是符合大写情况'''
        for d in self.data:
            if d not in self.txttable:
                self.describe=d+' not allowed'
                return False
        return True

    def __check_low(self):
        '''检测是不是符合小写情况'''
        for d in self.data:
            if d not in self.txttable.lower():
                self.describe=d+' not allowed'
                return False
        return True

    @auto_muti_return
    def check(self):
        ups=self.__check_up()
        lows=self.__check_low()
        if ups==False and lows==False:
            self.possibility=0
        else:
            if len(self.data)%2==0:
                self.possibility=0.8
                self.describe+=' len%2==0,good'
            else:
                self.possibility=0.5
                self.describe+=' len%2!=0,not good'
            if ups==True and lows==False:self.possibility-=0
            if ups==True and lows==True:self.possibility-=0.1
            if ups==False and lows==True:self.possibility-=0.2

            if len(self.data)%2==0:#可正常解码
                try:
                    self.describe='default use utf-8'
                    self.result=base64.b16decode(self.data.upper()).decode('utf-8')
                    self.describe+=' decode success'
                    self.possibility+=0.2
                except Exception as ex:
                    self.describe+=' decode error->'+str(ex)
                    self.possibility-=0.1
                    self.result=''
            else:#长度不符合标准
                success=False
                for t in self.txttable:
                    try:
                        self.describe='default use utf-8'
                        self.result=base64.b16decode(self.data.upper()+t).decode('utf-8')
                        self.describe+=' decode success with append "'+t+'"'
                        self.possibility+=0.2
                        success=True
                        break
                    except:
                        pass
                if success==False:
                    self.describe+=' all try decode fail'
                    self.possibility-=0.1
            if self.possibility<0:self.possibility=0
