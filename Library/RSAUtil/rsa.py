# -*- coding: utf-8 -*-
from gcd import ext_gcd
from exponentiation import exp_mode
import time

# 生成公钥私钥，p、q为两个超大质数
def gen_key(p, q,e):
    n = p * q
    fy = (p - 1) * (q - 1)      # 计算与n互质的整数个数 欧拉函数
    #e = 3889                    # 选取e   一般选取65537
    # generate d
    a = e
    b = fy
    r, x, y = ext_gcd(a, b)
    print(x)   # 计算出的x不能是负数，如果是负数，说明p、q、e选取失败，一般情况下e选取65537
    d = x
    # 返回：   公钥     私钥
    return    (n, e), (n, d)
    
# 加密 m是被加密的信息 加密成为c
def encrypt(m, pubkey):
    n = pubkey[0]
    e = pubkey[1]
    
    c = exp_mode(m, e, n)
    return c

# 解密 c是密文，解密为明文m
def decrypt(c, selfkey):
    n = selfkey[0]
    d = selfkey[1]
    
    m = exp_mode(c, d, n)
    return m
    