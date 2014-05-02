#coding:utf-8

'''
@author: admin
'''


import re 
import time
import config
import urllib2


time_retry = 0
 
# include basic weibo info.
class WeiboPage(object):
    
    def __init__(self, uid=2862441992):         
        self.isComplete   = False                 # whether this page is info isComplete
        
        self.host   = 'http://weibo.com/' 
        self.pagenum    = 1 
        self.uid        = uid 
         

    def _complete(self):
        if not self.isComplete:
            url = self.host + 'u/' + str(self.uid)
            doc = self.getDoc(url).decode('string_escape')
            
            m = re.search(r'href=\"\\/p\\/(\d+)\\/(\w+)\?from=page_(\d+)', doc)
            if m:
                self.fulluid    = m.group(1)
                self.domain     = m.group(3)  # getDoc for domain id
            else:
                raise Exception('Your visit may be block by Sina!')
            self.isComplete = True


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

    #depricate, indepent
    def makeUrl_comment2(self, mid, uid):
        return self.host + 'aj/comment/small?_wv=5&act=list&mid=' + \
                str(mid) + '&uid=' + str(uid) + '&isMain=true&ouid=' + str(uid)
    
    def makeUrl_hostfollow(self):
        self._complete()
        return self.host + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=1'
    
    def makeUrl_hostweibo(self):
        self._complete()
        return self.host + 'p/' + self.fulluid + '/weibo?from=page_'  + self.domain + '&mod=TAB'
    
    def makeUrl_hostinfo(self):
        self._complete()
        return self.host + 'p/' + self.fulluid + '/info?from=page_'   + self.domain + '&mod=TAB'
    
    # need isComplete
    def makeUrl_autoload(self, pagenum, endid, num): 
        self._complete()
        return self.host + 'p/aj/mblog/mbloglist?domain=' + self.domain + '&pre_page=' + str(pagenum) \
                + '&page=' + str(pagenum) + '&max_id=0&end_id=' + str(endid) + '&count=15&pagebar=' + str(num) \
                + '&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__20&id=' + self.fulluid \
                + '&script_uri=/p/' + self.fulluid + '/weibo&feed_type=0&from=page_' + self.domain + '&mod=TAB'
    
    # indepent
    def makeUrl_manload(self, pagenum):
        w = self.makeUrl_hostweibo()
        return  w + 'pids=Pl_Official_LeftProfileFeed__20&is_search=0&visible=0&is_tag=0&profile_ftype=1&page=' \
                    + str(pagenum)
    
    # indepent
    def makeUrl_comment(self, pagenum, mid):
        return self.host + 'aj/comment/big?_wv=5&id=' + str(mid) + '&page=' + str(pagenum)
     
    # need isComplete           
    def makeUrl_follow(self, pagenum):
        self._comlete()
        return self.host + 'p/' + self.fulluid + '/follow?from=page_' + self.domain + '&page=' \
                + str(pagenum)






