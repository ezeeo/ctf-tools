#encoding=utf-8
#name AACodeEng
#version 1.0
#output normal
#describe 检测是不是aaencode,aaencode可以将JS代码转换成常用的网络表情,也就是我们说的颜文字js加密


from _MetaEng import MetaEngine,auto_muti_return


class AACodeEng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.__start="ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); (ﾟДﾟ) =(ﾟΘﾟ)= (o^_^o)/ (o^_^o);(ﾟДﾟ)={ﾟΘﾟ: '_' ,ﾟωﾟﾉ : ((ﾟωﾟﾉ==3) +'_') [ﾟΘﾟ] ,ﾟｰﾟﾉ :(ﾟωﾟﾉ+ '_')[o^_^o -(ﾟΘﾟ)] ,ﾟДﾟﾉ:((ﾟｰﾟ==3) +'_')[ﾟｰﾟ] }; (ﾟДﾟ) [ﾟΘﾟ] =((ﾟωﾟﾉ==3) +'_') [c^_^o];(ﾟДﾟ) ['c'] = ((ﾟДﾟ)+'_') [ (ﾟｰﾟ)+(ﾟｰﾟ)-(ﾟΘﾟ) ];(ﾟДﾟ) ['o'] = ((ﾟДﾟ)+'_') [ﾟΘﾟ];(ﾟoﾟ)=(ﾟДﾟ) ['c']+(ﾟДﾟ) ['o']+(ﾟωﾟﾉ +'_')[ﾟΘﾟ]+ ((ﾟωﾟﾉ==3) +'_') [ﾟｰﾟ] + ((ﾟДﾟ) +'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ ((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [(ﾟｰﾟ) - (ﾟΘﾟ)]+(ﾟДﾟ) ['c']+((ﾟДﾟ)+'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ (ﾟДﾟ) ['o']+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ];(ﾟДﾟ) ['_'] =(o^_^o) [ﾟoﾟ] [ﾟoﾟ];(ﾟεﾟ)=((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟДﾟ) .ﾟДﾟﾉ+((ﾟДﾟ)+'_') [(ﾟｰﾟ) + (ﾟｰﾟ)]+((ﾟｰﾟ==3) +'_') [o^_^o -ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟωﾟﾉ +'_') [ﾟΘﾟ]; (ﾟｰﾟ)+=(ﾟΘﾟ); (ﾟДﾟ)[ﾟεﾟ]='\\'; (ﾟДﾟ).ﾟΘﾟﾉ=(ﾟДﾟ+ ﾟｰﾟ)[o^_^o -(ﾟΘﾟ)];(oﾟｰﾟo)=(ﾟωﾟﾉ +'_')[c^_^o];(ﾟДﾟ) [ﾟoﾟ]='\"';(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (ﾟεﾟ+(ﾟДﾟ)[ﾟoﾟ]+"
        self.__end="(ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');"
        self.__split="(ﾟДﾟ)[ﾟεﾟ]+"
        self.__meta=[
		"(c^_^o)",
		"(ﾟΘﾟ)",
		"((o^_^o) - (ﾟΘﾟ))",
		"(o^_^o)",
		"(ﾟｰﾟ)",
		"((ﾟｰﾟ) + (ﾟΘﾟ))",
		"((o^_^o) +(o^_^o))",
		"((ﾟｰﾟ) + (o^_^o))",
		"((ﾟｰﾟ) + (ﾟｰﾟ))",
		"((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))",
		"(ﾟДﾟ) .ﾟωﾟﾉ",
		"(ﾟДﾟ) .ﾟΘﾟﾉ",
		"(ﾟДﾟ) ['c']",
		"(ﾟДﾟ) .ﾟｰﾟﾉ",
		"(ﾟДﾟ) .ﾟДﾟﾉ",
		"(ﾟДﾟ) [ﾟΘﾟ]"
        ]
        self.__err=["X=_=3;","X / _ / X < \"来週も見てくださいね!\";"]

        self.__up127='(oﾟｰﾟo)+'#大于127的字符标识

    @auto_muti_return
    def check(self):
        #print(self.data)
        start=self.data.find(self.__start)#开始位置
        if start==-1 and self.__start.replace(' ','')[:670] in self.data.replace(' ',''):#避免转义冲突
            self.describe+='开始标记空格数不匹配'
            self.possibility+=0.3
            start=self.data.find("ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻")
        elif start==-1:
            self.describe+='未找到开始标记'
        elif start==0:
            self.describe+='开始标记完全正确'
            self.possibility+=0.4
        else:
            self.describe+='警告,开始位于'+str(start)
            self.possibility+=0.3

        end=self.data.find(self.__end)#结束位置
        if start==-1 and self.__end.replace(' ','') in self.data.replace(' ',''):
            self.describe+=',结束标记空格数不匹配'
            self.possibility+=0.3
            end=self.data.replace(' ','').find(self.__end.replace(' ',''))
            end=self.data.find("('_');",end)
        elif end==-1:
            self.describe+=',未找到结束标记'
        elif end==len(self.data)-len(self.__end):
            self.describe+=',结束标记完全正确'
            self.possibility+=0.4
        else:
            self.describe+=',警告,结束位于'+str(end+len(self.__end))
            self.possibility+=0.3

        err=self.data.find(self.__err[0])#错误信息位置
        if err==-1:
            err=self.data.find(self.__err[1])
        if err==-1:
            self.describe+=",未找到编码错误标记"
        else:
            self.describe+=',警告,找到编码错误标记'
            self.possibility+=0.1

        split_num=self.data.count(self.__split)#输入字符数
        if split_num>0:
            self.describe+=',检测到输入字符数'+str(split_num)
            self.possibility+=0.1
        else:
            self.describe+=',警告,未检测到输入字符'

        text_num=sum([self.data.count(t) for t in self.__meta])#使用的编码字符数
        if text_num>0:
            self.describe+=',检测到用于编码的颜文字字符数'+str(split_num)
            self.possibility+=0.1
        else:
            self.describe+=',警告,未检测到用于编码的颜文字'
        up127=self.data.count(self.__up127)#大于127的字符个数
        if split_num>0 and up127>0:
            self.describe+=',检测到ascii>127的字符数'+str(split_num)

        if start!=-1 and end!=-1:
            self.result=self.data[start:end+len(self.__end)]
