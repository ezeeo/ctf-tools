#coding=utf-8
#version 1.0
import os
import json

def read_req(file_path):
    first_line=''#最终结果
    uri=''#资源路径
    url=''#请求地址
    req_method=''#请求方法
    header={}#请求头
    cookies={}#cookies
    req_body={}#请求体
    req_methods={'GET':'get','POST':'post','PUT':'put','DELETE':'delete','HEAD':'head','OPTIONS':'options','TRACE':'trace','CONNECT':'connect'}
    if not os.path.exists(file_path):
        print('[!]file error:file not exists')
        return False
    
    txt=''#保存读入的文件
    with open(file_path,'r') as f:
        txt=f.read().split('\n')
    
    all_rows_num=len(txt)
    processed_rows_num=0
    txt_dic=dict(zip(txt,range(1,len(txt)+1)))#保存行数信息

    print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')
    #第一行必须是规定格式
    line=txt.pop(0)
    line=line.split(' ')
    #检查格式
    if len(line)!=3:#
        print("\n[!]format error in line 1:' ' num must 2, but now is {}".format(len(line)-1))
        return False
    if line[2]!='HTTP/1.1':#检查请求版本
        print('\n[!]Unsupported requests in line 1:must HTTP/1.1, but now is {}'.format(line[2]))
        return False
    if line[0] not in req_methods.keys():
        print('\n[!]Unsupported method in line 1:must HTTP/1.1 method, but now is {}'.format(line[0]))
        return False
    #第一行验证通过
    name=line[1].split('/')[-1]#生成函数名
    if name=='':
        name='index'
    first_line='def '+line[0]+'_'+name+'():'#函数头创建
    uri=line[1]
    req_method=req_methods[line[0]]

    processed_rows_num+=1
    print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')

    #通过Host创建出url
    for raw_line in txt:
        if raw_line[:4]=='Host':
            line=raw_line.split(':')
            #检查格式
            if len(line)!=2:
                print("\n[!]format error in line {}:':' num must 1, but now is {}".format(txt_dic[raw_line],len(line)-1))
                return False
            url=line[1].strip()+uri
            txt.remove(raw_line)
            break
    if url=='':#创建url失败
        print("\n[!]Missing data:must have Host")
        return False
    if ''.join(txt).find('https://')!=-1:
        url='https://'+url
    else:
        url='http://'+url

    processed_rows_num+=1
    print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')
    
    #创建请求头
    num=0
    while num!=len(txt)-1:
        raw_line=txt[num]
        if raw_line[:6]=='Cookie' or (len(raw_line.split(': '))!=2 and raw_line.find('"')==-1):
            num+=1
            continue
        line=raw_line.split(': ')
        header[line[0]]=line[1].strip()

        txt.remove(raw_line)
        processed_rows_num+=1
        print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')

    #创建cookies
    for raw_line in txt:
        if raw_line[:6]=='Cookie':
            line=raw_line[7:].strip().split(';')
            for c in line:
                if c.find('"')!=-1:
                    tmp=c.split('=')
                    cc[0]=tmp[0]
                    cc[1]='='.join(tmp[1:])
                else:
                    cc=c.split('=')
                if len(cc)!=2:
                    print("\n[!]format error in line {}:cookie format error, too more '='".format(txt_dic[raw_line]))
                    return False
                cookies[cc[0].strip()]=cc[1].strip()
            
            txt.remove(raw_line)
            processed_rows_num+=1
            print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')
    
    #删除空行
    while '' in txt:
        txt.remove('')
        processed_rows_num+=1
        print('\r{}|{} processing'.format(processed_rows_num,all_rows_num)+' '*100,end='')

    if len(txt)>1:
        print('\n[!]format error:request body must in one line, but now is {}'.format(len(txt)))
        print("[!]Data that cannot be processed:"+str(txt))
        return False
    #创建请求体
    elif len(txt)==1:
        raw_line=txt[0].strip()
        jload_ok=False
        if raw_line[0]=='{' and raw_line[-1]=='}':
            try:
                j_line=json.loads(raw_line)
                jload_ok=True
            except Exception as ex:
                print('\n[-]fromat warn in line {}:Suspected json but load fail'.format(txt_dic[txt[0]]))
                print('[+]try normal parse...')
        if jload_ok:
            for key in j_line:
                req_body[key]=j_line[key]
        else:
            raw_line=raw_line.split('&')
            for line in raw_line:
                p=line.split('=')
                if len(p)!=2:
                    print("\n[!]fromat error in line {}:request body '=' num error in {}".format(txt_dic[txt[0]],line))
                    return False
                req_body[p[0].strip()]=p[1].strip()

        processed_rows_num+=1
        if processed_rows_num!=all_rows_num:
            print('\n[-]file warn:Unexpected number of file lines,may missing something')
        print('\r{}|{} processing'.format(all_rows_num,all_rows_num)+' done')
        #返回读取结果
        return (first_line,url,req_method,header,cookies,req_body)


def create_method(first_line,url,req_method,header,cookies,req_body):
    txt='''{first_line}
    url='{url}'
    headers={{ 
{headers}
    }}
    jar=requests.cookies.RequestsCookieJar()
{set}
    body={{
{body}
    }}
    r=requests.{req_method}(url,cookies=jar,data=body,headers=headers)
    return r'''
    
    line="        '{}':'{}',"
    headers=[]
    for l in header:
        headers.append(line.format(l,header[l]))
    if headers!=[]:
        headers[-1]=headers[-1][:-1]
    
    line="        '{}':'{}',"
    body=[]
    for l in req_body:
        body.append(line.format(l,req_body[l]))
    if body!=[]:
        body[-1]=body[-1][:-1]

    line="    jar.set('{}','{}')"
    jar_set=[]
    for l in cookies:
        jar_set.append(line.format(l,cookies[l]))

    return txt.format(first_line=first_line,url=url,req_method=req_method,headers='\n'.join(headers),body='\n'.join(body),set='\n'.join(jar_set))

if __name__ == "__main__":
    path=input('input bp request file:')
    res=read_req(path)
    print('-'*50)
    if res!=False:
        first_line,url,req_method,header,cookies,req_body=res
        print(create_method(first_line,url,req_method,header,cookies,req_body))
    else:
        print('error')