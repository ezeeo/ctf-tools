import sys
import os
import time
import copy
from ScanEngine import ScanEngine
from RunEngine import Runner

#不扫描文件夹和下划线开头的py脚本
#name 检测引擎名称*
#version 版本*
#output 输出方式(normal函数返回(True/False/0-1,evaluate,result)|file输出到文件返回(filename)(第一行状态True/False/0-1,后面的#开头为描述,否则为结果)|console输到控制台返回None)*
#describe 描述,可以多行



class CodingTypeDetector():
    def __init__(self,path=None,report_type='console'):
        if report_type in ('console','html'):
            self.__report_type=report_type
        else:
            self.__report_type='other'
        print('[+]Start init detector on   '+time.asctime(time.localtime(time.time())))
        self.__init_scan_engine(path)
        self.__activation_engines(True)
        print('[+]Success init detector on '+time.asctime(time.localtime(time.time())))
        print('[+]Available Engines num='+str(len(self.__engines)))

    #扫描引擎
    def __init_scan_engine(self,path):
        print('[+]Engines path:'+('CheckEngines' if not path else str(path)))
        if not path:
            self.__scaner=ScanEngine()
        else:
            self.__scaner=ScanEngine(path)
        print('[+]Scan engines...',end='')
        state=self.__scaner.scan()
        if state!=True:
            print('fail')
            print(str(state))
            raise Exception('scan engine path error')
        else:
            print('success')
        print('[+]Detected engine num '+str(len(self.__scaner.engine_list)))
        self.__show_list_errors(self.__scaner.error_list,'scan engine')


    #展示错误
    def __show_list_errors(self,errorlist,process=None):
        if len(errorlist)!=0:
            if not process:
                print('[!]Detected error num='+str(len(errorlist)))
            else:
                print('[!]Detected error in '+str(process)+' num='+str(len(errorlist)))
            state=input('[<]Do you want to view error messages?(y/n)')
            if state=='Y' or state=='y':
                if not process:
                    print('-'*20+'error'+'-'*20)
                else:
                    print('-'*20+str(process)+' error'+'-'*20)
                for e in errorlist:
                    print(e)
                print('-'*60)
            else:
                print('[-]Hiding error information')
        else:
            if not process:
                print('[+]No error ,good')
            else:
                print('[+]No error in {} ,good'.format(process))

    #激活所有检测器
    def __activation_engines(self,immediately_load=(True,False)):
        self.__engines={}#用于执行的引擎file:engine obj
        self.__file_engine_table={}#通过引擎文件名查找引擎信息file:einfo
        print('[+]Start activation engine num='+str(len(self.__scaner.engine_list)))
        error_list=[]
        for e in self.__scaner.engine_list:
            try:
                r=Runner(e,immediately_load)
                self.__engines[e['file']]=r
                self.__file_engine_table[e['file']]=e
            except Exception as ex:
                error_list.append(ex)
        print('[+]Success activation engine num='+str(len(self.__engines)))
        self.__show_list_errors(error_list,'activation engine')

    #检测
    def __detector(self,data):
        assert isinstance(data,str)
        self.__data=data#保存用户输入的数据
        result={}#保存所有检测结果
        errors={}#保存所有检测错误
        for efile,r in self.__engines.items():
            try:
                state=r.setdata(data)
                if state!=True:
                    errors[efile]=state
                    continue
                state=r.run()
                if state!=True:
                    errors[efile]=state
                    continue
                else:
                    if isinstance(r.result,tuple):#标准单结果返回
                        result[efile]=r.result
                    elif isinstance(r.result,dict):#标准多结果返回
                        for k in r.result.keys():
                            result[efile+'_'+k]=r.result[k]
                            self.__file_engine_table[efile+'_'+k]=copy.deepcopy(self.__file_engine_table[efile])
                            self.__file_engine_table[efile+'_'+k]['name']=self.__file_engine_table[efile]['name']+'_'+k
            except Exception as ex:
                errors[efile]=str(ex)
        return result,errors


    def __base_show_report(self,result,errors):
        '''基本的报告展示函数'''
        txt='engine:{}    version:{}    file:{}'
        
        print('-'*30+'report'+'-'*30)
        while len(result)>0:
            maxf=['',0]
            for f,r in result.items():
                if isinstance(r,tuple) and len(r)==3 and (isinstance(r[0],int) or isinstance(r[0],float)):#标准输出
                    if r[0]>maxf[1]:
                        maxf[1]=r[0]
                        maxf[0]=f
            if maxf[0]=='':break#没有标准输出的了
            tmpr=result.pop(maxf[0])
            #展示引擎信息
            print(txt.format(self.__file_engine_table[maxf[0]]['name'],self.__file_engine_table[maxf[0]]['version'],self.__file_engine_table[maxf[0]]['file']))
            print('engine describe:'+self.__file_engine_table[maxf[0]]['describe'])
            #展示结果
            print('Possibility:'+str(tmpr[0]))
            print('result describe:'+str(tmpr[1]))
            print('result:'+str(tmpr[2]))
            print('-'*60)

        #输出非标准内容
        for f,r in result.items():
            #展示引擎信息
            print(txt.format(self.__file_engine_table[f]['name'],self.__file_engine_table[f]['version'],self.__file_engine_table[f]['file']))
            print('engine describe:'+self.__file_engine_table[f]['describe'])
            #展示结果
            print('Possibility:'+str(r[0]))
            print('result describe:'+str(r[1]))
            print('result:'+str(r[2]))
            print('-'*60)

        if len(errors)!=0:
            #展示错误信息
            print('-'*30+'error'+'-'*30)
            for f,e in errors.items():
                #展示引擎信息
                print(txt.format(self.__file_engine_table[f]['name'],self.__file_engine_table[f]['version'],self.__file_engine_table[f]['file']))
                print('engine describe:'+self.__file_engine_table[f]['describe'])
                #展示错误
                print('Error:'+str(e))
                print('-'*60)


    def __html_report_creater(self,engines,result,errors):

        #获取当前时间命名报告文件和报告标题
        filename='report'+time.strftime("[%Y-%m-%d-%H%M%S]", time.localtime())+'.html'
        title='检测报告' 
        subtitle='创建日期：'+time.strftime("[%Y-%m-%d , %H:%M:%S]", time.localtime())
        htmlhead='''<!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8"> 
        <title>Report</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/css/bootstrap.min.css">  
        <script src="https://cdn.staticfile.org/jquery/2.1.1/jquery.min.js"></script>
        <script src="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
        </head>
        <body>
        <div class="container">
        <h2>{title}</h2> 
        <h4>{subtitle}</h5>
        <br>
        <h5></b>输入信息：</b>{data}</h5>
        <table class="table table-hover table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>引擎信息</th>
                    <th>结果信息</th>
                </tr>
            </thead>
            <tbody>'''.format(title=title,subtitle=subtitle,data=self.__data)
        htmlend="</div></body></html>"

        #排序并添加信息到表格中
        maxp=[i[0] for i in result.values()]
        namearr=[i for i in result.keys()]
        tabledata=""
        for num in range(len(maxp)):
            name=namearr.pop(maxp.index(max(maxp)))
            maxp.pop(maxp.index(max(maxp)))
            engine=engines[name]
            res=result[name]

            #对运行信息格式化处理
            enter='<br>'+'&nbsp'*17
            runinfo=res[1].replace('codec',enter+'codec')
            resu=res[2]
            if len(resu)>70 and '\n' not in resu:
                temp=''
                for i in range(len(resu)//70):
                    temp+=resu[i*70:i*70+70]+enter
                resu=temp
            else:
                resu=resu.replace('\n',enter)

            tabledata+='''<tr>
                <td style='text-align:center;vertical-align:middle;'>{num}</td>
                <td><b>名称:</b>&nbsp;&nbsp;{name}<br>
                    <b>版本:</b>&nbsp;&nbsp;{version}<br>
                    <b>文件:</b>&nbsp;&nbsp;{file}<br>
                    <b>描述:</b>&nbsp;&nbsp;{describe}
                </td>
                <td><b>概&nbsp;&nbsp;&nbsp;&nbsp;率:</b>&nbsp;&nbsp;&nbsp;&nbsp;{possibility}<br>
                    <b>运行信息:</b>&nbsp;{runinfo}<br>
                    <b>结&nbsp;&nbsp;&nbsp;&nbsp;果:</b>&nbsp;&nbsp;&nbsp;&nbsp;{result}
                </td>
            </tr>'''.format(num=num+1,name=engine['name'],version=engine['version'],\
                    file=engine['file'],describe=engine['describe'],\
                    possibility=res[0],runinfo=runinfo,result=resu)
        tabledata+='</tbody></table>'

        #如果有错误信息，则添加
        if len(errors)!=0:
            errdata='''<br><br><h3 style='color:red'>错误报告</h3>
            <table class="table table-hover table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>引擎名称</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>'''
            for i in range(len(errors)):
                name=list(errors.keys())[i]
                errdata+='''<tr>
                <td style='text-align:center;vertical-align:middle;'>{num}</td>
                <td>{name}</td>
                <td>{errmsg}</td>
            </tr>'''.format(num=i+1,name=name,errmsg=errors[name])
            errdata+='</tbody></table>'
            tabledata+=errdata
                

        #拼接并将结果写入html
        with open('./Reports/'+filename,'w',encoding='utf-8') as f:
            f.write(htmlhead+tabledata+htmlend)
        if sys.platform=='win32':
            return '.\\Reports\\'+filename
        else:
            return './Reports/'+filename

    #展示扫描结果
    def __show_report(self,result,errors):
        if self.__report_type=='console':
            self.__base_show_report(result,errors)
        elif self.__report_type=='html':
            filename=self.__html_report_creater(self.__file_engine_table,result,errors)
            os.system('"'+filename+'"')
        else:
            state=input('[<]create html report?(y/n)')
            if state=='y' or state=='Y':
                filename=self.__html_report_creater(self.__file_engine_table,result,errors)
            state=input('[<]open html report?(y/n)')
            if state=='y' or state=='Y':
                os.system(filename)
            state=input('[<]show base report?(y/n)')
            if state=='y' or state=='Y':
                self.__base_show_report(result,errors)


    def Detector(self,data):
        try:
            print('[+]Run detector...',end='')
            result,errors=self.__detector(data)
            print('done')
            print('[+]Reporting...')
            self.__show_report(result,errors)
        except Exception as ex:
            print('[!]Exception in Detector->'+str(ex))
        self.__data=''#检测完成即清空输入信息