#coding: utf-8
'''
@author: prehawk
'''
import re, json, os, time
import login
import urllib2 
from config import *
from os.path import join
from pyquery import PyQuery

class FigureReader(login.Login):
    
    def __init__(self, url):
        super(FigureReader, self).__init__(TEST_USER, TEST_PWD)
        self.figureUrl = url
        
        self.hosthome   = 'http://weibo.com/p/'
        self.hostauto   = self.hosthome + 'aj/mblog/mbloglist?'
        self.pagenum    = 1
        self.filecount  = 0
        
        m = re.search(self.hosthome + '(\d+)/(\w+)\?from=page_(\d+)', url)
        if m:
            self.figureid   = m.group(1)
            self.domain     = m.group(3)
            self.hostweibo  = self.hosthome + self.figureid + '/weibo?' 
            
        else:
            print 'raw url parse error'
            return
              
        self.savedir = '../' + self.figureid
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)
            
        
        #self.start()
        
    
    def start(self):
        
        url = self.hostweibo + 'from=page_' + self.domain + '&mod=TAB'
        self.fetchData(url) 
 
 
    def fetchFollowlist(self):
        url = self.hosthome + self.figureid + '/follow?from=page_' + self.domain
        doc = urllib2.urlopen(url).read() 
        time.sleep(1)
        
        print doc
        #pl.content.followTab.index
        jdiclst = []
        m = re.findall('<script>FM\.view\((.*)\);?</script>', doc)
        if m:
            for i in m:
                jdiclst.append( json.loads(i) ) 
        else:
            print 'raw doc parse error'
        
        for i, jdic in enumerate(jdiclst):
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.content.followTab.index':
                    followlist = jdic['html'] 
                    print followlist 
                        
        pass
    
    
    def saveWeibo(self):
        
        for i in range(2):
            urlauto = self.hostauto + 'domain=' + self.domain + '&pre_page=' + str(self.pagenum) \
                + '&page=' + str(self.pagenum) + '&max_id=0&end_id=' + self.endid + '&count=15&pagebar=' + str(i) \
                + '&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__20&id=' + self.figureid \
                + '&script_uri=/p/' + self.figureid + '/weibo&feed_type=0&from=page_' + self.domain + '&mod=TAB'
            jsondata = urllib2.urlopen(urlauto).read()
            time.sleep(1)
            
            docstr = json.loads(jsondata)['data']
            with open(join(self.savedir, str(self.filecount) ), 'w') as f:
                f.write(docstr.encode('utf-8'))
                self.filecount += 1
            
            if i == 1: # encounter the end of the page
                m = re.search(u'<span>下一页</span></a>', docstr)
                if m: 
                    self.pagenum += 1
                    url = self.hostweibo + \
                        'pids=Pl_Official_LeftProfileFeed__20&is_search=0&visible=0&is_tag=0&profile_ftype=1&page=' \
                        + str(self.pagenum)
                    self.fetchData(url)
                else:
                    print 'the end! ' + str(self.pagenum - 1) + 'pages'
        
        

    def fetchData(self, url):
         
        doc = urllib2.urlopen(url).read()
        time.sleep(1)
        
        
        jdiclst = []
        m = re.findall('<script>FM\.view\((.*)\);?</script>', doc)
        if m:
            for i in m:
                jdiclst.append( json.loads(i) ) 
        else:
            print 'raw doc parse error'
        
        
        for i, jdic in enumerate(jdiclst):
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    head = jdic['html'] 
                    with open(join(self.savedir, 'info'), 'w') as f:
                        f.write(head.encode('utf-8'))
                if jdic['ns'] == 'pl.content.homeFeed.index':
                    weibo = jdic['html']
                    n = re.search('mid=\"(\d+)\"', weibo)
                    if n:
                        self.endid = n.group(1)
                    else:
                        print 'parse error' + str(self.pagenum)
                    with open(join(self.savedir, str(self.filecount) ), 'w') as f:
                        f.write(weibo.encode('utf-8'))
                        self.filecount += 1
  
        
        self.saveWeibo()
        pass 
    


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
    fr = FigureReader('http://weibo.com/p/1035051191258123/home?from=page_103505&mod=TAB#place') 
    fr.fetchFollowlist()
    