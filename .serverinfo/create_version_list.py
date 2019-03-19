#coding=utf-8

import os
import json

path_t=os.path.abspath('..')+'\\tools'
#path_l=os.path.abspath('..')+'\\Library'

#文件索引
def scan_files(directory,prefix=None,postfix=None):
    files_list=[]
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root,special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root,special_file))
            else:
                files_list.append(os.path.join(root,special_file))

    return files_list

def scan():#扫描存在的文件
    global path_t,path_l
    tool_list=scan_files(path_t,postfix=".py")
    #lib_list=scan_files(path_l)
    version_list=[]
    for tool in tool_list:
        Find=False
        with open(tool,'r',encoding='utf-8') as f:
            for line in f:
                if line=='':
                    break
                if line[0]!='#':
                    break
                elif line[:8]=='#version':
                    version_list.append(line[8:].strip())
                    Find=True
                    break
        if Find==False:
            version_list.append('null')
    
    for i in range(len(tool_list)):
        tool_list[i]=tool_list[i].replace(os.path.abspath('..'),'.')

    return dict(zip(tool_list,version_list))

def writefile(v_dict):
    f=open('./version.txt','w',encoding='utf-8')
    for m,v in v_dict.items():
        f.write(m.replace('\\','/')+' '+v+'\n')
    #f.write(json.dumps(v_dict))
    f.close()


def main():
    version_dict=scan()
    writefile(version_dict)


if __name__ == "__main__":
    main()