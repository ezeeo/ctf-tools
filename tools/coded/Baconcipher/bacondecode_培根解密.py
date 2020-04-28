#coding:utf-8
#version 1.1
import sys
import re
if sys.platform=='linux':
    import readline
    
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

first_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","babaa","babab","babba","babbb","bbaaa","bbaab"]

second_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","baabb","babaa","babab","babba","babbb"]

def decode(e_string):
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
            if not flag1 and index == first_cipher[i]:
                d_string1 += alphabet[i]
                flag1=True
            if not flag2 and index == second_cipher[i]:
                if i==8 or i==9:
                    d_string2 +='(i/j)'
                else:
                    d_string2 += alphabet[i]
                flag2=True
    if upper_flag:
        d_string1 = d_string1.upper()
        d_string2 = d_string2.upper()
    print ("first method :"+d_string1)
    print ("second method:"+d_string2)
    return

#两种字符识别模式
def parse_ab_for_other_char(data):
    if len(data)<5 or len(data)%5!=0:
        print('[!]Failure of Character Recognition Mode,lenth<5 or lenth%5!=0')
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
            print('[!]Character types greater than 2')
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
    return result1,result2,charA,charB

#删除除大小写以外所有字符
def clean_to_case_write(data):
    result=''
    for c in data:
        if c.isupper() or c.islower():
            result+=c
    return result

#大小写识别模式
def parse_ab_for_case_write(data):
    data=clean_to_case_write(data)
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



if len(sys.argv)==2:
    data=sys.argv[1]
    s1,s2,a,b=parse_ab_for_other_char(data)
    if s1!=False:#只有两种字符
        print("[-]a='{}' b='{}'".format(a,b))
        decode(s1)
        print("[-]a='{}' b='{}'".format(b,a))
        decode(s2)
    else:#大小写识别模式
        s1,s2=parse_ab_for_case_write(data)
        print("[-]a=lower b=super")
        decode(s1)
        print("[-]a=super b=lower")
        decode(s2)
    exit()





if __name__ == '__main__':
    while True:
        data=input('Bacon decode>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        s1,s2,a,b=parse_ab_for_other_char(data)
        if s1!=False:#只有两种字符
            print("[-]a='{}' b='{}'".format(a,b))
            decode(s1)
            print("[-]a='{}' b='{}'".format(b,a))
            decode(s2)
            continue
        else:#大小写识别模式
            s1,s2=parse_ab_for_case_write(data)
            print("[-]a=lower b=super")
            decode(s1)
            print("[-]a=super b=lower")
            decode(s2)
            continue
            