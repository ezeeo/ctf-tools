#coding:utf-8
#version 1.1
import sys
if sys.platform=='linux':
    import readline
    
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

first_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","babaa","babab","babba","babbb","bbaaa","bbaab"]

second_cipher = ["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab","aabba","aabbb","abaaa","abaaa","abaab","ababa","ababb","abbaa","abbab","abbba","abbbb","baaaa","baaab","baaba","baabb","baabb","babaa","babab","babba","babbb"]

def encode(string):
    upper_flag = False # 用于判断输入是否为大写
    if string.isupper():
        upper_flag = True
        string = string.lower()
    e_string1 = ""
    e_string2 = ""
    for index in string:
        for i in range(0,26):
            if index == alphabet[i]:
                e_string1 += first_cipher[i]
                e_string2 += second_cipher[i]
                break
    if upper_flag:
        e_string1 = e_string1.upper()
        e_string2 = e_string2.upper()
    print ("first method :"+e_string1)
    print ("second method:"+e_string2)
    return


if len(sys.argv)==2:
    data=sys.argv[1]
    if data.isupper() or data.islower():
        pass
    else:
        data=data.upper()
    encode(data)
    exit()

if __name__ == '__main__':
    while True:
        data=input('Bacon encode>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        if data.isupper() or data.islower():
            pass
        else:
            data=data.upper()
        encode(data)