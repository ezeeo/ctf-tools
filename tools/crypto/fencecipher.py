#econding:utf-8
#version 1.1
import sys
if sys.platform=='linux':
    import readline
    
def get_field(elen):
    field=[]
    for i in range(2,elen):
        if(elen%i==0):
            field.append(i)
    return field

def decode(e,elen,field):
    for f in field:
        b = elen // f
        result = {x:'' for x in range(b)}
        for i in range(elen):
            a = i % b
            result.update({a:result[a] + e[i]})
        d = ''
        for i in range(b):
            d = d + result[i]
        print ('分为\t'+str(f)+'\t'+'栏时,解密结果为：  '+d)

print('[+]栅栏密码解密')
e = input('请输入要解密的字符串:')
elen = len(e)
#pen=input('允许填充?(y/n)').strip().lower()=='y'


if len(get_field(elen))==0:
    for i in range(elen):
        field=get_field(elen+i)
        if len(field)!=0:
            print('填充长度:',i)
            decode(e+' '*i,elen+i,field)
            print('-'*30)
else:
    decode(e,elen,get_field(elen))