def autokbex_input(*args,catch_kbex=True,handle_kbex=lambda :exit(0),exitsign='exit()',handle_exitsign=lambda :exit(0),**kwargs):
    '''自动处理不限量次数的KeyboardInterrupt.内容输出使用print且默认不换行

    :param catch_kbex: 是否要在内部自动处理KeyboardInterrupt和EOFError
    :type catch_kbex: bool
    :param handle_kbex: 在用户触发kbex并且决定不继续程序的时候被调用的方法
    :type handle_kbex: callable
    :param exitsign: 触发handle_exitsign的输入字符串
    :type exitsign: any
    :param handle_exitsign:输入字符串.strip()等于exitsign时被调用的方法
    :type handle_exitsign: callable
    '''
    if (handle_kbex and not callable(handle_kbex)) or not callable(handle_exitsign):
        raise Exception('init process error')
    try:
        if 'end' not in kwargs:
            kwargs['end']=''
        print(*args,**kwargs)
        data=input()
    except (KeyboardInterrupt,EOFError) as ex:
        if catch_kbex:
            if not _continue_input():
                return handle_kbex()
            else:
                return autokbex_input(*args,catch_kbex=catch_kbex,handle_kbex=handle_kbex,exitsign=exitsign,handle_exitsign=handle_exitsign,**kwargs)
        else:
            raise ex
    if data.strip()==exitsign:
        return handle_exitsign()
    return data

def _continue_input():
    try:
        data=input('\r[!]continue?(y/n)').strip().lower()
    except (KeyboardInterrupt,EOFError) as ex:
        return _continue_input()
    return data=='y'


if __name__ == "__main__":

    print(autokbex_input('tt','tt>',handle_kbex=lambda :'aaa',handle_exitsign=lambda:'bbb'))
    #print(_exit_input())