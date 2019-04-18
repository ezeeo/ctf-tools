#coding=utf-8
#version 1.0
table = {
'a':'j','b':'k','c':'l','d':'m','e':'n','f':'o','g':'p','h':'q','i':'r','j':'a','k':'b',
'l':'c','m':'d','n':'e','o':'f','p':'g','q':'h','r':'i','s':'w','t':'x','u':'y','v':'z',
'w':'s','x':'t','y':'u','z':'v','A':'J','B':'K','C':'L','D':'M','E':'N','F':'O','G':'P',
'H':'Q','I':'R','J':'A','K':'B','L':'C','M':'D','N':'E','O':'F','P':'G','Q':'H','R':'I',
'S':'W','T':'X','U':'Y','V':'Z','W':'S','X':'T','Y':'U','Z':'V'
}
def pig(data):
	new = ""
	for ch in data:
		if ch.isalpha():
			new += table[ch]
		else:
			new += ch
	return new
while True:
    data=input('pigpen cipher decode>')
    if data=='exit()':
        exit()
    elif data=='':
        continue
    print(pig(data))