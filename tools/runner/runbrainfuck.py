#coding=utf-8
#version 1.0
import os
import sys

path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library\\runbrainfuck'
else:
    path=path+'\\Library\\runbrainfuck'
if not path in sys.path:
    sys.path.append(path)


from PyFuck import PyFuck
from sys import exit

choice = 0

print('Brainfuck是一种极小化的计算机语言，按照”Turing complete（完整图灵机）”思想设计的语言')
print('它的主要设计思路是:用最小的概念实现一种“简单”的语言')
print('BrainF**k 语言只有八种符号，所有的操作都由这八种符号(> < + - . , [ ])的组合来完成')
print('注意:此程序可能有些问题,建议参考runbfd的结果')

print ("Welcome to Michalios13 BrainFuck Interpreter !")

while choice not in ["1", "2"]:
    choice = input("Do you want to :\n1)Run Code ?\n2)Exit ?\nOption : ")

if choice == "1":
    fi = 0
    while fi not in ["1", "2", "3"]:
        fi = input("Do you want to :\n1)Input Program ?\n2)Read File ?\n3)Exit ?\nOption : ")
    
    if fi == "1":
        program  = input("Input Program : ")
    elif fi == "2":
        program  = open(input("Input File: ")).read()
    else:
        exit()

    input_text = input("STDIN : ")
    asize = input("Input Array Size (if blank default size will be used) : ")
    if not asize.isdigit():
        bi = PyFuck(program = program, input_text = input_text)
    else:
        asize = int(abs(int(asize)))
        bi = PyFuck(asize, program, input_text)
    bi.execute()
