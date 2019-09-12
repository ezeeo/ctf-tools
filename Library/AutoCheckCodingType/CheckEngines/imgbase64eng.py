#encoding=utf-8
#name ImgBase64eng
#version 1.0
#output normal
#describe 检测是不是base64的图片

from _MetaEng import MetaEngine,auto_muti_return
import sys
import string
import base64
from urllib import parse

class ImgBase64eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable=string.ascii_lowercase+string.ascii_uppercase+string.digits+'+/='+':;,'

    @auto_muti_return
    def check(self):
        tmpdata=parse.unquote(self.data)
        if tmpdata!=self.data:
            self.possibility=0.1
            self.data=tmpdata

        for d in self.data:
            if d not in self.txttable:
                self.possibility=0
                self.describe=d+' not allowed'
                break
        else:
            if len(self.data)<len('data:image/gif;base64,'):
                self.describe='data too short'
            else:
                imginfos=('data:image/gif;base64,','data:image/png;base64,','data:image/jpeg;base64,','data:image/x-icon;base64,')
                index=0
                for i in imginfos:
                    if i in self.data:
                        self.possibility+=0.7
                        self.describe='found '+i
                        break
                    index+=1
                else:
                    self.describe='not found any'
                if self.data[:22]=='data:image/gif;base64,' or self.data[:22]=='data:image/png;base64,' or self.data[:23]=='data:image/jpeg;base64,' or self.data[:25]=='data:image/x-icon;base64,':
                    self.possibility+=0.1
                tmpd=self.data.split(imginfos[index],maxsplit=1)
                try:
                    base64.b64decode(tmpd[1])
                    self.possibility+=0.1
                except :
                    self.describe+=' decode error'
                    self.possibility-=0.1
                