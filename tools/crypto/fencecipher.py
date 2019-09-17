#econding:utf-8
#version 1.0

print('[+]栅栏密码解密')
e = input('请输入要解密的字符串:')
elen = len(e)
field=[]
for i in range(2,elen):
    if(elen%i==0):
        field.append(i)

for f in field:
    b = elen // f
    result = {x:'' for x in range(b)}
    for i in range(elen):
        a = i % b
        result.update({a:result[a] + e[i]})
    d = ''
    for i in range(b):
        d = d + result[i]
    print ('分为\t'+str(f)+'\t'+'栏时，解密结果为：  '+d)