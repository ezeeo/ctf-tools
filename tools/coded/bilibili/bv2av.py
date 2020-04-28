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

def dec(x):
	r=0
	for i in range(6):
		r+=tr[x[s[i]]]*58**i
	return (r-add)^xor


if len(sys.argv)==2:
    data=sys.argv[1].strip()
    if len(data)==12:
        pass
    elif len(data)==10:
        data='BV'+data
    elif len(data)==9:
        data='BV1'+data

    print(dec(data))
    exit(0)

if __name__ == "__main__":
    while 1:
        data=input('convert bv to av>').strip()
        if data=='exit()':
            exit()
        elif data=='':
            continue
        if len(data)==12:
            pass
        elif len(data)==10:
            data='BV'+data
        elif len(data)==9:
            data='BV1'+data
        print(dec(data))