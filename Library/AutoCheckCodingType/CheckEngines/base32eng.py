#encoding=utf-8
#name Base32eng
#version 1.0
#output normal
#describe 检测是不是base32

from _MetaEng import MetaEngine,auto_muti_return
import sys
import string
import base64

class Base32eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable=string.ascii_uppercase+'01234567='

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
            if len(self.data)%8==0:
                self.possibility+=0.1
                self.describe='data lenth good ,'
            else:
                self.possibility-=0.1
                self.data=self.data+'='*(8-len(self.data)%8)
                self.describe='data lenth%8!=0 ,'
            try:
                self.describe+='default use utf-8'
                self.result=base64.b32decode(self.data).decode('utf-8')
                self.describe+=' decode success'
                self.possibility+=0.2
            except Exception as ex:
                self.describe+=',base32 decode error->'+str(ex)+',output raw result'
                self.possibility-=0.1
                try:
                    self.result=base64.b32decode(self.data).__str__()
                except Exception as ex:
                    self.possibility=0
                    self.describe+=',raw decode fail->'+str(ex)+',end'
                    self.result=''

        

if __name__ == "__main__":
    sys.exit(int(main() or 0))