#coding=utf-8
#version 1.0
import base64
from hashlib import md5,sha1

def rc4(text, key = 'default-key', mode = "decode"):
    if mode == "decode":
        text = base64.b64decode(text)   #去除base64
    result = ''
    key_len = len(key)

    #1. 初始化长度为256的S盒
    box = list(range(256))              #将0到255的互不重复的元素装入S盒
    j = 0
    for i in range(256):                #根据密钥打乱S盒
        j = (j + box[i] + ord(key[i%key_len]))%256
        box[i],box[j] = box[j],box[i]   #swap elements

    #2. 保证每256次循环中S盒的每个元素至少被交换过一次
    i = j = 0
    for element in text:
        i = (i+1)%256
        j = (j+box[i])%256
        box[i],box[j] = box[j],box[i]
        k = chr(element ^ box[(box[i]+box[j])%256])
        result += k
    if mode == "encode":
        result = base64.b64encode(result.encode("utf-8"))
    return result

# if __name__=="__main__":
#     key='welcometoicqedu'
#     text='UUyFTj8PCzF6geFn6xgBOYSvVTrbpNU4OF9db9wMcPD1yDbaJw=='
#     print(rc4(text,key=key,mode='decode'))

def crypt(data,key) :
    s = [0] * 256
    for i in range(256) :
        s[i] = i

    j = 0
    for i in range(256) :
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = 0
    j = 0
    res = ""
    for c in data :
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        res = res + chr(c ^ s[(s[i] + s[j]) % 256])
    return res

def tdecode(data ,key) :
    data = base64.b64decode(data)
    salt = data[:16]
    return crypt(data[16:] ,sha1(bytes(key,encoding = "utf8") + salt).digest())

if __name__ =='__main__':
    #key = "welcometoicqedu"
    #data = "UUyFTj8PCzF6geFn6xgBOYSvVTrbpNU4OF9db9wMcPD1yDbaJw=="
    key=input('input key:')
    data=input('input data:')
    data+='=='
    print('plain: '+rc4(data,key=key,mode='decode'))
    print('md5  : '+rc4(data,key=md5(key.encode('utf-8')).hexdigest(),mode='decode'))
    print('sha1 : '+tdecode(data,key))