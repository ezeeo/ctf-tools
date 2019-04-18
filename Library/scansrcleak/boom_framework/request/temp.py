def index(requri):
    import warnings
    warnings.filterwarnings("ignore")
    a='http://116.85.48.104:5023/'
    #print(a+requri)
    r=requests.get(a+requri,allow_redirects=False,verify=False)
    return r
    