#coding: utf-8

''' 

@author: admin
'''

import re, json, time 
from login import LoginFail
from pyquery import PyQuery
from main.Item import FigureItem, WeiboItem, CommentItem
from main.itemReader import Page, WeiboPage, CommentPage
from main.itemDatabase import Database, FigureDatabase, CommentDatabase, WeiboDatabase, FollowDatabase


# a wrap of itemReader and itemDatabase
class Fetcher(object):
    
    def __init__(self): 
        try:
            self.remoteReader = Page()
        except LoginFail:
            raise
        
        self.localReader  = Database()

# e.g.        depricated
# fr         = FollowReader( 123456 )
# followlist = getFollowLst()
class FollowReader(Page):
    
    def __init__(self, uid):
        super(FollowReader, self).__init__(uid)
        self.localReader = FollowDatabase()
        self.followLst = []
        
    def getFollowLst(self):
        self._fetchlist( self.makeUrl_hostfollow() ) 
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
# cr      = CommentFetcher( 123456 ) mid, uid is not required
# comment = cr.getCommentLst()
class CommentFetcher(Fetcher):
    
    def __init__(self):
        super(CommentFetcher, self).__init__()
        self.localReader = CommentDatabase() 
        self.nexturl = ''
        self.rawDoc  = ''
        self.uid = 2862441992           # none use
        
        
        self.cidmask = re.compile('object_id=(\d+)')
        self.uidmask = re.compile('id=(\d+)')
        self.nummask = re.compile('\((\d+)\)')
        
    # if database has records, never read the internet
    def getCommentLst(self, mid):
        self.mid = mid  
        self.repeat = 0
        for doc in CommentPage(self.uid, self.mid):
            self.commentLst = []
            if self._parseComment(doc):
                break 
            self.localReader.record( self.commentLst )
        ret = self.localReader.fetchLst(self.mid)
        return ret
         
    
    def _parseComment(self, doc): 
        d = PyQuery(doc) 
        repeat = 0
        for c in d('dl.comment_list.S_line1').items():
            t = CommentItem()
            dd = c.children('dd')
            #print dd.children('div.info').children('a').eq(1).outerHtml()
            m = re.search(self.nummask, dd.children('div.info').children('a').eq(0).text())
            if m:
                t.thumbs = m.group(1)
            else:
                t.thumbs = 0
                
            m = re.search(self.nummask, dd.children('div.info').children('a').eq(1).text())
            if m:
                t.comments = m.group(1)
            else:
                t.comments = 0
                
            t.cid  = re.search(self.cidmask, 
                              dd.children('div.info').children('a').attr('action-data')
                              ).group(1)
            t.uid  = re.search(self.uidmask,
                              dd.children('a').attr('usercard')
                              ).group(1)
            t.mid  = self.mid
            
            text = dd.remove('a').remove('span').remove('div').text()
            if text:
                t.text = text[1:] 
                  
            # once you fetch a same comment, you say that there is no newer comments
            if self.localReader.fetch(t.cid):
                repeat += 1
            
            if t.isValid():
                self.commentLst.append(t)  
            else:
                print '_parsecomment: item not complete'  

            if repeat > 19:
                return True

 
 
# e.g. 
# wr     = WeiboFetcher( 123456 )
# html   = wr.getWeiboLst()   # return a list of WeiboItem object
class WeiboFetcher(Fetcher):
    
    def __init__(self):         
        super(WeiboFetcher, self).__init__() 
  
        self.localReader = WeiboDatabase()   
        
        self.datamask = re.compile(u'(\(\d+\))?.*转发(\(\d+\))?.*评论(\(\d+\))?')
        self.midmask  = re.compile('mid=\"(\d+)\"')
        self.uidmask  = re.compile('ouid=(\d+)')
        
        
    def getWeiboLst(self, arg): 
        weibopage = WeiboPage(arg)
        uid = weibopage.getUID()
        ret = self.localReader.fetchLst(uid)
        if not ret: 
            for doc in WeiboPage(uid):
                self.weiboLst   = []
                self._parseWeibo(doc)
                self.localReader.recordLst(self.weiboLst)
            ret = self.localReader.fetchLst(uid) 
        return ret
        
    
    
    def _parseWeibo(self, doc):
        d = PyQuery( doc )
        
        for i in d('.WB_feed_type.SW_fun.S_line2').items():
            t = WeiboItem()
            t.uid = re.search(self.uidmask, i.attr('tbinfo')).group(1)
            
            if i.attr('mid'):
                t.mid  = int(i.attr('mid'))
             
            if i.attr('omid'):
                t.omid = int(i.attr('omid'))
            else:
                t.omid = 0
                
 
            t.text = i('.WB_detail').find('.WB_text').text()
                
            try:
                dat = i('.WB_detail').children('.WB_func.clearfix').children('.WB_from') \
                                     .children('a').attr('date')[:-4]
                t.pubtime = int(dat)
            except:
                pass
            
                             
            form = i('.WB_detail').children('.WB_func.clearfix').text()
            if form:
                t.thumbs     = 0
                t.forwarding = 0
                t.comments   = 0
                m = re.search(self.datamask, form)
                if m:
                    if m.group(1):
                        t.thumbs        = int(m.group(1)[1:-1])
                    if m.group(2):
                        t.forwarding    = int(m.group(2)[1:-1])
                    if m.group(3):
                        t.comments      = int(m.group(3)[1:-1])
            
            if self.localReader.fetch(t.mid):
                self.phase = -1
            
            if t.isValid():
                self.weiboLst.append(t)
            else:
                print '_parseweiboinfo: item not complete, will be discard'


# e.g.
# fr = FigureFetcher( 123456 )
# fg = fr.getFigure()    # fg is a Figure object
class FigureFetcher(Fetcher):
    
    def __init__(self):         
        super(FigureFetcher, self).__init__()
        self.localReader = FigureDatabase()
        self.figure = FigureItem() 
        
        self.followmask = u'(\d+)\s*</strong>\s*<span>\s*关注\s*</span>'
        self.fansmask   = u'(\d+)\s*</strong>\s*<span>\s*粉丝\s*</span>'
        self.weibomask  = u'(\d+)\s*</strong>\s*<span>\s*微博\s*</span>'
        
    def getFigure(self, uid):
        self.uid = uid
        ret = self.localReader.fetch(self.uid)
        if not ret:
            return self.updateFigure() 
        else:
            return ret

    def updateFigure(self):
        self._parseHeadinfo()
        self.remoteReader.finishFetching()
        self.localReader.record( self.figure )
        return self.figure

    def _parseHeadinfo(self):
        
        data = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostweibo(self.uid) )
        strimdata  = ''
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', data)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetch_manload: raw doc parse error'
            
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    strimdata = jdic['html']
                    d = PyQuery( strimdata ) 
                    break
        else:
            raise Exception('_parseHeadinfo error')
        
        
        info = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostinfo(self.uid) )
        m = re.search(r'注册时间[.\s\S]+(\d{4})-(\d{2})-(\d{2})', info) 
        if m:
            t = time.mktime(time.strptime('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), '%Y-%m-%d'))
        else:
            t = 0  #2012-07-06
        
        self.figure.uid       = self.remoteReader.uid
        self.figure.domainid  = self.remoteReader.domain
        self.figure.establish = t
        self.figure.follow = re.search(self.followmask, strimdata).group(1)
        self.figure.fans = re.search(self.fansmask, strimdata).group(1)
        self.figure.weibo = re.search(self.weibomask, strimdata).group(1)
        
        text1 = d('span').filter('.name').text()
        text2 = d('strong').filter('.W_f20.W_Yahei').text()
        if text1:
            self.figure.name = text1
        else:
            self.figure.name = text2
             
        try:
            self.figure.verify = d('.pf_verified_info').contents()[0]
        except:
            self.figure.verify = ''
            
            
        self.figure.intro = d('.pf_intro').text()
         
        for i in d('.layer_menulist_tags').items('a'):
            self.figure.tags.append( i.text() ) 
            
        if not self.figure.isValid():
            print 'weibo figure info not enough'
                
                
                
                
                