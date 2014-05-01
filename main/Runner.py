#coding: utf-8
'''
@author: prehawk
''' 

from itemReader import *

class Controller(login.Login):
    
    def __init__(self, proxyip = False):
        super(Controller, self).__init__(config.TEST_USER, config.TEST_PWD, proxyip)
        
        
    def start(self):\
        wr = WeiboReader(2862441992).getWeiboLst()
        #fg = self.writeWeiboLst( 2862441992 )
        #print fg.name 
        
        
        
    def parseWeiboLst(self, uid):
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
        
        
    def writeWeiboLst(self, uid):

        wr = WeiboReader(uid)
        ret = wr.getWeiboHtml()
        
        
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




if __name__ == '__main__':
    c = Controller()
    c.start()