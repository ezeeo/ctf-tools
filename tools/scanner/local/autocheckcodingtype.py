#coding=utf-8
#version 1.1

import sys
import os
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):
    path=path.split('tools',maxsplit=1)[0]+'Library/AutoCheckCodingType'
else:
    path=path+'/Library/AutoCheckCodingType'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)


from AutoCheckCodingType import CodingTypeDetector



if __name__ == "__main__":
    de=CodingTypeDetector(report_type='console',path='./Library/AutoCheckCodingType/CheckEngines')
    if len(sys.argv)==2:
        de.Detector(sys.argv[1])
        exit(0)

    while True:
        data=input('CodingTypeDetector>')
        if data=='exit()':exit(0)
        elif data=='':continue
        de.Detector(data)

