import os

class Aria2_Downloader:
    def __init__(self,dir_path,t_num=6):
        self._aria2c='./Library/utils/aria2c.exe'
        if not self._check_aria2c():
            raise Exception('[!]错误:未找到 extra lib aria2c')
        self._t_num=t_num
        self._dir_path=dir_path

    def _check_aria2c(self):
        return os.path.exists(self._aria2c)



    def _create_args(self,url,file_name):
        return '-d {} -x {} --check-certificate=false {} -o {}'.format(self._dir_path,self._t_num,url,file_name)

    def download(self,url,file_name):
        fd=self._run_aria(self._create_args(url,file_name))
        if fd!=0:
            raise Exception('[!]下载出错')




    def _run_aria(self,args):
        #input('"'+self._aria2c+'" '+args)
        return os.system('""'+self._aria2c+'" '+args+'"')