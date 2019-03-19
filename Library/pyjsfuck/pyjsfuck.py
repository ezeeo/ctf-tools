#!/usr/bin/env python
#import execjs
import execjs
import os
path=os.path.abspath('.')+'\\Library\\pyjsfuck'
class JSFuck():

    def __init__(self):
        f = open(path+'\\jsfuck.js', 'r')
        jsf_code = f.read()
        js = execjs.get()
        #print "Using Engine %s" % js.name
        self.jsf_int = js.compile(jsf_code)
        pass

    def encode(self, code):
        return self.jsf_int.call('JSFuck',code,'1')