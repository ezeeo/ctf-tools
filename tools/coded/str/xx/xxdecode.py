#coding=utf-8
#version 1.1
import sys
if sys.platform=='linux':
    import readline
	
def xxcode(s):
	flag = ''
	ans = ''
	consts = '+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	for i in s:
		for j in range(0,len(consts)):
			if i == consts[j] :
				k = j
		#print k
		num = ''
		while(k>0):
			num += chr(k%2+ord('0'))
			k = k//2
		while(len(num)<6):
			num = num + '0'
		#print num
		num = num[::-1]
		#print num
		flag += num
	#print flag
	while(len(flag)%8!=0):
		flag += '0'
	for i in range(0,len(flag),8):
		x = 0
		for j in range(0,8):
			x *= 2
			if flag[i+j]=='1':
				x += 1
		#print x
		ans += chr(x)
	return ans


if len(sys.argv)==2:
    print(xxcode(sys.argv[1][1:]))
    exit()

print('注意:解码时会忽略长度位,如果不知道长度位是什么,请在开头添加字符h')
if __name__ == '__main__':
    while True:
        data=input('xxdecode>')
        if data=='exit()':
            exit()
        elif data=='':
            continue
        data=data[1:]
        print(xxcode(data))