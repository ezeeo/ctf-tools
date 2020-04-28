#version 1.0
import html,sys
if sys.platform=='linux':
    import readline
def htmlunescape(s):
    return(html.unescape(s))



while True:
    data=input('html_entity_decode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(htmlunescape(data))
