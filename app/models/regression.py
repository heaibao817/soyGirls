import sys
sys.path.append(".")
sys.path.append("../")
sys.path.append("../../")
import json
from app.util.mongo_util import MongoClient
# stock_no : SH000001
# stock_id : 1
# only support stock_no query
# because SH000001 -> index, SZ000001 -> PingAn, but they share the same stock_id
# date should be string not number
class Regression(object):
    def __init__(self):
        self.HOST = "10.0.1.111"
        self.PORT = 27017
        self.DB_NAME = "stock"
        self.mongo = MongoClient(self.HOST, self.PORT, self.DB_NAME)

    def get_price_seq_by_date(self, stock_no, begin_date, end_date): 
        res = {"ok":0}
        query = {
            "stock_no" : stock_no,
            "date" : {
                "$gte" : begin_date,
                "$lte" : end_date
            }
        }
        projection = {
            "close" : 1,
            "date"  : 1
        }
        data = self.mongo.find("origin", query, projection)
        if len(data)>0:
            res["ok"] = 1
            res["data"] = data
        return json.dumps(res)

    def get_price_seq(self, stock_no, end_date, seq_len):
        res = {"ok":0}
        query = {
            "stock_no" : stock_no,
            "date" : {
                "$lte" : end_date
            }
        }
        projection = {
            "close" : 1,
            "date" : 1
        }
        cursor = self.mongo.db["origin"].find(query, projection).sort("date", -1).limit(seq_len)
        data = list(cursor)
        i = 1
        for obj in data:
            obj["index"] = i
            date = obj["date"]
            obj["date"] = "%s-%s-%s"%(date[:4], date[4:6], date[6:])
            i += 1
            del obj['_id']

        if len(data)>0:
            res["ok"] = 1
            res["data"] = data
            res["xkey"] = "date"
            res["ykeys"] = ["close", ]
            res["labels"] = ["price", ]
        return json.dumps(res)

    def get_reg_by_date(self, date):
        res = {"ok":0}
        data = self.mongo.find("regression",{"date":date})
        if len(data)>0:
            res["ok"] = 1
            res["data"] = data[0]
        return json.dumps(res)

    def get_date_list(self):
        res = {"ok":0}
        cursor = self.mongo.db["regression"].distinct("date")
        data = list(cursor)
        if len(data)>0:
            res["ok"] = 1
            res["data"] = data
        return json.dumps(res)

    def reset_mongo(self, colname):
        self.mongo.drop(colname)

if __name__ == '__main__':
    reg = Regression()
    res = reg.get_price_seq("SZ000001", "20150101", 10)
    print res