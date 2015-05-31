#encoding: utf-8
'''
Created on 2015-05-28 19:25

author: Linzertorte https://github.com/Linzertorte/LeetCode-in-Python/edit/master/LRUCache.py
modify: YuZhenchuan
email: yuzhenchuan@delete.so
'''

from base.hash_lru import LRUCache
from base.db_proc import db_proc
from base.PO.ACcommentsPO import *
from multiprocessing.dummy import Pool as ThreadPool 

class Ac_Data():
    def __init__(self, capacity):
        self.db_proc = db_proc()
        self.lru = LRUCache(capacity)
        
    #从数据库中读取
    def load(self):
        datas = self.db_proc.ACComments.load()
        #使用map进行多线程读取历史数据
        pool = ThreadPool(16) 
        nodes = pool.map(self.load_data, tuple(datas))
        pool.close()
        pool.join()
        
        #载入历史数据
        for node in nodes:
            self.insert(node)
            
    def load_data(self, data):
        row = ACcommentsPO()
        row.set_cid(int(data[0]))
        row.set_content(data[1])
        row.set_user_name(data[2])
        row.set_layer(int(data[3]))
        row.set_acid(int(data[4]))
        row.set_delete(int(data[5]))
        row.set_delete(int(data[6]))
        row.set_check_time(data[7])
        
        return row
    
    def insert(self, data):
        if not data:
            #有的投稿什么都没有
            return
        
        if data.get_delete() == 1\
        or data.get_siji() == 1:
            try:
                self.db_proc.ACComments.insert(self.lru.get(data.get_cid()))
            except Exception as e:
                #永远不应该走到这里
                print e
                pass
        else:
            try:
                self.lru.set(data.get_cid(), data)
            except Exception as e:
                print e
                #在多线程并发的时候，容易出现头结点被同时操作的情况，先跑跑看，以后再看是不是需要加锁
                pass
            
    def save(self):
        nodes = self.lru.get_all()
        self.db_proc.ACComments.clear()
        pool = ThreadPool(16) 
        nodes = pool.map(self.db_proc.ACComments.save, tuple(nodes))
        pool.close()
        pool.join()