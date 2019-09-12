

import requests


def GET_index():
    url='https://www.ehvip.cn/File/Download?action=download&path=%2Faria2c.jpg'
    headers={
        'Connection':'close',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer':'https',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-User':'?1',
        'Sec-Fetch-Site':'same-origin'
    }
    jar=requests.cookies.RequestsCookieJar()
    jar.set('user_id','3879')
    jar.set('login_key','ced8c11742fc6629e1fa493bd28f889a')
    body={

    }
    r=requests.get(url,cookies=jar,data=body,headers=headers)
    return r



def download():
    res = GET_index()
    res.raise_for_status()
    ariaFile = open('aria2c.exe', 'wb')
    for chunk in res.iter_content(100000):
        ariaFile.write(chunk)
    ariaFile.close()


if __name__ == "__main__":
    download()