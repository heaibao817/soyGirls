import os
from pymongo import MongoClient as Mongo
import pandas as pd
from file_util import generate_stock_json, get_predict_json
class MongoClient(object):
    def __init__(self, host, port, db, username=None, password=None):
        self.db = Mongo(host, port)[db]
        if username != None:
            self.db.authenticate(username, password)

    def findOne(self,col):
        return self.db[col].find_one()

    def find(self, col, query = None, projection = None,no_id = True):
        """ Read from Mongo and Store into DataFrame """
        cursor = self.db[col].find(query, projection)
        res = list(cursor)
        for obj in res:
            del obj['_id']
        return res

    def insert(self,col,data):
        _id = self.db[col].insert(data)
        return str(_id)

    def update(self,col,query,update,upsert=False,multi=False):
        _id = self.db[col].update(query,update,upsert=upsert,multi=multi)
        return str(_id)

    def insert_many(self,col,data):
        res = self.db[col].insert_many(data)
        return res

    def delete_repeat_records(self,indexList):
        self.col_1.ensureIndex(indexList,unique=True, dropDups=True,name="_time_station_index_")

    def find_slice(self,col,query,sort_rule,begin,length):
        cursor = self.db[col].find(query).sort(sort_rule).skip(begin).limit(length) 
        res =  list(cursor)
        for obj in res:
            del obj['_id']
        return res

    def count(self,col,query):
        return self.db[col].count(query)

    def drop(self,col):
        self.db[col].drop()

    def remove(self,col,query):
        self.db[col].remove(query)

    def load_origin(self, data_dir):
        file_list = os.listdir(data_dir)
        size = len(file_list)
        i = 1
        for file_name in file_list:
            print "%s :  %d / %d"%(file_name, i, size)
            input_name = os.path.join(data_dir, file_name)
            res = generate_stock_json(input_name)
            if len(res)>0:
                self.insert_many("origin",res)
            else:
                print "warning: %s empty data"%file_name
            i += 1

    def load_predict(self, data_dir):
        file_list = os.listdir(data_dir)
        size = len(file_list)
        i = 1
        for file_name in file_list:
            print "%s :  %d / %d"%(file_name, i, size)
            input_name = os.path.join(data_dir, file_name)
            res = get_predict_json(input_name)
            if len(res)>0:
                self.insert_many("predict",res)
            else:
                print "warning: %s empty data"%file_name
            i += 1


def load_mongo():
    data_dir = "/home/huangwei/stockwrap/data/stock_data_1day/"
    mongo = MongoClient("10.0.1.111",27017,"stock")
    mongo.load_origin(data_dir)


def load_predict():
    data_dir = "/home/huangwei/stockwrap/data/predict"
    mongo = MongoClient("10.0.1.111",27017,"stock")
    mongo.load_predict(data_dir)

if __name__ == '__main__':
    load_predict()