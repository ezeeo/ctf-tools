#encoding=utf-8
#import pycryptodome
#version 1.2

from Crypto.PublicKey import RSA
import os

print('此模块用于从RSA密钥文件中提取数据')
pem=input('input a rsa file path:')
if pem=='exit()':
    exit()
if not os.path.exists(pem):
    print('file not exists')
    exit()
public = RSA.importKey(open(pem).read())

if public.has_private:
    print('----------private key----------')
    try:
        print("n={}\nd={}\n".format(public.n,public.d))
    except Exception as ex:
        print('error in read n,d try output n,e')
        n = public.n
        e = public.e

        print("n=\n%s\ne=\n%s"%(n,e))
        
    try:
        print("p={}\nq={}\ne={}\nu={}".format(public.p,public.q,public.e,public.u))
    except Exception as ex:
        print('error in read p,q')
else:
    print('----------public  key----------')
    n = public.n
    e = public.e
    print("n=\n%s\ne=\n%s"%(n,e))