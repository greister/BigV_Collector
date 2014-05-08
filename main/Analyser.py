#coding:utf-8

'''
@author: admin
'''

import re
from main.itemFetcher import WeiboFetcher, FigureFetcher, CommentFetcher
from main.Item import *


class Analyser(object):
    
    def __init__(self, filename):
        self.anaLst = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.anaLst.append( line )
        self.fgFetch = FigureFetcher()
        self.wbFetch  = WeiboFetcher()

    
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration()
    
    def prepareData(self):
        wbs = []
        for figure in self.anaLst:
            f = self.fgFetch.getFigure(figure)
            wbs.append( self.wbFetch.getWeiboLst(figure) )
            print f.name
        
            
    
    
