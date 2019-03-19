# -*- coding: utf-8 -*-

# 求两个数字的最大公约数（欧几里得算法）
def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

'''
扩展欧几里的算法
计算 ax + by = 1中的x与y的整数解（a与b互质）
'''
def ext_gcd(a, b):
    if b == 0:
        x1 = 1
        y1 = 0
        x = x1
        y = y1
        r = a
        return r, x, y
    else:
        r, x1, y1 = ext_gcd(b, a % b)
        x = y1
        y = x1 - a // b * y1
        return r, x, y
