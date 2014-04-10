#coding: utf-8
'''
@author: prehawk
'''
import re, json, os, time
import login
import urllib2 
import config 
from pyquery import PyQuery

class Controller(login.Login):
    
    def __init__(self):
        super(Controller, self).__init__(config.TEST_USER, config.TEST_PWD)
        
    def start(self):
        self.parseWeiboLst(2862441992)
        
        
    def parseWeiboLst(self, uid):
        fd = '../BigVs/' + str(uid)
        if os.path.exists(fd): 
            with open( '../BigVs/' + str(uid), 'r' ) as f:
                rawdoc = f.read()
            
            d = PyQuery(rawdoc.decode('utf-8')) 
            
            follow = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'follow')
            fans = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'fans')
            weibo = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'weibo')  
            
            name = d('span').filter('.name').text()
            verify = d('.pf_verified_info').contents()[0]
            intro = d('.pf_intro').text()
            
            tags = []
            for i in d('.layer_menulist_tags').items('a'):
                tags.append( i.text() )
            
        
        else:
            print 'file not exists'
        
        
    def writeWeiboLst(self, uid):

        wr = WeiboReader(uid)
        ret = wr.getWeiboLst()
        
        
        savedir = '../BigVs/'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
            
        with open( savedir + str(ret[0]), 'w' ) as f:
            f.write(ret[1].encode('utf-8') + '\n\n')
            f.write(ret[2].encode('utf-8') )
    
    def writeFollowLst(self):
         
        followSet = set()
        with open('../followlist', 'r') as f: 
            for line in f.readlines():
                followSet.add( line ) 
 
        layerSet = followSet
        for uid in layerSet:
            
            newSet = set( FollowReader(uid).getFollowLst() )
            writeSet = newSet - followSet
            followSet.union(newSet)  
        
            with open('../followlist', 'a') as f:
                for w in writeSet:
                    f.write(w + '\n')

class WeiboFigure(object):
    
    def __init__(self, uid):         
       
        self.hosthome   = 'http://weibo.com/'
        self.hostauto   = self.hosthome + 'p/aj/mblog/mbloglist?'
        self.pagenum    = 1
        self.filecount  = 0
        self.uid        = uid
        
        url = self.hosthome + 'u/' + str(uid)
        doc = urllib2.urlopen(url).read().decode('string_escape') 
        
        m = re.search(r'href=\"\\/p\\/(\d+)\\/(\w+)\?from=page_(\d+)', doc)
        if m:
            self.fulluid    = m.group(1)
            self.domain     = m.group(3)
            self.hostweibo  = self.hosthome + 'p/' + self.fulluid + '/weibo?from=page_'  + self.domain + '&mod=TAB'
            self.hostfollow = self.hosthome + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=1'
        else:
            print 'Init: Alias reference page parse error'
            return

        

class FollowReader(WeiboFigure):
    
    def __init__(self, uid):
        super(FollowReader, self).__init__(uid)
        self.followLst = []
        
    def getFollowLst(self):
        self._fetchlist( self.hostfollow ) 
        return self.followLst
        
    def _fetchlist(self, url):
        doc = urllib2.urlopen(url).read().decode('string_escape')
        time.sleep(0.5) 
          
        m = re.findall('<div class=\"name\">\s+(.*)\s+(.*)', doc)
        if m:
            for i in m: 
                if re.search('class=\"W_ico16 approve\"', i[1]):
                    userid = re.search('usercard=\"id=(\d+)\"', i[0]).group(1)
                    self.followLst.append(userid)
                else:
                    continue 

        self.pagenum += 1
        if re.search(r'<span>下一页<\\/span><\\/a>', doc):
            url = self.hosthome + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=' \
                + str(self.pagenum)
            self._fetchlist(url)
        

class WeiboReader(WeiboFigure):
    
    def __init__(self, uid):         
        super(WeiboReader, self).__init__(uid) 

#         self.savedir = '../BigVs' + self.fulluid
#         if not os.path.exists(self.savedir):
#             os.mkdir(self.savedir) 
            
        self.phase      = 0
        self.nextUrl    = self.hostweibo 
        self.weiboLst   = [self.uid, '', '']
        
    def getWeiboLst(self):
    
        while self.phase >= 0:
            
            self.data = urllib2.urlopen(self.nextUrl).read()
            time.sleep(config.TIME_GAP)
            
            if self.phase == 0:
                self.fetchNext1()
            else:
                self.fetchNext2(self.phase)
        
        
        return self.weiboLst
            
  
    def makeAutoLink(self, num):
        return self.hostauto + 'domain=' + self.domain + '&pre_page=' + str(self.pagenum) \
                + '&page=' + str(self.pagenum) + '&max_id=0&end_id=' + self.endid + '&count=15&pagebar=' + str(num) \
                + '&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__20&id=' + self.fulluid \
                + '&script_uri=/p/' + self.fulluid + '/weibo&feed_type=0&from=page_' + self.domain + '&mod=TAB'
                
    def fetchNext2(self, phase):

        docstr = json.loads(self.data)['data']
        self.weiboLst[2] += docstr
        
        
#         with open(join(self.savedir, str(self.filecount) ), 'w') as f:
#             f.write(docstr.encode('utf-8'))
#             self.filecount += 1
        
        if phase == 2: # encounter the end of the page 
            if re.search(u'<span>下一页</span></a>', docstr):  # has next page
                self.pagenum += 1
                self.phase = 0 
                self.nextUrl = self.hostweibo + \
                    'pids=Pl_Official_LeftProfileFeed__20&is_search=0&visible=0&is_tag=0&profile_ftype=1&page=' \
                    + str(self.pagenum) 
            else: # whole loop end
                print 'the end! ' + str(self.pagenum - 1) + 'pages'
                self.phase = -1
                return
        else:
            self.phase = 2
            self.nextUrl = self.makeAutoLink(1) 

    def fetchNext1(self):
                 
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', self.data)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print 'fetchNext1: raw doc parse error'
        
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    head = jdic['html'] 
                    self.weiboLst[1] = head
#                     with open(join(self.savedir, 'info'), 'w') as f:
#                         f.write(head.encode('utf-8'))
                if jdic['ns'] == 'pl.content.homeFeed.index':
                    weibo = jdic['html']
                    n = re.search('mid=\"(\d+)\"', weibo)
                    if n:
                        self.endid = n.group(1)
                    else:
                        print 'parse error' + str(self.pagenum)
                        
                    self.weiboLst[2] += weibo
                    
#                     with open(join(self.savedir, str(self.filecount) ), 'w') as f:
#                         f.write(weibo.encode('utf-8'))
#                         self.filecount += 1
  
        self.phase = 1
        self.nextUrl = self.makeAutoLink(0)
        
    
  
def transformer():
    
    with open('../a.txt', 'r') as a:
        with open('../b.txt', 'w') as b:
            plain = a.read()
            unicodeText = plain.decode('unicode_escape')
            utf8Text = unicodeText.encode('utf-8')
            b.write(utf8Text)

if __name__ == '__main__':
    c = Controller()
    c.start()