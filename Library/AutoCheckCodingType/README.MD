# 编码类型判断
## 更新说明
    大幅强化_MetaEng，现在支持auto_muti_return，增加了解码器，可以一次输入，多次检测得到多个结果  
    例如输入的是hexstream形式的数据，那么在使用auto_muti_return作为装饰器的时候将会使用原始数据运行一遍check()，然后使用hex解码后的数据再运行一遍check()
    这一切都是自动的，只需要添加一个装饰器
    而且你可以自己写解码器(一个输入一个输出)，然后使用add_decode_func添加到解码器列表，这样在以后的检测中都会自动调用(使用了auto_muti_return作为装饰器的情况下)
    
## 使用
    相应目录添加进sys.path后  
    from AutoCheckCodingType import CodingTypeDetector
    即可
    然后创建检测器对象
    de=CodingTypeDetector(report_type='html')
    可设置的参数:
    path='检测引擎所在目录'，可不写，默认为CheckEngines
    report_type=('console','html','other')设置报告模式，可不写，默认为console
    html即为生成html文件，console即为直接输出到控制台
    默认为console

    然后调用Detector(data)方法即可
    
## 注意
    如果检测引擎的输出模式为console，则结果不会出现在报告文件夹内

## 开发说明
    建议检测引擎使用自带的MetaEngine作为父类
    否则的话必须拥有set_data(self,data)方法  

* 必须重写的方法  

    check(self)
    此方法的返回方式由文件开始的注释定义  
    #output 输出方式(normal|file|console)

说明:

    normal:(概率,运行过程的说明,解码后的结果)
    概率范围为0-1，其他两项为字符串，最后返回三元组
    注:如果使用使用了MetaEngine作为父类，并且使用 了_MetaEng里的 auto_return 或者auto_muti_return作为check()的装饰器，那么可以不用在意返回形式，写return即可
    注:这两个装饰器都只适用于normal输入方式
    file:需要返回文件路径标准格式为(第一行0-1,后面的#开头为描述,否则为结果)
    console:输到控制台,返回None即可

* 类的注意点  
如果文件内有多个类的话  
文件内第一个出现的类必须是要直接使用的类

* 开始部分注释的必写项  
#name 检测引擎名称(必须与第一个出现的类名相同)  
#version 版本  
#output 输出方式  
#describe 描述,可以多行  

示例:
```
#encoding=utf-8
#name MetaEngine
#version 1.0
#output normal
#describe 元类
```
