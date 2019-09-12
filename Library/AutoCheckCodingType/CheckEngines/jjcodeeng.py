#encoding=utf-8
#name JJCodeEng
#version 1.0
#output normal
#describe 检测是不是jjencode,jjencode可以将JS代码转换成只有符号的字符串


from _MetaEng import MetaEngine,auto_muti_return
import sys


class JJCodeEng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)

        self.__split=["=~[];"
        , "={___:++" ,",$$$$:(![]+\"\")[","],__$:++",",$_$_:(![]+\"\")[","],_$_:++"
        ,",$_$$:({}+\"\")[","],$$_$:(","[","]+\"\")[","],_$$:++",",$$$_:(!\"\"+\"\")["
        ,"],$__:++",",$_$:++",",$$__:({}+\"\")[","],$$_:++",",$$$:++",",$___:++",",$__$:++","};"
        ,".$_="
        "(",".$_=","+\"\")[",".$_$]+",
        "(","._$=",".$_[",".__$])+",
        "(",".$$=(",".$+\"\")[",".__$])+",
        "((!",")+\"\")[","._$$]+",
        "(",".__=",".$_[",".$$_])+",
        "(",".$=(!\"\"+\"\")[",".__$])+",
        "(","._=(!\"\"+\"\")[","._$_])+"
        ,".$_[",".$_$]+"
        ,".__+"
        ,"._$+"
        ,".$;"
        ,".$$="
        ,".$+",
        "(!\"\"+\"\")[","._$$]+"
        ,".__+"
        ,"._+"
        ,".$+"
        ,".$$;"
        ,".$=(",".___)[",".$_][",".$_];"
        ,".$(",".$(",".$$+\"\\\"\"+"]
        self.__end="\"\\\"\")())();"

    @auto_muti_return
    def check(self):
        if self.__end not in self.data:
            self.describe+='警告,必要结束标记未找到'
            self.possibility=0
        else:
            index=self.data.index(self.__end)
            if index+len(self.__end)==len(self.data):
                self.describe+='结束标记位于预计位置'
                self.possibility+=0.4
            else:
                self.describe+='注意,结束标记不在预计位置'
                self.possibility+=0.2
                self.result=self.data[:index+len(self.__end)]
        num=0
        for s in self.__split:
            if s in self.data:num+=1
        if num==len(self.__split):
            self.describe+=',所有分隔符均找到'
        else:
            self.describe+=',找到分隔符{}|{}'.format(num,len(self.__split))
        self.possibility+=num/len(self.__split)*0.6
