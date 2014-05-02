#coding: utf-8

''' 

@author: admin
'''
import re, json, os, time 
import urllib2 
import config 
from pyquery import PyQuery
from itemSorage import FigureItem, WeiboItem, CommentItem


time_retry = 0

# for inheritant
# include basic weibo info.
class WeiboPage(object):
    
    def __init__(self, uid):         
       
        self.hosthome   = 'http://weibo.com/' 
        self.pagenum    = 1
        self.filecount  = 0
        self.uid        = uid 
        
        url = self.hosthome + 'u/' + str(uid)
        doc = self.getDoc(url).decode('string_escape') 
        
        m = re.search(r'href=\"\\/p\\/(\d+)\\/(\w+)\?from=page_(\d+)', doc)
        if m:
            self.fulluid    = m.group(1)
            self.domain     = m.group(3)  # getDoc for domain id
            self.hostweibo  = self.hosthome + 'p/' + self.fulluid + '/weibo?from=page_'  + self.domain + '&mod=TAB'
            self.hostfollow = self.hosthome + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=1'
            self.hostinfo   = self.hosthome + 'p/' + self.fulluid + '/info?from=page_'   + self.domain + '&mod=TAB'
        else:
            print 'Init: Alias reference page parse error'
            return

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

    #depricate
    def makeUrl_comment2(self, mid, uid):
        ret = self.hosthome + 'aj/comment/small?_wv=5&act=list&mid=' + \
                str(mid) + '&uid=' + str(uid) + '&isMain=true&ouid=' + str(uid)
        return ret
    
    def makeUrl_autoload(self, pagenum, endid, num):
        return self.hosthome + 'p/aj/mblog/mbloglist?domain=' + self.domain + '&pre_page=' + str(pagenum) \
                + '&page=' + str(pagenum) + '&max_id=0&end_id=' + str(endid) + '&count=15&pagebar=' + str(num) \
                + '&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__20&id=' + self.fulluid \
                + '&script_uri=/p/' + self.fulluid + '/weibo&feed_type=0&from=page_' + self.domain + '&mod=TAB'
    
    def makeUrl_manload(self, pagenum):
        return self.hostweibo + 'pids=Pl_Official_LeftProfileFeed__20&is_search=0&visible=0&is_tag=0&profile_ftype=1&page=' \
                    + str(pagenum)
    
    def makeUrl_comment(self, pagenum, mid):
        return self.hosthome + 'aj/comment/big?_wv=5&id=' + str(mid) + '&page=' + str(pagenum)
                
    def makeUrl_follow(self, pagenum):
        return self.hosthome + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=' \
                + str(pagenum)
    
    
# e.g.
# fr         = FollowReader( 123456 )
# followlist = getFollowLst()
class FollowReader(WeiboPage):
    
    def __init__(self, uid):
        super(FollowReader, self).__init__(uid)
        self.followLst = []
        
    def getFollowLst(self):
        self._fetchlist( self.hostfollow ) 
        return self.followLst
        
    def _fetchlist(self, url):
        doc = self.getDoc(url).decode('string_escape') 
          
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
            url = self.makeUrl_follow(self.pagenum)
            self._fetchlist(url)



# e.g.
# cr      = CommentReader( 123456 ) mid, uid is not required
# comment = cr.getCommentLst()
class CommentReader(WeiboPage):
    
    def __init__(self, mid, uid=2862441992):
        super(CommentReader, self).__init__(uid)
        self.mid = mid 
        self.nexturl = ''
        self.rawDoc  = ''
        self.commentLst = []
        
    
    def getCommentLst(self):
        self._parseComment()
        return self.commentLst
    
    def _parseComment(self):
        self._fetchComment()
        d = PyQuery(self.rawDoc)
        t = CommentItem()
        cidmask = re.compile('object_id=(\d+)')
        uidmask = re.compile('id=(\d+)')
        nummask = re.compile('\((\d+)\)')  
        for c in d('dl.comment_list.S_line1').items():
            dd = c.children('dd')
            #print dd.children('div.info').children('a').eq(1).outerHtml()
            m = re.search(nummask, dd.children('div.info').children('a').eq(0).text())
            if m:
                t.thumbs = m.group(1)
            else:
                t.thumbs = 0
                
            m = re.search(nummask, dd.children('div.info').children('a').eq(1).text())
            if m:
                t.comment = m.group(1)
            else:
                t.comment = 0
                
            t.cid  = re.search(cidmask, 
                              dd.children('div.info').children('a').attr('action-data')
                              ).group(1)
            t.uid  = re.search(uidmask,
                              dd.children('a').attr('usercard')
                              ).group(1)
            t.mid  = self.mid
            
            t.text = dd.remove('a').remove('span').remove('div').text()[1:] 
                  
            self.commentLst.append(t)
        

    def _fetchComment(self):
        nextpage = re.compile(u'<span[.\s\S]+下一页</span>')
        page     = 1
        
        while(True):
            url = self.makeUrl_comment(page, self.mid)
            doc = self.getDoc(url)
            
            docstr = json.loads(doc)['data']['html']
            if docstr:
                self.rawDoc += docstr + '\n'
                #print docstr
                if re.search(nextpage, docstr):
                    page += 1
                else:
                    break
         
 
    
    
        

# e.g. 
# wr     = WeiboReader( 123456 )
# html   = wr.getWeiboHtml()
class WeiboReader(WeiboPage):
    
    def __init__(self, uid):         
        super(WeiboReader, self).__init__(uid) 
  
        self.figure     = FigureItem()
        self.weiboLst   = []
        self.commentLst = []
        
        self.phase      = 0
        self.nextUrl    = self.hostweibo 
        
        #generated by self._requestWeibo method
        self.rawPage   = []    # 3 tuple, 1: uid, 2: figure info page, 3: weibo html intergrity
    
    #depricate
    def getWeiboHtml(self):
        self._requestWeibo()         
        return self.rawPage
                    
    def getFigureInfo(self):
        self._requestFormatInfo()
        return self.figure
    
    def getWeiboLst(self):
        #self._requestFormatInfo() 
        fd = '../BigVs/' + str(self.uid)
        if os.path.exists(fd): 
            with open( '../BigVs/' + str(self.uid), 'r' ) as f:
                rawdoc = f.read()
                
                
        d = PyQuery( rawdoc.decode('utf-8') )
        
        t = WeiboItem()
        datamask = re.compile('\((\d+)\).*\((\d+)\).*\((\d+)\)') 
        for i in d('.WB_feed_type.SW_fun.S_line2').items():
            t.mid       = i.attr('mid')
            t.omid      = i.attr('omid')
            t.text      = i('.WB_detail').find('.WB_text').text() 
            t.pubtime   = i('.WB_detail') \
                            .children('.WB_func.clearfix') \
                            .children('.WB_from') \
                            .children('a').attr('date')[:-4]
                            
            CommentReader(t.mid, self.uid).getCommentLst()
            
            m = re.search(datamask, i('.WB_detail').children('.WB_func.clearfix').text())
            if m:
                t.thumbs     = m.group(1)
                t.forwarding = m.group(2)
                t.comment    = m.group(3)
                
        return self.weiboLst
    
    def _fetchComment(self):
        self._requestFormatInfo()
        return self.commentLst
    
    def _requestFormatInfo(self):
        if not self.rawPage:
            self.rawPage = [self.uid, '', '']
            self._requestWeibo()
            self._parseHeadinfo(self.rawPage[1])
            self._parseWeiboinfo(self.rawPage[2])
            self._parseCommentinfo(0)
            
 
    def _parseWeiboinfo(self, doc):
        d = PyQuery( doc )
        
        
        t = WeiboItem()
        datamask = re.compile('\((\d+)\).*\((\d+)\).*\((\d+)\)')
        nummask  = re.compile('.*=(\d+)')
        for i in d('.WB_feed_type.SW_fun.S_line2').items():
            t.mid       = i.attr('mid')
            t.omid      = i.attr('omid')
            t.text      = i('.WB_detail').find('.WB_text').text() 
            t.pubtime   = i('.WB_detail') \
                            .children('.WB_func.clearfix') \
                            .children('.WB_from') \
                            .children('a').attr('date')[:-4]
                            
            n = re.search(nummask, i.attr('tbinfo'))
            if n:
                t.ouid       = n.group(1)
            
            m = re.search(datamask, i('.WB_detail').children('.WB_func.clearfix').text())
            if m:
                t.thumbs     = m.group(1)
                t.forwarding = m.group(2)
                t.comment    = m.group(3)
                
            self.weiboLst.append(t)
        
       
    
    def _parseCommentinfo(self, mid):
        pass 

    def _parseHeadinfo(self, doc):
        d = PyQuery( doc ) 
        
        info = self.getDoc(self.hostinfo)
        m = re.search(r'注册时间[.\s\S]+(\d{4})-(\d{2})-(\d{2})', info) 
        if m:
            t = time.mktime(time.strptime('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), '%Y-%m-%d'))
        else:
            t = 1341504000  #2012-07-06
        
        self.figure.uid       = self.uid
        self.figure.domainid  = self.domain
        self.figure.establish = t
        self.figure.follow = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'follow').text()
        self.figure.fans = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'fans').text()
        self.figure.weibo = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'weibo').text()
        
        self.figure.name = d('span').filter('.name').text()
        self.figure.verify = d('.pf_verified_info').contents()[0]
        self.figure.intro = d('.pf_intro').text()
         
        for i in d('.layer_menulist_tags').items('a'):
            self.figure.tags.append( i.text() ) 
            
        if not self.figure.isFullfill():
            print 'weibo figure info not enough' 
        

    #long long request time, generate self.rawPage
    def _requestWeibo(self):
        while self.phase >= 0: 
            self.data = self.getDoc(self.nextUrl)
            
            if self.phase == 0:
                self._fetchNext1()
            else:
                self._fetchNext2(self.phase)
 
 
    def _fetchNext2(self, phase):

        docstr = json.loads(self.data)['data']
        self.rawPage[2] += docstr
          
        if phase == 2: # encounter the end of the page 
            if re.search(u'<span>下一页</span></a>', docstr):  # has next page
                self.pagenum += 1
                self.phase = 0 
                self.nextUrl = self.makeUrl_manload(self.pagenum) 
            else: # whole loop end
                print 'the end! ' + str(self.pagenum - 1) + 'pages'
                self.phase = -1
                return
        else:
            self.phase = 2
            self.nextUrl = self.makeUrl_autoload(self.pagenum, self.endid, 1) 

    def _fetchNext1(self):
                 
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', self.data)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetchNext1: raw doc parse error'
        
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    head = jdic['html'] 
                    self.rawPage[1] = head 
                if jdic['ns'] == 'pl.content.homeFeed.index':
                    weibo = jdic['html']
                    n = re.search('mid=\"(\d+)\"', weibo)
                    if n:
                        self.endid = n.group(1)
                    else:
                        print 'parse error' + str(self.pagenum)
                        
                    self.rawPage[2] += weibo
                     
  
        self.phase = 1
        self.nextUrl = self.makeUrl_autoload(0)
        
    
  