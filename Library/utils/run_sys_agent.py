from auto_decoder import auto_decode
import subprocess
def agent_system(s,sp=' ',return_error=False):
    '''运行指定cmd命令,获取返回code和结果'''
    s=[i.strip() for i in s.split(sp)]
    while '' in s:
        s.remove('')
    #import locale
    
    #if locale.getdefaultlocale()[1]=='cp936':
    #    recode=True
    #else:
    #    recode=False
    if len(s)==0:return None
    
    #s[0]='set PYTHONIOENCODING=UTF-8&&'+s[0] 

    subs=subprocess.Popen(s,bufsize=0,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    subs.stdin.close()
    subs.wait()

    result=''
    errors=''
    for line in subs.stdout.readlines():
        ##blow for pycharm and cygwin show chinese#

        output = auto_decode(line)
        result+=output
    for line in subs.stderr.readlines():
        ##blow for pycharm and cygwin show chinese#

        output = auto_decode(line)
        errors+=output
    if return_error:
        return (subs.returncode,result,errors)
    else:
        return (subs.returncode,result)

if __name__ == "__main__":
    code,result=agent_system('G:\\python\\tool_manager\\installer.exe serverinfo')
    print(code,result)