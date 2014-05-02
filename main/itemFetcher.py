#coding: utf-8

''' 

@author: admin
'''

import re, json, time 
from pyquery import PyQuery
from main.Item import FigureItem, WeiboItem, CommentItem
from main.itemReader import WeiboPage
from main.itemDatabase import Database, FigureDatabase, CommentDatabase, WeiboDatabase


# a wrap of itemReader and itemDatabase
class Fetcher(object):
    
    def __init__(self): 
        self.remoteReader = WeiboPage()
        self.localReader  = Database()

# e.g.        depricated
# fr         = FollowReader( 123456 )
# followlist = getFollowLst()
class FollowReader(WeiboPage):
    
    def __init__(self, uid):
        super(FollowReader, self).__init__(uid)
        self.localReader = FollowReader()
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
    
    def __init__(self, mid, uid=2862441992):
        super(CommentFetcher, self).__init__()
        self.localReader = CommentDatabase()
        self.mid = mid 
        self.nexturl = ''
        self.rawDoc  = ''
        self.commentLst = []
        
    # if database has records, never read the internet
    def getCommentLst(self): 
        if not self.localReader.fetch(self.mid):
            self.addCommentLst() 
        ret = self.localReader.fetchLst(self.mid)
        return ret
        
    
    def addCommentLst(self): 
        self._fetchComment()
        self.localReader.record( self.commentLst )
    
     
    
    def _parseComment(self, doc): 
        d = PyQuery(doc)
        
        cidmask = re.compile('object_id=(\d+)')
        uidmask = re.compile('id=(\d+)')
        nummask = re.compile('\((\d+)\)')  
        
        for c in d('dl.comment_list.S_line1').items():
            t = CommentItem()
            dd = c.children('dd')
            #print dd.children('div.info').children('a').eq(1).outerHtml()
            m = re.search(nummask, dd.children('div.info').children('a').eq(0).text())
            if m:
                t.thumbs = m.group(1)
            else:
                t.thumbs = 0
                
            m = re.search(nummask, dd.children('div.info').children('a').eq(1).text())
            if m:
                t.comments = m.group(1)
            else:
                t.comments = 0
                
            t.cid  = re.search(cidmask, 
                              dd.children('div.info').children('a').attr('action-data')
                              ).group(1)
            t.uid  = re.search(uidmask,
                              dd.children('a').attr('usercard')
                              ).group(1)
            t.mid  = self.mid
            
            t.text = dd.remove('a').remove('span').remove('div').text()[1:] 
                  
            # once you fetch a same comment, you say that there is no newer comments
            if self.localReader.fetch(t.cid):
                return False
            
            if t.isValid():
                self.commentLst.append(t)
                return True
            else:
                print '_parsecomment: item not complete'
                return False
        

    def _fetchComment(self):
        nextpage = re.compile(u'<span[.\s\S]+下一页</span>')
        page     = 1
        
        while(True):
            url = self.remoteReader.makeUrl_comment(page, self.mid)
            doc = self.remoteReader.getDoc(url)
            
            docstr = json.loads(doc)['data']['html']
            if self._parseComment(docstr):  
                if re.search(nextpage, docstr):
                    page += 1
                else:
                    break
            else:
                break
         
 
 
# e.g. 
# wr     = WeiboFetcher( 123456 )
# html   = wr.getWeiboLst()   # return a list of WeiboItem object
class WeiboFetcher(Fetcher):
    
    def __init__(self, uid):         
        super(WeiboFetcher, self).__init__() 
  
        self.localReader = WeiboDatabase() 
        self.weiboLst    = []
        self.uid         = uid
        self.phase       = 0
        self.pagenum     = 1
        self.nextUrl     = self.remoteReader.makeUrl_hostweibo() 
         
        self.rawPage   = ''    
        
    def getWeiboLst(self):  
        if not self.localReader.fetch(self.uid):
            self.addWeiboLst()
        ret = self.localReader.fetchLst(self.uid)
        return ret
        
    def addWeiboLst(self):
        self._requestWeibo()
        self.localReader.record(self.weiboLst)
    
    
    def _parseWeiboinfo(self, doc):
        d = PyQuery( doc )
        ret = True
        
        datamask = re.compile('\((\d+)\).*\((\d+)\).*\((\d+)\)') 
        
        for i in d('.WB_feed_type.SW_fun.S_line2').items():
            t = WeiboItem()
            t.uid       = self.uid  
            t.mid       = i.attr('mid')
            omid = i.attr('omid')
            if not omid:
                t.omid = 0
            else:
                t.omid = omid
            t.text      = i('.WB_detail').find('.WB_text').text()  
            t.pubtime   = i('.WB_detail') \
                            .children('.WB_func.clearfix') \
                            .children('.WB_from') \
                            .children('a').attr('date')[:-4]
                             
            m = re.search(datamask, i('.WB_detail').children('.WB_func.clearfix').text())
            if m:
                t.thumbs      = m.group(1)
                t.forwarding  = m.group(2)
                t.comments    = m.group(3)
            else:
                t.thumbs      = 0
                t.forwarding  = 0
                t.comments    = 0
            
            if self.localReader.fetch(t.mid):
                return False
            
            if t.isValid():
                self.weiboLst.append(t)
                ret = True
            else:
                print '_parseweiboinfo: item not complete'
                ret = False
                
        return ret

    #long long request time, generate self.rawPage
    def _requestWeibo(self):
        while self.phase >= 0: 
            self.data = self.remoteReader.getDoc(self.nextUrl)
            
            if self.phase == 0:
                if not self._fetchNext1():
                    break
            else:
                if not self._fetchNext2(self.phase):
                    break
 
 
    def _fetchNext2(self, phase):

        docstr = json.loads(self.data)['data']
        if not self._parseWeiboinfo( docstr ):
            return False
          
        if phase == 2: # encounter the end of the page 
            if re.search(u'<span>下一页</span></a>', docstr):  # has next page
                self.pagenum += 1
                self.phase = 0
                self.nextUrl = self.remoteReader.makeUrl_manload(self.pagenum) 
            else: # whole loop end
                print 'the end! ' + str(self.pagenum - 1) + 'pages'
                self.phase = -1 
            return True
        else:
            self.phase = 2
            self.nextUrl = self.remoteReader.makeUrl_autoload(self.pagenum, self.endid, 1) 
            return True

    def _fetchNext1(self):
                 
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', self.data)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetchNext1: raw doc parse error'
        
        ret = True 
        for jdic in jdiclst:
            if 'ns' in jdic: 
                if jdic['ns'] == 'pl.content.homeFeed.index':
                    weibo = jdic['html']
                    n = re.search('mid=\"(\d+)\"', weibo)
                    if n:
                        self.endid = n.group(1)
                    else:
                        print 'parse error' + str(self.pagenum)
                        
                    if not self._parseWeiboinfo( weibo ):
                        ret = False
    
        self.phase = 1
        self.nextUrl = self.remoteReader.makeUrl_autoload(self.pagenum, self.endid, 0)
        return ret
        

# e.g.
# fr = FigureFetcher( 123456 )
# fg = fr.getFigure()    # fg is a Figure object
class FigureFetcher(Fetcher):
    
    def __init__(self, uid):         
        super(FigureFetcher, self).__init__()
        self.localReader = FigureDatabase()
        self.figure = FigureItem()
        self.uid = uid
        
    def getFigure(self):
        ret = self.localReader.fetch(self.uid)
        if not ret:
            return self.updateFigure()
        else:
            return ret

    def udpateFigure(self):
        self._parseHeadinfo()
        self.localReader.record( self.figure )
        return self.figure

    def _parseHeadinfo(self):
        
        data = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostweibo() )
        
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', data)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetchNext1: raw doc parse error'
            
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    d = PyQuery( jdic['html'] ) 
                    break
        else:
            raise Exception('_parseHeadinfo error')
        
        
        info = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostinfo() )
        m = re.search(r'注册时间[.\s\S]+(\d{4})-(\d{2})-(\d{2})', info) 
        if m:
            t = time.mktime(time.strptime('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), '%Y-%m-%d'))
        else:
            t = 1341504000  #2012-07-06
        
        self.figure.uid       = self.remoteReader.uid
        self.figure.domainid  = self.remoteReader.domain
        self.figure.establish = t
        self.figure.follow = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'follow').text()
        self.figure.fans = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'fans').text()
        self.figure.weibo = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'weibo').text()
        
        self.figure.name = d('span').filter('.name').text()
        self.figure.verify = d('.pf_verified_info').contents()[0]
        self.figure.intro = d('.pf_intro').text()
         
        for i in d('.layer_menulist_tags').items('a'):
            self.figure.tags.append( i.text() ) 
            
        if not self.figure.isValid():
            print 'weibo figure info not enough'
                
                
                
                
                