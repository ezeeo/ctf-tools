def index(requri):
    import warnings
    warnings.filterwarnings("ignore")
    a='https://lyyousa.cn/'
    #print(a+requri)
    r=requests.get(a+requri,allow_redirects=False,verify=False)
    return r
    