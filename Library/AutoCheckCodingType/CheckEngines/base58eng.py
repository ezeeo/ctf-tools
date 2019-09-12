#encoding=utf-8
#name Base58eng
#version 1.0
#output normal
#describe 检测是不是base58

from _MetaEng import MetaEngine,auto_muti_return
import sys
import string
import base64

class Base58eng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    def b58decode(self):
        temp = 0
        for c in self.data:
            temp = temp * 58 + self.txttable.find(c)
        while temp>0:
            self.result=chr(temp%256)+self.result
            temp = temp//256

    @auto_muti_return
    def check(self):
        for d in self.data:
            if d not in self.txttable:
                self.possibility=0
                self.describe=d+' not allowed'
                break
        else:
            try:
                self.describe='default use ascii'
                self.b58decode()
                self.describe+=' decode success'
                self.possibility+=0.2
            except Exception as ex:
                self.describe='base58 decode error->'+str(ex)
                self.possibility-=0.1
        