def index(requri):
    import warnings
    warnings.filterwarnings("ignore")
    a='http://47.244.178.135:9999/'
    #print(a+requri)
    r=requests.get(a+requri,allow_redirects=False,verify=False)
    return r
    