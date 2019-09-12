#encoding=utf-8
#name Base85eng
#version 1.0
#output normal
#describe 检测是不是base85

from _MetaEng import MetaEngine,auto_muti_return
import sys
import string
import base64

class Base85eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable=string.ascii_lowercase+string.ascii_uppercase+string.digits+'.-:+=^!/*?&<>()[]{}@%$#'

    @auto_muti_return
    def check(self):
        for d in self.data:
            if d not in self.txttable:
                self.possibility=0
                self.describe=d+' not allowed'
                break
        else:
            try:
                self.describe='default use utf-8'
                self.result=base64.b85decode(self.data+'==').decode('utf-8')
                self.describe+=' decode success'
                self.possibility+=0.2
            except Exception as ex:
                self.describe='base85 decode error->'+str(ex)+',output raw result'
                self.possibility-=0.1
                self.result=base64.b85decode(self.data+'==').__str__()
        