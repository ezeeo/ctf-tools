#coding=utf-8
#version 0.0

'''
操作剪切板：读取剪切板的字符串;清空剪切板;向剪切板中写入字符串（只能写入 ascii 字符）。
win10, python3, 
'''
from ctypes import *
import sys

user32 = windll.user32
kernel32 = windll.kernel32
def get_clipboard():
    user32.OpenClipboard(c_int(0))
    contents = c_char_p(user32.GetClipboardData(c_int(1))).value
    user32.CloseClipboard()
    return contents
def empty_clipboard():
    user32.OpenClipboard(c_int(0))
    user32.EmptyClipboard()
    user32.CloseClipboard()

def set_clipboard(data):
    user32.OpenClipboard(c_int(0))
    user32.EmptyClipboard()
    alloc = kernel32.GlobalAlloc(0x2000, len(bytes(data, encoding='utf_8'))+1)
    # alloc = kernel32.GlobalAlloc(0x2000, len(data)+1)
    lock = kernel32.GlobalLock(alloc)
    cdll.msvcrt.strcpy(c_char_p(lock),bytes(data, encoding='utf_8'))
    # cdll.msvcrt.strcpy(c_char_p(lock), data)
    kernel32.GlobalUnlock(alloc)
    user32.SetClipboardData(c_int(1),alloc)
    user32.CloseClipboard()


if __name__=='__main__':
    if len(sys.argv)==2:
        if sys.argv[1]=='clear' or sys.argv[1]=='c':
            b=get_clipboard()
            if len(b)<=1024:
                print(b)
            empty_clipboard()
            print('clear clipboard success')
    b=get_clipboard()
    empty_clipboard()