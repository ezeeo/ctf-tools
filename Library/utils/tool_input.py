def withexit_input(*args, **kwargs):
    data=input(*args,**kwargs).strip()
    if data=='exit()':exit(0)
    return data