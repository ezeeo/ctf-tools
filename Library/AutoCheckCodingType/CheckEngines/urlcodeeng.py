#encoding=utf-8
#name UrlCodeEng
#version 1.0
#output normal
#describe 检测是不是urlencode

from _MetaEng import MetaEngine,auto_muti_return
from urllib import parse
import string

class UrlCodeEng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable=string.ascii_lowercase+string.ascii_uppercase+string.digits+'-_.~'+"!*'();:@&=+$,/?#[]"

    
    #@auto_return
    @auto_muti_return
    def check(self):
        for i in self.data:
            if i not in self.txttable:
                self.possibility=0.4
                break
        else:
            self.possibility=0
            self.describe='未出现需要url编码的字符'
            self.result=''
            return
        if '%' in self.data:
            self.possibility+=0.1
        else:
            self.possibility=0
            self.describe='出现需编码字符但未出现%'
            self.result=''
            return
        try:
            self.result=parse.unquote(self.data)
            self.describe='url解码成功'
            self.possibility+=0.2
            if self.data!=self.result:
                self.possibility+=0.2
                self.describe+=',且结果存在变化'
            else:
                self.possibility-=0.1
                self.describe+=',但结果无变化'
        except Exception as ex:
            self.describe='url解码失败->'+str(ex)
            self.result=''
            self.possibility-=0.2
