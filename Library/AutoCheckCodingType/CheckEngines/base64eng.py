#encoding=utf-8
#name Base64eng
#version 1.0
#output normal
#describe 检测是不是base64

from _MetaEng import MetaEngine,auto_muti_return
import string
import base64

class Base64eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable=string.ascii_lowercase+string.ascii_uppercase+string.digits+'+/='

    @auto_muti_return
    def check(self):
        for d in self.data:
            if d not in self.txttable:
                self.possibility=0
                self.describe=d+' not allowed'
                break
        else:
            if self.data[-1]=='=':
                self.possibility=0.8
            else:
                self.possibility=0.7
            try:
                self.describe='default use utf-8'
                self.result=base64.b64decode(self.data+'==').decode('utf-8')
                self.describe+=' decode success'
                self.possibility+=0.2
            except Exception as ex:
                self.describe='base64 decode error->'+str(ex)+',output raw result'
                self.possibility-=0.1
                self.result=base64.b64decode(self.data+'==').__str__()
        
