'''
@author: prehawk
'''
import login
import urllib2
from config import *

class A(login.Login):
    
    def __init__(self):
        super(A, self).__init__(TEST_USER, TEST_PWD)


    def scrap(self, url):
        doc = urllib2.urlopen(url).read()
        print doc
    

if __name__ == '__main__':
    a = A()
    a.scrap('http://weibo.com/p/1006061718436033/info?from=page_100606&mod=TAB#place')
    
    
    