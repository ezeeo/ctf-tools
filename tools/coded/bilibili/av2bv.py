#coding=utf-8
#version 1.0
import sys
if sys.platform=='linux':
    import readline
    
table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr={}
for i in range(58):
	tr[table[i]]=i
s=[11,10,3,8,4,6]
xor=177451812
add=8728348608


def enc(x):
	x=(x^xor)+add
	r=list('BV1  4 1 7  ')
	for i in range(6):
		r[s[i]]=table[x//58**i%58]
	return ''.join(r)




if len(sys.argv)==2:
    data=sys.argv[1].strip().lower()
    if data.startswith('av'):
        data=data[2:]
    data=int(data)
    print(enc(data))
    exit(0)

if __name__ == "__main__":
    while 1:
        data=input('convert av to bv>').strip().lower()
        if data=='exit()':
            exit()
        elif data=='':
            continue
        if data.startswith('av'):
            data=data[2:]
        data=int(data)
        print(enc(data))