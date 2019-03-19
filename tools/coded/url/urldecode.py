#version 1.0
from urllib import parse
from urllib import request

while True:
    data=input('urldecode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(parse.unquote(data))