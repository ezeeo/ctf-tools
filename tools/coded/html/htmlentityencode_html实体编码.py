#version 1.0
import html,sys
if sys.platform=='linux':
    import readline
def htmlescape(s):
    s=html.escape(s)
    return s





while True:
    data=input('html_entity_encode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(htmlescape(data))
