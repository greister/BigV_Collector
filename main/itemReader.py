#coding:utf-8

'''
@author: admin
'''


import re 
import time
import json
import config
import urllib2

time_retry = 0
 

 
# include basic weibo info.
class Page(object):
    
    def __init__(self):   
        self.isComplete   = False                 # whether this page is info isComplete
        
        self.host   = 'http://weibo.com/'
        
         

    def _complete(self, uid):
        if not self.isComplete:
            if unicode(uid).isnumeric():
                url = self.host + 'u/' + str(uid)
            else:
                url = self.host + str(uid)
            doc = self.getDoc(url).decode('string_escape')
            
            m = re.search(r'href=\"\\/p\\/(\d+)\\/(\w+)\?from=page_(\d+)', doc)
            if m:
                self.fulluid    = m.group(1)
                self.domain     = m.group(3)                        # getDoc for domain id
                self.uid        = self.fulluid[len(self.domain):]   # fulluid = domain + uid
            else:
                raise Exception('Your visit may be block by Sina!')
            self.isComplete = True

    def finishFetching(self):
        self.isComplete = False


    def getUID(self, uid):
        self._complete(uid)
        return self.uid

    # simple retry machanism retry by 0.5, 1.5, 2.5, 3.5, 4.5 sec. 
    def getDoc(self, url):
        global time_retry
        time.sleep(config.TIME_GAP + time_retry)
        try:
            ret = urllib2.urlopen(url).read()
            time_retry = 0
            return ret
        except:
            if time_retry < 5:
                time_retry += 1
                return self.getDoc(url)
            else:
                time_retry = 0
                raise

    def _make_timestamp(self):
        return str( int(time.time()*1000) )
    
    #depricate, indepent
    def makeUrl_comment2(self, mid, uid):
        return self.host + 'aj/comment/small?_wv=5&act=list&mid=' + \
                str(mid) + '&uid=' + str(uid) + '&isMain=true&ouid=' + str(uid)
    
    def makeUrl_hostfollow(self, uid):
        self._complete(uid)
        return self.host + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=1'
    
    def makeUrl_hostweibo(self, uid):
        self._complete(uid)
        return self.host + 'p/' + self.fulluid + '/weibo?from=page_'  + self.domain + '&mod=TAB'
    
    def makeUrl_hostinfo(self, uid):
        self._complete(uid)
        return self.host + 'p/' + self.fulluid + '/info?from=page_'   + self.domain + '&mod=TAB'
    
    # need isComplete
    def makeUrl_autoload(self, uid, pagenum, endid, num): 
        self._complete(uid)
        return self.host + 'p/aj/mblog/mbloglist?domain=' + self.domain + '&pre_page=' + str(pagenum) \
                + '&page=' + str(pagenum) + '&max_id=0&end_id=' + str(endid) + '&count=15&pagebar=' + str(num) \
                + '&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__20&id=' + self.fulluid \
                + '&script_uri=/p/' + self.fulluid + '/weibo&feed_type=0&from=page_' + self.domain + '&mod=TAB' \
                + '&_rnd=' + self._make_timestamp()
    
    # indepent
    def makeUrl_manload(self, uid, pagenum):
        w = self.makeUrl_hostweibo(uid)
        return  w + 'pids=Pl_Official_LeftProfileFeed__20&is_search=0&visible=0&is_tag=0&profile_ftype=1&page=' \
                    + str(pagenum) + '&_rnd=' + self._make_timestamp()
    
    # indepent
    def makeUrl_comment(self, pagenum, mid, maxid):
        return self.host + 'aj/comment/big?_wv=5&id=' + str(mid) \
                + '&max_id=' + str(maxid)+ '&page=' + str(pagenum) + '&_rnd=' + self._make_timestamp()
     
    # need isComplete           
    def makeUrl_follow(self, uid, pagenum):
        self._comlete(uid)
        return self.host + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=' \
                + str(pagenum) + '&_rnd=' + self._make_timestamp()


class WeiboPage(Page):
    

    def __init__(self, arg):
        super(WeiboPage, self).__init__()
        self.data        = ''
        self.phase       = 0
        self.pagenum     = 1
        self.uid         = arg
        self.endid       = 0
        self.nextUrl     = self.makeUrl_hostweibo(arg)
        
    def __iter__(self):
        return self
    
    
    def getUID(self):
        return self.uid
    
    #long long request time, generate self.rawPage
    def next(self):  

        while self.phase >= 0: 
            self.data = self.getDoc(self.nextUrl)
            
            if self.phase == 0:
                return self._fetch_manload()
            else:
                return self._fetch_autoload()
        raise StopIteration()
 
 
    def _fetch_autoload(self):

        docstr = json.loads(self.data)['data'] 
          
        if self.phase == 2: # encounter the end of the page 
            if re.search(u'<span>下一页</span></a>', docstr):  # has next page
                self.pagenum += 1
                self.phase = 0
                self.nextUrl = self.makeUrl_manload(self.uid, self.pagenum) 
            else: # whole loop end
                print 'the end! ' + str(self.pagenum) + 'pages'
                self.phase = -1 
        else:
            self.phase = 2
            self.nextUrl = self.makeUrl_autoload(self.uid, self.pagenum, self.endid, 1)
        return docstr

    def _fetch_manload(self):
                  
        weibo = ''
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', self.data)
        if scripts:
            for i in scripts:
                jsondata = json.loads(i)
                if 'ns' in jsondata:
                    if jsondata['ns'] == 'pl.content.homeFeed.index':
                        weibo = jsondata['html']
                        m = re.search('mid=\"(\d+)\"', weibo)
                        if m:
                            self.endid = m.group(1)
                        else:
                            print 'parse error page:' + str(self.pagenum)
                        
        else:
            print '_fetch_manload: raw doc parse error'
 
        self.phase = 1
        self.nextUrl = self.makeUrl_autoload(self.uid, self.pagenum, self.endid, 0)
        return weibo

class CommentPage(Page):
    
    def __init__(self, uid, mid):
        super(CommentPage, self).__init__()
        self.pagemask  = re.compile(u'<span[.\s\S]+下一页</span>')
        self.maxidmask = re.compile(u'&max_id=(\d+)&')
        self.page  = 1
        self.uid   = uid
        self.mid   = mid
        self.maxid = 0
        
        self.error = 0
        self.once  = False
    
    def __iter__(self):
        return self
    
    def _getMaxid(self, doc):
        if not self.once:
            self.once = True
            m = re.search(self.maxidmask, doc)
            if m:
                self.maxid = m.group(1)
            else:
                print '_getMaxid error'
    
    def next(self):  
        url = self.makeUrl_comment(self.page, self.mid, self.maxid)
        doc = self.getDoc(url)
        self._getMaxid(doc)
        
        self.page += 1
        try:
            docstr = json.loads(doc)['data']['html']
            if not re.search(self.pagemask, docstr):
                raise StopIteration()
        except:
            print 'CommentPage: json data read error'
        
        if self.error > 5:
            raise Exception('You visit may be block by sina')
        return docstr
        self.isComplete = False
        raise StopIteration()

