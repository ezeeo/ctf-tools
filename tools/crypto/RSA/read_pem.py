#encoding=utf-8
#import pycryptodome
#version 1.0

from Crypto.PublicKey import RSA

print('此模块用于从RSA公钥文件中提取n和e')
pem=input('input a pem file path:')
if pem=='exit()':
    exit()
public = RSA.importKey(open(pem).read())
n = public.n
e = public.e
print("n=\n%s\ne=\n%s"%(n,e))