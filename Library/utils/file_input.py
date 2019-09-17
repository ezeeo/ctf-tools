#读取文件到buffer
filereadmode = {
    "none":lambda s:s,
    "without_newline":lambda s:s.replace('\n','').replace('\r',''),
    "without_space":lambda s:s.replace(' ',''),
    "without_all":lambda s:s.replace('\n','').replace('\r','').replace('\n','').replace(' ','')
}

def inputfile(path_mode):
    buffer=''
    arg=path_mode.split(' ')
    path=arg[0]
    mode=''
    if path=='':
        print('>>>no input path<<<')
        return
    if len(arg)>2:
        print('>>>too more args<<<')
        return
    elif len(arg)==2:
        mode=arg[1]
    try:
        f=open(path,'r',encoding='UTF-8')
        if mode in filereadmode:
            buffer=filereadmode[mode](f.read())
        else:
            buffer=f.read()
        f.close()
    except:
        print('>>>a except in inputfile()<<<')
        return
    return buffer
