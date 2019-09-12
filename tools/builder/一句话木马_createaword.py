#coding=utf-8
#version 1.1
import random
import base64
import sys
import os
path=os.path.abspath('.')+'\\Library\\createaword'
if not path in sys.path:
    sys.path.append(path)
from phpcreater import *

def main():
    result=''
    print('选择语言:')
    print('1.php')
    
    lan=input()
    if lan=='exit()':
        exit()
    elif lan=='':
        return

    if lan=='1':
        print('选择模式:')
        print('1.php_base')
        print('2.php_array_confusion1')
        print('3.php_array_confusion2')
        print('4.php_rot13')
        print('5.php_func_encode')
        print('6.php_base64_confusion')
        print('7.php_muti_base64')
        print('8.php_word_coded')
        print('9.php_note_confusion')
        print('10.php_str_splicing')
        print('11.php_免杀')
        print('12.php_间接写马')
        print('13.php_无?马')
        print('14.php_过狗')
        lan=input()
        if lan=='12':
            result=php_jianjiexxiema()
        else:
            pwd=input('输入连接密码:')
            if lan=='5':
                chouse=input('输入混淆选择(1-3)为空表示随机:')
                result=php_func_encode(pwd,chouse)
            elif lan=='7':
                num=input('次数:')
                result=php_muti_base64(pwd,num)
            else:
                if lan=='1':
                    result=php_base(pwd)
                elif lan=='2':
                    result=php_array_confusion1(pwd)
                elif lan=='3':
                    result=php_array_confusion2(pwd)
                elif lan=='4':
                    result=php_rot13(pwd)
                elif lan=='6':
                    result=php_base64_confusion(pwd)
                elif lan=='8':
                    result=php_word_coded(pwd)
                elif lan=='9':
                    result=php_note_confusion(pwd)
                elif lan=='10':
                    result=php_str_splicing(pwd)
                elif lan=='11':
                    result=php_miansha(pwd)
                elif lan=='13':
                    result=php_no_wenhao(pwd)
                elif lan=='14':
                    result=php_guogou(pwd)
    elif lan=='2':
        pass
    print(result)

if __name__ == "__main__":
    while True:
        main()