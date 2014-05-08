#coding: utf-8
'''
@author: prehawk
'''  
import re, time
import os 
import config
from login import Login
from pyquery import PyQuery
from main.Item import FigureItem, WeiboItem, CommentItem
from main.itemFetcher import WeiboFetcher, FigureFetcher, CommentFetcher, FollowReader
from Analyser import Analyser

 
    
class Controller():
    
    def __init__(self):
        Login(config.TEST_USER, config.TEST_PWD, config.TEST_PROXY)
        
        
    def start(self):  
        #self.test_getlotsfigure() 
        a = Analyser('../university_lib.txt')
        a.prepareData()
        pass
    
    def test_arg(self):
        a = '1234556666'
        b = '123455'
        
        print a[len(b):]
        
        

    def test_printweibo(self):
        w = WeiboFetcher()
        wf = w.getWeiboLst(2862441992)
        for i in wf:
            print i.text
        
    def test_printfigure(self):
        f = FigureFetcher()
        fg = f.getFigure(2862441992)
        print fg.name
        
    def test_printcomment(self):
        c = CommentFetcher()
        cm = c.getCommentLst(3694134789199108)
        for c in cm:
            print c.text
     
    def debug_html(self):
        with open('../a.html', 'r') as f:
            d = PyQuery( f.read().decode('utf-8') )
        print d('.WB_detail').html()
        
    def test_getlotsfigure(self): 
        figure  = FigureFetcher()
        weibo   = WeiboFetcher()
        comment = CommentFetcher()
        with open('../followlist', 'r') as f:
            for line in f.readlines(): 
                figure.getFigure( int(line) )
                ret2 = weibo.getWeiboLst( int(line) )
                for r in ret2:
                    comment.getCommentLst(r.mid)
                break
                
                
    def test_nonetype(self):
        
        pass
    
    def test_re(self):
        text = u'| 转发(361) | 收藏| 评论(5) 2013-8-23 15:48 来自 微博 weibo.com | 举报'
        mask = re.compile(u'(\((\d+)\))?\|\s*转发\s*(\((\d+)\))?\s*\|\s*收藏\s*(\((\d+)\))?\|\s*评论(\((\d+)\))?')
        m = re.search(mask, text) 
        if m:
            print m.group(2)
            print m.group(4)
            print m.group(8)
        
        
    def test_parseWeiboLst(self, uid):
        fd = '../BigVs/' + str(uid)
        if os.path.exists(fd): 
            with open( '../BigVs/' + str(uid), 'r' ) as f:
                rawdoc = f.read()
            
            d = PyQuery( rawdoc.decode('utf-8') ) 
            fg = FigureItem()
            
            fg.follow = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'follow').text()
            fg.fans = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'fans').text()
            fg.weibo = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'weibo').text()
            
            fg.name = d('span').filter('.name').text()
            fg.verify = d('.pf_verified_info').contents()[0]
            fg.intro = d('.pf_intro').text()
             
            for i in d('.layer_menulist_tags').items('a'):
                fg.tags.append( i.text() ) 
                
                
            return fg
        else:
            print 'file not exists'
        
    def test_writeWeiboLst(self, uid):

        wr = WeiboFetcher(uid)
        ret = wr.getWeiboHtml()
        
        
        savedir = '../BigVs/'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
            
        with open( savedir + str(ret[0]), 'w' ) as f:
            f.write(ret[1].encode('utf-8') + '\n\n')
            f.write(ret[2].encode('utf-8') )
    
    def test_writeFollowLst(self):
         
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




if __name__ == '__main__':
    c = Controller()
    c.start()