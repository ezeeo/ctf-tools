#执行模式
def exec_mode():
    #exec('global buffer')
    while True:
        data=input('exec>')
        if data=='exit()':
            return
        elif data=='':
            continue
        else:
            if data.find('=')==-1 or data.find('==')!=-1:
                data='print('+data+')'
                pass
            try:
                exec(data.replace('$','buffer'))
            except Exception as ex:
                print('>>>Illegal code<<<')