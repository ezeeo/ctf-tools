#coding=utf-8
#import requests
#version 1.0

import requests
import os

def Is64Windows():
  return 'PROGRAMFILES(X86)' in os.environ

path=os.path.abspath('.')+'/Library/yafu1.34'
exe=''
if Is64Windows():
    exe='yafu-x64.exe'
else:
    exe='yafu-Win32.exe'

print('此程序用于分解RSA公钥,用到了factordb和yafu')
print('factordb : http://factordb.com/index.php')
print('yaml     : http://sourceforge.net/projects/yafu/')
print('ps:yaml 只进行基本factor操作,需要更多操作请自行访问:'+path)


def translate_status(s):
    result=[]
    if s.find('*')!=-1:
        s=s.replace('*','').strip()
        result.insert(0,'Added to database during this request')
    else:s=s.strip()
    if s=='C':
        result.insert(0,'Composite, no factors known')
    elif s=='CF':
        result.insert(0,'Composite, factors known')
    elif s=='FF':
        result.insert(0,'Composite, fully factored')
    elif s=='P':
        result.insert(0,'Definitely prime')
    elif s=='Prp':
        result.insert(0,'Probably prime')
    elif s=='U':
        result.insert(0,'Unknown')
    elif s=='Unit':
        result.insert(0,'	Just for "1"')
    elif s=='N':
        result.insert(0,'This number is not in database (and was not added due to your settings')
    return '\n'.join(result).strip()

def parse_n_for_factordb(n,raw):
    print('search in factordb',end='',flush=True)
    url='http://factordb.com/index.php?query={}'.format(n)
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Referer':'http://factordb.com/index.php',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Upgrade-Insecure-Requests':'0',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'factordb.com'}
    print('.',end='',flush=True)
    try:
        timeout_num=0
        r=''
        while True:
            try:
                print('.',end='',flush=True)
                r=requests.get(url,headers=headers,timeout=5)
                print('.',end='',flush=True)
                break
            except Exception as ex:
                timeout_num+=1
                if timeout_num<=3:
                    print('retry.',end='',flush=True)
                else:
                    print('\nerror:'+str(ex))
                    return False
        print('done',flush=True)
        
        if r.status_code!=200:
            print('net error:r.status_code!=200')
            return False
        r.encoding = 'utf-8'
        ltext=r.text.split('\n')
        for i in range(24):
            ltext.pop(0)
        for i in range(1,len(ltext)+1):
            if ltext[-1].find('More information')==-1:
                ltext.pop(-1)
        if len(ltext)==0:
            print('format error:cannot find start point')
            return False
        if ltext[-1].find('</table>')==-1:
            print('format error:cannot find end point')
            return False
        ltext[0]=ltext[0].replace('</tr>','')
        ltext[-1]=ltext[-1][:ltext[-1].find('</table>')]
        ltext=''.join(ltext)
        ltext=ltext.replace('<tr>','').replace('</tr>','')
        ltext=ltext.split('</td>')
        while '' in ltext:
            ltext.remove('')
        if len(ltext)!=3:
            print('format error:table columns num error')
            return False
        for i in range(len(ltext)):
            ltext[i]=ltext[i].replace('<td>','')
        if len(ltext[0])>4:
            print('format error:status code lenth too long')
            return False
        if ltext[1].find('<a')==-1:
            print('format error:digits parse error')
            return False
        print('------------------status------------------')
        print(translate_status(ltext[0]))
        print('input :'+str(n))
        print('digits:'+ltext[1][:ltext[1].find('<a')])
        print('------------------result------------------')
        raw=ltext
        ltext=ltext[2]
        if ltext.find('</a>')==-1:#寻找目标数字的标签
            print('format error:result format error')
            return False
        #去掉等号左边的部分
        ltext=ltext[ltext.find('</a>'):]
        ltext=ltext[ltext.find('=')+1:].strip()

        ltext=ltext.split('&middot;')
        while '' in ltext:
            ltext.remove('')
        
        for i in range(len(ltext)):#提取行内数据
            if ltext[i].find('<sub>&lt;')!=-1:#删除位数描述
                ltext[i]=ltext[i][:ltext[i].find('<sub>&lt;')]

            ltext[i]=(ltext[i][:ltext[i].find('<')]+ltext[i][ltext[i].find('<font color=')+22:].replace('</font></a>','')).strip()
        #输出
        for t in ltext:
            print(t)
        if raw==True:
            print('------------------rawdata------------------')
            for t in raw:
                print(t)
        print('-------------------------------------------')
        if len(ltext)==2:
            return True
        else:
            return False
    except Exception as ex:
        print('exception:'+str(ex))
        return False
    

def run_yafu(n):
    print('run yafu...')
    os.system('cd '+path+' && '+exe+' factor('+str(n)+')')


def clear_yafu():
    if os.path.exists(path+'/session.log'):
        os.remove(path+'/session.log')
    if os.path.exists(path+'/factor.log'):
        os.remove(path+'/factor.log')
    if os.path.exists(path+'/siqs.dat'):
        os.remove(path+'/siqs.dat')


if __name__ == "__main__":
    clear_yafu()
    n=input('input n:')
    if n=='exit()':
        exit()
    if parse_n_for_factordb(n,False):
        r=input('success find in factordb, Need to continue local search?(y/n)')
        if r!='y' and r!='Y':
            exit()
    run_yafu(n)
    clear_yafu()