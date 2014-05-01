#coding:utf-8
'''
Created on 2014年4月15日

@author: admin
'''


class FigureItem(object):
    
    def __init__(self):
        self.uid        = 0
        self.domainid   = 0
        self.name       = ''
        self.verify     = ''
        self.intro      = ''
        self.follow     = -1
        self.fans       = -1
        self.weibo      = -1
        self.tags       = []
        self.establish  = 0     #better time stamp
        
    def isFullfill(self):
        if self.uid == 0 or \
            self.domainid == 0 or \
            self.name == '' or \
            self.verify == '' or \
            self.intro == '' or \
            self.follow == -1 or \
            self.fans == -1 or \
            self.weibo == -1 or \
            self.establish == 0:
            return False
        else:
            return True 
        
        
class WeiboItem(object):

    def __init__(self):
        #  mid, omid, thumbs, forwarding, comment, pubtime, text
        self.mid        = 0
        self.omid       = 0 
        self.thumbs     = 0
        self.forwarding = 0
        self.comment    = 0
        self.pubtime    = 0     #better time stamp
        self.text       =''
        

    def isFullfill(self):
        if self.mid == 0 or \
            self.omid == 0 or \
            self.thumbs == 0 or \
            self.forwarding == 0 or \
            self.comment == 0 or \
            self.pubtime == 0 or \
            self.text == '' :
            return False
        else:
            return True 
        
        
        
class CommentItem(object):
    pass
