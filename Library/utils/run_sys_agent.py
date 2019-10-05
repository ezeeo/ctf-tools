def agent_system(s):
    '''运行指定cmd命令,获取返回code和结果'''
    s=[i.strip() for i in s.split(' ')]
    while '' in s:
        s.remove('')
    #import locale
    import subprocess
    #if locale.getdefaultlocale()[1]=='cp936':
    #    recode=True
    #else:
    #    recode=False

    subs=subprocess.Popen(s,bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    subs.stdin.close()
    subs.wait()

    result=''
    for line in subs.stdout.readlines():
        ##blow for pycharm and cygwin show chinese#
        output = line.decode('utf-8')
        result+=output
    if len(result)>1:
        result=result[:-1]

    return (subs.returncode,result)


if __name__ == "__main__":
    code,result=agent_system('G:\\python\\tool_manager\\installer.exe serverinfo')
    print(code,result)