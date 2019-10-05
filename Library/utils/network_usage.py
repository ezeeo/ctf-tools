import os,sys
def check_use_net():
    '''检查是否使用网络(installer.exe)'''
    if not os.path.exists('pytools.bat'):return True
    elif sys.platform!='win32':return False
    else:
        try:
            with open('pytools.bat','r',encoding='utf-8') as f:
                for line in f:
                    if line[:6]=='::net=':
                        if line[6]=='0':return False
                        else:return True
            return True
        except Exception as ex:
            return True