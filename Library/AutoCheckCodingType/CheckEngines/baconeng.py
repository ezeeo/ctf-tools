#encoding=utf-8
#name BaconEng
#version 1.0
#output normal
#describe 检测是不是培根密码

from _MetaEng import MetaEngine,auto_muti_return
import re

class BaconEng(MetaEngine):
    def __init__(self, data = ''):
        super().__init__(data)
        self.alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        self.first_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","babaa","babab","babba","babbb","bbaaa","bbaab"]
        self.second_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","baabb","babaa","babab","babba","babbb"]



    @auto_muti_return
    def check(self):
        s1,s2,a,b=self.__parse_ab_for_other_char(self.data)
        if s1!=False:#只有两种字符
            if (a=='a' and b=='b') or (a=='A' and b=='B'):
                self.possibility+=0.2
            else:
                self.possibility+=0.1
            self.result+="[-]a='{}' b='{}'".format(a,b)
            self.__decode(s1)
            self.result+="\n[-]a='{}' b='{}'".format(b,a)
            self.__decode(s2)
        else:#大小写识别模式
            self.describe+=',now try parse_ab_for_case_write'
            s1,s2=self.__parse_ab_for_case_write(self.data)
            self.result+="[-]a=lower b=super"
            self.__decode(s1)
            self.result+="\n[-]a=super b=lower"
            self.__decode(s2)
            self.possibility+=0.1



    #两种字符识别模式
    def __parse_ab_for_other_char(self,data):
        if len(data)<5 or len(data)%5!=0:
            self.describe+='[!]Failure of Character Recognition Mode,lenth<5 or lenth%5!=0'
            self.possibility=0.1
            return False,False,False,False#小于一字符长度或者字符长度不正确
        charA=''
        charB=''
        for c in data:
            if charA=='':
                charA=c
                continue
            if charB=='' and c!=charA:
                charB=c
                continue
            if c!=charA and c!=charB:
                self.describe+='[!]Character types greater than 2'
                self.possibility=0.1
                return False,False,False,False
        result1=''
        result2=''
        for c in data:
            if c==charA:
                result1+='a'
                result2+='b'
            else:
                result1+='b'
                result2+='a'
        self.describe+='[+]Character types = 2,good'
        self.possibility=0.4
        return result1,result2,charA,charB


    #删除除大小写以外所有字符
    def __clean_to_case_write(self,data):
        result=''
        for c in data:
            if c.isupper() or c.islower():
                result+=c
        return result

    #大小写识别模式
    def __parse_ab_for_case_write(self,data):
        data=self.__clean_to_case_write(data)
        result1=''
        result2=''
        for c in data:
            if c.islower():
                result1+='a'
                result2+='b'
            else:
                result1+='b'
                result2+='a'
        return result1,result2




    def __decode(self,e_string):
        upper_flag = False  # 用于判断输入是否为大写
        if e_string.isupper():
            upper_flag = True
            e_string = e_string.lower()
        e_array = re.findall(".{5}",e_string)
        d_string1 = ""
        d_string2 = ""
        for index in e_array:
            flag1=False
            flag2=False
            for i in range(0,26):
                if not flag1 and index == self.first_cipher[i]:
                    d_string1 += self.alphabet[i]
                    flag1=True
                if not flag2 and index == self.second_cipher[i]:
                    if i==8 or i==9:
                        d_string2 +='(i/j)'
                    else:
                        d_string2 += self.alphabet[i]
                    flag2=True
        if upper_flag:
            d_string1 = d_string1.upper()
            d_string2 = d_string2.upper()
        self.result+="first method:"+d_string1
        self.result+=",second method:"+d_string2
        return