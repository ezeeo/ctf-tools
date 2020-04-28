#version 1.0
from urllib import parse
from urllib import request
import sys
if sys.platform=='linux':
    import readline

while True:
    data=input('urlencode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(parse.quote(data))