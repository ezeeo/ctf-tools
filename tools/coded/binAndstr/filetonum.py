# -*- coding: utf-8 -*-
#version 1.0
import os

if __name__ == "__main__":
    while True:
        path=input('input file_path:')
        if path=='exit()':
            exit()
        if not os.path.exists(path):
            print('file not exists')
        with open(path,'rb') as f:
            fil=f.read()
        print('---------------little and signed----------------')
        num=int.from_bytes(fil,byteorder='little', signed=True)
        print('int:{}\nhex:{}\noct:{}\n'.format(num,hex(num),oct(num)))
        print('--------------little and no signed--------------')
        num=int.from_bytes(fil,byteorder='little', signed=False)
        print('int:{}\nhex:{}\noct:{}\n'.format(num,hex(num),oct(num)))
        print('-----------------big and signed-----------------')
        num=int.from_bytes(fil,byteorder='big', signed=True)
        print('int:{}\nhex:{}\noct:{}\n'.format(num,hex(num),oct(num)))
        print('---------------big and no signed---------------- Commonly used')
        num=int.from_bytes(fil,byteorder='big', signed=False)
        print('int:{}\nhex:{}\noct:{}\n'.format(num,hex(num),oct(num)))
        