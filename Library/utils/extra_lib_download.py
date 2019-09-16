'''由于服务器带宽有限，大文件分散下载压力'''
import os
import shutil
import sys
path=os.path.abspath('.')
if 'tools' in path:#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library\\utils'
else:
    path=path+'\\Library\\utils'
if not path in sys.path:
    sys.path.append(path)
from pbar import Pbar

shuld_download_data=[{'file_name':'aria2c.exe','filepath':'./Library/utils/aria2c.exe','downloader_name':'download_aria2'}]


class ext_downloader:
    def __init__(self,download_list):
        self._download_list=download_list


    def _get_downloader(self,downloader_name):
        exec('from Library.utils.extra_downloader.{} import download'.format(downloader_name))
        downloader=eval('download')
        return (downloader_name,downloader)

    def _call_downloader(self,downloader):
        try:
            downloader[1]()
        except Exception as ex:
            print('[!]下载出错->'+downloader[0]+'->'+str(ex))
        

    def _move_file(self,s):
        if os.path.exists(s['file_name']):
            if os.path.exists(s['filepath']):
                os.remove(s['filepath'])
            shutil.move(s['file_name'],s['filepath'])
        elif os.path.exists(s['filepath']):
            return
        else:
            raise Exception('[!]未找到文件')


    def download_ext(self):
        num=len(self._download_list)
        down_num=0
        bar=Pbar(speed=60,bar_fill='#',bar_moving='<=-=>',move_mode='lr')
        bar.start_bar()
        bar.set_rate(None,'checking extra lib...')
        for s in self._download_list:
            if os.path.exists(s['filepath']):
                down_num+=1
                for i in range(int(100/num*down_num)):
                    bar.set_speed((100-i)//3+60)
                    bar.set_rate(i,'checking extra lib...')
                continue
            print('\nwarnning:leak extra lib...downloading'+' '*70)
            bar.set_rate(None,'downloading...')
            
            self._call_downloader(self._get_downloader(s['downloader_name']))
            down_num+=1
            for i in range(int(100/num*down_num)):
                bar.set_rate(i,'checking extra lib...')
            self._move_file(s)
            print('\ninfo:success download extra lib '+s['file_name']+' '*70)
        bar.set_rate(100,'extar lib check pass')
        bar.end_bar()