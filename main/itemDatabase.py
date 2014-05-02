#coding:utf-8

''' 

@author: admin
'''

import sqlite3
import config
from main.Item import FigureItem, WeiboItem, CommentItem

class Database(object):
   
    def __init__(self):
        self.cxn = sqlite3.connect(config.DB_FILE)
        self.cur = self.cxn.cursor() 
        
        # if no tables create one
        try:
            self.cur.execute("SELECT * FROM Comment")
            self.cur.execute("SELECT * FROM Weibo")
            self.cur.execute("SELECT * FROM Figure")
            self.cur.execute("SELECT * FROM Bigv")
        except sqlite3.OperationalError, e:
            if e.message.startswith('no such table'):     
                with open('../tables.sql', 'r') as f:
                    self.cur.executescript(f.read())
                self.cxn.commit()
        

# done 
class FigureDatabase(Database):
    
    def __init__(self):
        super(FigureDatabase, self).__init__()
        
    def fetch(self, uid):
        sql = "SELECT * FROM Figure WHERE u_id=?"
        self.cur.execute( sql, (uid,) )
        row = self.cur.fetchone()
        if row:
            return self.itemCast(row) 

    def itemCast(self, row):
        fg = FigureItem()
        fg.uid          = row[0]
        fg.domainid     = row[1]
        fg.name         = row[2] 
        fg.follow       = row[3]
        fg.fans         = row[4]
        fg.weibo        = row[5]
        fg.establish    = row[6]     
        return fg

    def record(self, fg):
        try:
            sql = "INSERT INTO Figure VALUES (?,?,?,?,?,?,?)"
            self.cur.execute(sql, 
                             (fg.uid, fg.domainid, fg.name, fg.follow, fg.fans, fg.weibo, fg.establish) )
        except sqlite3.IntegrityError:
            sql = "UPDATE Figure SET 'follow'=?,'fans'=?,'weibo'=?" 
            self.cur.execute(sql, 
                             (fg.follow, fg.fans, fg.weibo) )
        self.cxn.commit()
        
     
     
     
     
class WeiboDatabase(Database):
    
    def __init__(self):
        super(WeiboDatabase, self).__init__()
        
    def fetch(self, mid):
        sql = "SELECT * FROM Weibo WHERE m_id=?"
        self.cur.execute( sql, (mid,) )
        row = self.cur.fetchone()
        if row:
            return self.itemCast(row) 
        
    def itemCast(self, row):
        wb = WeiboItem()
        wb.mid         = row[0]
        wb.omid        = row[1]
        wb.uid         = row[2]
        wb.thumbs      = row[3]
        wb.forwarding  = row[4]
        wb.comment     = row[5]     #better time stamp
        wb.pubtime     = row[6]
        wb.text        = row[7]
        return wb
        
    def record(self, wbs):
        for wb in wbs: 
            try:
                sql = "INSERT INTO Weibo VALUES (?,?,?,?,?,?,?,?)"
                self.cur.execute(sql, 
                        (wb.mid, wb.omid, wb.uid, wb.thumbs, wb.forwarding, wb.comment, wb.pubtime, wb.text) )
            except sqlite3.IntegrityError:
                sql = "UPDATE Weibo SET 'thumbs'=?,'forwarding'=?,'comment'=?" 
                self.cur.execute(sql, 
                                 (wb.thumbs, wb.forwarding, wb.comments) )
        self.cxn.commit()
        
        
      
         
class CommentDatabase(Database):
    
    def __init__(self):
        super(CommentDatabase, self).__init__()
        
        

    def fetchLst(self, mid):
        sql = "SELECT * FROM Comment WHERE c_mid=?"
        self.cur.execute( sql, (mid,) )
        rows = self.cur.fetchall()
        ret = []
        if rows:
            for r in rows:
                ret.append( self.itemCast(r) )
            return ret

    def fetch(self, cid):
        sql = "SELECT * FROM Comment WHERE c_id=?"
        self.cur.execute( sql, (cid,) )
        row = self.cur.fetchone() 
        if row:
            return self.itemCast(row) 
        
    def itemCast(self, row):
        cm = CommentItem()
        cm.cid         = row[0]
        cm.mid         = row[1]
        cm.uid         = row[2]
        cm.text        = row[3]
        cm.thumbs      = row[4]
        cm.comments    = row[5]
         
        return cm
        
    def record(self, cms):
        for cm in cms:
            try:
                sql = "INSERT INTO Comment VALUES (?,?,?,?,?,?)"
                self.cur.execute(sql, 
                        (cm.cid, cm.mid, cm.uid, cm.text, cm.thumbs, cm.comments) )
            except sqlite3.IntegrityError:
                sql = "UPDATE Comment SET 'thumbs'=?,'comments'=?" 
                self.cur.execute(sql, 
                                 (cm.thumbs, cm.comments) )
        self.cxn.commit() 
   
   
   
   
   
        
class FollowDatabase(Database):
    
    def __init__(self):
        super(FollowDatabase, self).__init__()
    