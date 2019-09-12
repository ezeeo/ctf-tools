# -*- coding: utf-8 -*-
import json
import sys
import platform
import locale

try:
    import pip
except:
    print('error in install : must have module pip')
    exit()
from pip._internal.utils.misc import get_installed_distributions


mo=get_installed_distributions()
modules=[]
for i in mo:
    modules.append(str(i).split(' ')[0])
print('|'+json.dumps(modules))