'''由于服务器带宽有限，大文件分散下载压力'''
import os
import shutil

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
        for s in self._download_list:
            if os.path.exists(s['filepath']):continue
            print('warnning:leak extra lib...downloading')
            self._call_downloader(self._get_downloader(s['downloader_name']))
            self._move_file(s)
            print('info:success download extra lib '+s['file_name'])