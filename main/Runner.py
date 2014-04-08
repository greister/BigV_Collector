#coding: utf-8
'''
@author: prehawk
'''
import re, json
import login
import urllib2 
from config import *

class FigureReader(login.Login):
    
    def __init__(self, url):
        super(FigureReader, self).__init__(TEST_USER, TEST_PWD)
        self.figureUrl = url
        
        
        m = re.search('/weibo.com/p/(\d+)/(\w+)\?from=page_(\d+)', url)
        if m:
            self.figureid   = m.group(1)
            self.tag        = m.group(2)
            self.domain     = m.group(3)
        else:
            print 'raw url parse error'
              
        self.weiboUrl = 'http://weibo.com/p/' + self.figureid + '/weibo?from=page_' + self.domain + '&mod=TAB' 
        doc = urllib2.urlopen(self.weiboUrl).read()
        
        jdic = []
        m = re.findall('<script>FM\.view\((.*)\);?</script>', doc)
        if m:
            for i in m:
                jdic.append( json.loads(i) )
                
            pass
            
            
        else:
            print 'raw doc parse error'
        
        pass
            
        

    def scrapIt(self):
        
        doc = urllib2.urlopen(TEST_URL).read()
        return doc
    

class WeiboItem(object):
    pass



def transformer():
    
    with open('../a.txt', 'r') as a:
        with open('../b.txt', 'w') as b:
            plain = a.read()
            unicodeText = plain.decode('unicode_escape')
            utf8Text = unicodeText.encode('utf-8')
            b.write(utf8Text)

if __name__ == '__main__':
    fr = FigureReader(TEST_URL)
    #print fr.scrapIt()
    
    