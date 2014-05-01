#coding:utf-8
'''
Created on 2014年4月11日

@author: admin
'''
import re
import urllib2
import login
import config

class Proxy(login.Login):
    
    def __init__(self, username=config.TEST_USER, pwd=config.TEST_PWD, proxyip = False): 
         
        super(Proxy, self).__init__(username, pwd, proxyip)  
        
        
        # This time, rather than install the OpenerDirector, we use it directly:
        ipdoc = urllib2.urlopen('http://iframe.ip138.com/ic.asp').read().decode('gbk')
        print re.search('\[(\d+\.\d+\.\d+\.\d+)\]', ipdoc).group(1) 
        print urllib2.urlopen('http://weibo.com').read()

if __name__ == '__main__':
    proxy1 = 'http://41.0.57.83:3128'
    proxy2 = 'http://58.22.0.54:81'
    proxy3 = 'http://59.38.32.35:1111'
    proxy4 = 'http://60.190.138.151:80'
    p = Proxy(proxy4)
    