#coding=utf-8
#env .net4.0
#version 1.0

import os

exe=os.path.abspath('.')+'/Library/bftools/bftools.exe'

print('Braintools/bftools/图片隐写,用于解码图片中的brainfuck')
print('ps:核心程序为exe(.NET),本程序仅尝试解码,如需编码请自行运行源目录文件(./Library/bftools/bftools.exe)')


decode_arg=[' decode brainloller "{in_img}" --output "{o_bf}"',' decode braincopter "{in_img}" --output "{o_bf}"']
run_arg=' run {}'
out_file='./output/bftools_output'

#通过有木有生成文件判断是否成功
def decode_exe_run(arg,o_file):
    if os.path.exists(o_file):
        os.remove(o_file)
        print('[-]auto remove '+o_file)
    print('[+]startup decode program...',end='')
    os.system(exe+arg)
    if os.path.exists(o_file) and os.path.getsize(o_file)!=0:
        print('success')
        return True
    else:
        print('filed')
        return False

#运行解码的文件
def run_bf():
    if os.path.exists(out_file+'.result'):
        os.remove(out_file+'.result')
        print('[-]auto remove '+out_file+'.result')
    print('[+]startup run program...',end='')
    os.system(exe+run_arg.format(out_file)+' >'+out_file+'.result')
    if os.path.exists(out_file+'.result'):
        print('success')
        return True
    else:
        print('filed')
        return False

#获取结果
def get_result():
    if not os.path.exists(out_file+'.result'):
        print('[!]resul file not exists')
        return False
    result=''
    f=open(out_file+'.result')
    for line in f:
        result+=line
    f.close()
    return result

#自动解码
def decode(file_path):
    result_list=[]
    if not os.path.exists(file_path): 
        print('[!]input file not exists')
        return False
    for arg in decode_arg:
        if decode_exe_run(arg.format(in_img=file_path,o_bf=out_file),out_file):
            if run_bf():
                result=get_result()
                result_list.append(result)
    if len(result_list)!=0:
        print('[+]success get result:')
        print('-'*60)
        for r in result_list:
            print(r)
            print('-'*60)
    else:
        print('[!]no result')



if __name__ == "__main__":
    path=input('输入图片路径:')
    if path=='exit()':
        exit()
    decode(path)