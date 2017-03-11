import sys
sys.path.append(".")
sys.path.append("../")
sys.path.append("../../")
import json
import tensorflow as tf
import numpy as np
from app.util.mongo_util import MongoClient
class Network(object):
    def __init__(self):
        self.HOST = "10.0.1.111"
        self.PORT = 27017
        self.DB_NAME = "stock"
        self.mongo = MongoClient(self.HOST, self.PORT, self.DB_NAME)

    def get_network(self, net_name):
    	res = {"ok":0}
    	data = self.mongo.find("netpool", {"net_name":net_name})
    	if len(data) >0:
    		res["data"] = data[0]
    		res["ok"] = 1
     	return json.dumps(res)