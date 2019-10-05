#coding=utf-8
#version 1.0
import sys
import os

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/RSAUtil'
else:
    path=path+'/Library/RSAUtil'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from rsa import *

if __name__ == "__main__":
    p=input('input p:')
    if p=='exit()':
        exit()
    q=input('input q:')
    if q=='exit()':
        exit()
    p=int(p)
    q=int(q)
    e = input('input e:')
    if e=='exit()':
        exit()
    '''生成公钥私钥'''
    e=int(e)
    pubkey, selfkey = gen_key(p, q,e)
    '''需要被加密的信息转化成数字，长度小于秘钥n的长度，如果信息长度大于n的长度，那么分段进行加密，分段解密即可。'''
    while True:
        c = input('input c(num):')
        if c=='exit()':
            exit()
        '''信息加密，m被加密的信息，c是加密后的信息'''
        c=int(c)
        m = decrypt(c, selfkey)
        print(m)