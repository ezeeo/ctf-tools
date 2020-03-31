def index(requri):
    import warnings
    warnings.filterwarnings("ignore")
    a='http://h.fox-f.top/'
    #print(a+requri)
    r=requests.get(a+requri,allow_redirects=False,verify=False)
    return r
    