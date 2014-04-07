#coding: utf-8
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
    

def transformer():
    
    with open('../a.txt', 'r') as a:
        with open('../b.txt', 'w') as b:
            plain = a.read()
            unicodeText = plain.decode('unicode_escape')
            utf8Text = unicodeText.encode('utf-8')
            b.write(utf8Text)

if __name__ == '__main__':
    transformer()
    
    