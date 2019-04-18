# boom_framework
<font color=red size=3>大量运用exec和eval,不好用那我也没办法。</font>  
<font color=red size=3>注意:win下bp保存的文件编码为gbk!自带转换器将识别gbk下的变量标记符'§'</font>

## 使用方法
    在start.py里更改传入boom_task构造函数的值即可

## 必要参数
    1.请求转换器(可选,位于 converter 目录,自带一个转换bp文件到requests函数的rawtorequests.py)
    必须实现convert(filepath,extra)方法,第二参数当前未使用,自带的转换器支持添加额外变量
    必须返回一个元组(调用形式,code)

    2.设置请求(必须,位于 request 目录,如果设置了转换器,那么会调用转换器进行处理,否则直接当成函数进行加载)

    3.payload生成器(必须,位于 generator 目录,是一个无参函数形式,必要格式如下,示例见nonegen.py)
    yield (x,) #生成的payload必须为元组(成对↓出现)
    a=yield    #必须有接受结果反馈的语句(成对↑出现)

    4.结果分析器(可选,位于 result_analyzer 目录,是一个有两个参数的函数,第一个参数为payload,第二个参数为请求的返回数据,
    示例见noneana.py)

    5.混淆器(可选,位于 obfuscator 目录,是一个有一个参数的函数,传入传出payload,必须是元组,示例见noneobfu.py)

    6.传输器(必须,位于 transmitter 目录,有一个发送请求的类,
    和一个get_transmitter(req_func,gen_func,resultanalyzer_func,obf_func)方法,
    例子见single_thread_http.py(单线程http发送器)和muti_thread_http.py(多线程http发送器))
    get_transmitter接受四个函数的元组(调用形式,code class)(顺序不能错),调用形式类似test({},{}),
    get_transmitter返回的对象必须具有同步的run方法。


## 使用自带模块的示例
    在start.py里设置
```python
    #设置请求转换器  
    c='rawtorequests.py'  
    #设置请求  
    r='ctf.txt'  
    #设置payload生成器  
    g='ctfgen.py'  
    #设置请求结果分析器  
    re='ctfana.py'  
    #设置混淆器  
    o=None  
    #设置传输器  
    t='muti_thread_http.py'  

    b=boom_task(c,r,g,re,o,t)  
    b.run_task()#启动  
```
    然后启动就好

## 注意
    建议生成器,请求(非原始请求),结果分析器,混淆器内只有一个函数且函数头位于文件第一行！

## [地址](https://github.com/ezeeo/boom_framework "boom_framework")