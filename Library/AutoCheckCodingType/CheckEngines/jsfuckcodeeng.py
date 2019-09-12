#encoding=utf-8
#name JSFuckCodeEng
#version 1.0
#output normal
#describe 检测是不是JSFuck,JSFuck可以让你只用6个字符[ ]( ) ! +来编写 JavaScript 程序
#pip PyExecJS

from _MetaEng import MetaEngine,auto_muti_return
import sys
import execjs



class JSFuckCodeEng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.txttable='[]()!+'
    
    @auto_muti_return
    def check(self):
        if not self.check_in_txttable(ex_allow=' '):
            return
        else:
            self.possibility+=0.2
            try:
                ctx = execjs.eval(self.data.replace(' ','')) #运行js
                self.result=str(ctx)
                self.describe+=',run js success'
                if ctx==None:
                    self.possibility+=0.2
                    self.describe+=',result is None, code does not return a value'
                    return
                else:
                    self.possibility+=0.3
                    self.describe+=',normal return value'
                    self.result=str(ctx)
                    return
            except :
                self.possibility+=0.1
                self.describe+=',run js fail'
