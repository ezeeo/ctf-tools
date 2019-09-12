#这种实现中:*是匹配任意的长度不为1的字符串(这里的匹配长度黑名单可自定义)
#使用简单的递归搜索
#Date 2019.8.30-20：00->2019.8.31-14:00

import string
from collections import Iterable
import random
import time

def user_data_input():
    '''输入数据并检查，返回字符串和模式串'''
    s=input('str=')
    subs=input('substr=')

    #输入合法性检查
    if sum(map(lambda x:x not in string.ascii_lowercase,s))!=0 or sum(map(lambda x:x not in string.ascii_lowercase+'.*',subs))!=0 :
        print('输入非法')
        exit(1)
    return s,subs

class Matcher:
    '''匹配器,此处的*类似linux的*匹配，将会匹配任意字符串(默认时长度!=1)'''
    def __init__(self,substr='',asterisk_match_len_blacklist=(1,)):
        self._asterisk_match_len_blacklist=asterisk_match_len_blacklist#默认*不匹配长度为1
        self.set_substr(substr)
        
    def set_substr(self,substr):
        '''设置模式串'''
        self._substr=substr
        if not self._legitimacy_check(self._substr,string.printable):
            raise Exception('非法的模式串')
        self._compress_subs_asterisk()

    def _legitimacy_check(self,data,allow_chars):
        '''字符串合法性检查'''
        return True if sum(map(lambda x:x not in allow_chars,data))==0 else False

    def _compress_subs_asterisk(self):
        '''压缩连续的*，当且仅当*可匹配0长度时执行'''
        if 0 in self._asterisk_match_len_blacklist:return
        while '**' in self._substr:
            self._substr=self._substr.replace('**','*')

    def _cal_skip_table(self,s,s_index,subs_next_char):
        '''计算s_index可跳跃位置'''
        if subs_next_char in '.*':
            for i in range(s_index,len(s)):
                yield s_index,i
        else:
            for i in range(s_index,len(s)):
                if s[i]==subs_next_char:
                    yield s_index,i

    def _filter_skip_table(self,skip_table_iterator):
        '''使用黑名单过滤掉不可跳跃的位置'''
        #if not isinstance(skip_table_iterator,Iterable):raise Exception('必须传入迭代器')
        for s_index,i in skip_table_iterator:
            if i-s_index in self._asterisk_match_len_blacklist:continue#不匹配黑名单内的长度
            yield i

    def _basic_match(self,s,subs):
        '''基本匹配性判断'''
        s_index=0
        subs_index=0

        s_index_skip_table=None#标定s串索引能到达的值(出现*用到)
        subs_index_skip_num=0#标定出现*时subs回溯位置(出现*用到)

        while 1:
            if s_index==len(s) or subs_index==len(subs):break
            
            if s[s_index]==subs[subs_index]:
                s_index+=1
                subs_index+=1
            elif subs[subs_index]=='.':
                s_index+=1
                subs_index+=1
            elif subs[subs_index]=='*':
                if subs_index+1==len(subs):
                    #到达模式串末尾,此时s剩余字符数不在黑名单即可匹配成功，否则匹配失败
                    if len(s)-s_index not in self._asterisk_match_len_blacklist:return True
                    else:return False

                subs_index_skip_num=subs_index+1
                s_index_skip_table=self._filter_skip_table(self._cal_skip_table(s,s_index,subs[subs_index_skip_num]))
                
                #对每种*可到达的情况进行递归判断
                for s_skip_num in s_index_skip_table:
                    r=self._basic_match(s[s_skip_num:],subs[subs_index_skip_num:])
                    if r==True:return True
                return False
            else:
                return False
        if s_index==len(s) and subs_index==len(subs):return True#同时结束时可匹配
        elif len(subs[subs_index:])==1 and subs[subs_index]=='*':return True#s先结束且subs剩余为*且*可匹配0长度（可匹配时长度必定为1）
        return False

    def is_match(self,s):
        '''判定是否匹配'''
        if not self._legitimacy_check(s,string.printable):
            raise Exception('非法的字符串')
        return self._basic_match(s,self._substr)













if __name__ == "__main__":
    #s,subs=input_data()
    #s='ghnrpgxdyryzfqlcdnpdfzqqrngkkkphjfeopryw'
    #subs='*g.****..*.*h*.f*.'
    #s =    "mississippi"
    #subs = "mis*is*p*."
    #s='aaaabbbbccc'
    #subs='a*a*.bc.c'
    #s='abbbbccc'
    #subs='a*.bc.c'
    #s='aaa'
    #subs='a*'
    #gen_match_str(30)
    s='2019-09-10-mssb.xls'
    subs='2*.xls*'

    M=Matcher(subs)
    print(M.is_match(s))
    