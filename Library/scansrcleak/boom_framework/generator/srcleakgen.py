def gen():
    print('[+]load generator...',end='')
    f=open('G:/python/tool_manager/Library/scansrcleak/boom_framework/generator/temp','r',encoding='utf-8')
    passw=f.read()
    f.close()
    passw=set(passw.strip().split('\n'))
    print('done'+' num='+str(len(passw)))
    num=1
    for p in passw:
        #if num%100==0:print('{}|{}'.format(num,len(passw)),end='')
        yield (p,)
        num+=1
        a=yield


if __name__ == "__main__":
    a=list(gen())
    if "'0'" in a:
        print('t')
    else:
        print('f')