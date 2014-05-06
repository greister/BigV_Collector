#coding:utf-8

'''
@author: admin
'''

import re
from main.itemFetcher import WeiboFetcher, FigureFetcher, CommentFetcher

class Analyser(object):
    
    def __init__(self):
        pass
    
    def __iter__(self):
        return self
    
    def next(self):
        pass