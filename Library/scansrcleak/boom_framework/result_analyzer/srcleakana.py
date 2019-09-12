def analyzer(payl,resu):
    assert isinstance(payl,tuple)
    import time
    if isinstance(resu,str):
        print('\r[!]'+resu,flush=True)
    else:
        if resu.status_code==404:
            t=int(time.time()*1000)%6
            #print(t)
            if t==0:
                print('\r[  w(ﾟДﾟ)w  ]',end='',flush=True)
                #print('\r[-]',end='',flush=True)
            elif t==1:
                print('\r[ (￣_,￣ )  ]',end='',flush=True)
                #print('\r[\\]',end='',flush=True)
            elif t==2:
                print('\r[ヽ(✿ﾟ▽ﾟ)ノ ]',end='',flush=True)
                #print('\r[|]',end='',flush=True)
            elif t==3:
                print('\r[o(￣ヘ￣o＃)]',end='',flush=True)
                #print('\r[/]',end='',flush=True)
            elif t==4:
                print('\r[  (⊙﹏⊙)  ]',end='',flush=True)
                #pass
            elif t==5:
                print('\r[ (ー`´ー)   ]',end='',flush=True)
                #pass
        else:
            print('\r[>>>>>>>]code='+str(resu.status_code)+'|'+'size='+str(len(resu.text))+':'+str(payl)+':\t'+resu.text.split('\n')[0][:80].strip(),flush=True)
    return