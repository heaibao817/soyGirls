# -*- coding:utf-8 -*-
from flask import current_app as app

from app.util.date_util import reformat_date
from app.util.mongo_util import MongoClient
from app.util.file_util import to_utf8, seek_safely
import os
import datetime
import json
import chardet
import traceback
from datetime import datetime,timedelta

class History(object):
	"""docstring for History"""
	def __init__(self):
		super(History, self).__init__()
		self.HOST = host = app.config["MONGO_HOST"]
		self.PORT = port =  app.config["MONGO_PORT"]
		self.DB_NAME = db = app.config["MONGO_DB_NAME"]
		user = app.config["MONGO_USER"]
		password = app.config["MONGO_PASS"]
		self.mongo = MongoClient(host, int(port), db, user, password)
		self.typename = ""

	def get_all_accounts(self):
		return [app.config["BASE_CONFIG"]["ACCOUNT"][key] for key in app.config["BASE_CONFIG"]["ACCOUNT"]]

	def get_fname(self,account_name):
		file_dir = app.config["FILE_PATH"]
		filename = app.config["BASE_CONFIG"].get(self.typename)
		if account_name:
			fname = filename.replace("*",account_name)
			return os.path.join(file_dir, fname)
		return filename


	def _insert_update_meta(self,col,seek,m_time):
		res = self.mongo.update("meta",{"col":col},{"$set":{"col":col,"seek":seek,"m_time":m_time},
			"$currentDate":{"time_stamp":True}},upsert=True)
		return res

	def _check_update(self,colname,filename):
		cached_modify_time = 0
		seek = 0
		meta = self.mongo.find("meta",{"col":colname})
		if len(meta)>0:
			cached_modify_time = meta["m_time"][0]
			seek = meta["seek"][0]
		modify_time = os.stat(filename).st_mtime
		print "@_check_update",cached_modify_time,modify_time,seek
		return (int(cached_modify_time) < int(modify_time),seek)

	def reset_mongo(self,account_name):
		self.mongo.drop(self.col_template%account_name)
		self.mongo.remove("meta",{"col":self.col_template%account_name})

	def mongo_import_log(self,account_name, seek = 0):
		print "mongo_import_log",account_name
		res = self._get_from_file(account_name,seek)
		if res["ok"]==1:
			if seek==0:
				self.reset_mongo(account_name)
			res["objectIds"] = self.mongo.insert_many(self.col_template%account_name,res["data"])
			self._insert_update_meta(self.col_template%account_name,res["seek"],res["m_time"])
			del res["data"]
			return res
		else:
			return res

class Settlement(History):
	"""docstring for Settlement"""
	def __init__(self):
		super(Settlement, self).__init__()
		self.col_template = "settlement_%s"
		self.typename = "SETTLEMENT_FILE"

	def get_data(self,account_name,query=None):
		return self._get_from_mongo_all(account_name)

	def get_data_all(self,query=None):
		return self._get_from_mongo_all(query)

	def get_data_all_by_time(self,start_time,end_time):
		query = {"time":{"$gte":start_time,"$lte":end_time}}
		return self._get_from_mongo_all(query)

	def _get_from_mongo_all(self,query):
		map_all = {}
		time_list = []
		account_name_list = self.get_all_accounts()
		account_name_list.sort()
		for account_name in account_name_list:
			res = self._get_from_mongo(account_name,query)
			my_dict = {}
			if res["ok"]==1:
				for item in res["data"]:
					my_dict[item["time"]] = item["value"]
			map_all[account_name] = my_dict
			time_list.extend(map_all[account_name].keys())
		# calculate total
		total_data = []
		data = []
		time_list = list(set(time_list))
		time_list.sort()
		for time in time_list:
			record = {"time":time}
			total_fund = 0
			for account_name in account_name_list:
				if map_all[account_name].has_key(time):
					val = float(map_all[account_name][time])
					total_fund += val
					record[account_name] = val
			data.append(record)
			total_data.append({"time":time,"total":total_fund})
		return {"xkey":"time",
		"data":data,"labels":account_name_list,"ykeys":account_name_list,
		"total_data":total_data,"total_labels":['total'],"total_ykeys":['total']}

	def _get_from_mongo(self,account_name,query):
		res = {"ok":0}
		try:
			(isUpdate,seek) = self._check_update(self.col_template%account_name,self.get_fname(account_name))
			if isUpdate:
				self.mongo_import_log(account_name,seek)
			col = self.col_template%account_name
			df = self.mongo.find(col,query)
			if len(df)>0:
				res["ok"] = 1
				res["data"] = df.to_dict('records')
		except Exception, e:
			traceback.print_exc()
			print e
			return {"ok":0,"error":e}
		return res
		

	def _get_from_file(self,account_name,seek=0):
		data = []
		res = {"ok":1}
		try:
			filename = self.get_fname(account_name)
			f = open(filename)
			seek_safely(f,seek)
			for line in f:
				line = line.strip()
				strs = line.split("\t")
				if len(strs)==2:
					date = reformat_date(strs[0],"%Y%m%d")
					data.append({"time":date,"value":strs[1]})
			res["m_time"] = os.stat(self.get_fname(account_name)).st_mtime
			res["seek"] = f.tell()
			res["data"] = data
			f.close()
		except Exception, e:
			traceback.print_exc()
			print e
			return {"ok":0,"error":e}
		return res

class Balance(Settlement):
	"""docstring for Balance"""
	def __init__(self):
		super(Balance, self).__init__()
		self.col_template = "balance_%s"
		self.typename = "BALANCE_FILE"

	def _get_from_file(self,account_name,seek=0):
		data = []
		date_value_map = {}
		res = {"ok":1}
		try:
			filename = self.get_fname(account_name)
			f = open(filename)
			seek_safely(f,seek)
			for line in f:
				line = line.strip()
				strs = line.split("\t")
				if len(strs)==2:
					time_stamp = datetime.strptime(strs[0],"%Y%m%d%H%M%S")
					time = time_stamp.strftime("%Y-%m-%dT%H:00:00")
					if not date_value_map.has_key(time):
						data.append({"time":time,"value":strs[1]})
						date_value_map[time] = strs[1]
			res["m_time"] = os.stat(self.get_fname(account_name)).st_mtime
			res["seek"] = f.tell()
			res["data"] = data
			f.close()
		except Exception, e:
			traceback.print_exc()
			print e
			return {"ok":0,"error":e}
		return res

class Log(History):
	"""docstring for Log"""
	def __init__(self):
		super(Log, self).__init__()
		self.col_template = "log_%s"
		self.typename = "LOG_FILE"

	def get_data(self,account_name,query=None,skip=10,limit=10):
		return self._get_from_mongo(account_name,query,int(skip),int(limit))

	def _get_from_mongo(self,account_name,query,skip,limit):
		col = self.col_template%account_name
		(isUpdate,seek) = self._check_update(self.col_template%account_name,self.get_fname(account_name))
		if isUpdate:
			self.mongo_import_log(account_name,seek)
		res = {"ok":0}
		sort_rule = [("time_stamp",-1),("level",1)]
		count = self.mongo.count(col,query)
		data = self.mongo.find_slice(col,query,sort_rule,skip,limit)
		if len(data)>0:
			res["ok"] = 1
			res["data"] = data
			res["count"] = int(count)
			res["skip"] = skip
			res["limit"] = limit
		return res

	def _get_from_file(self,account_name, seek = 0):
		try:
			filename = self.get_fname(account_name)
			f = open(filename)
			seek_safely(f,seek)
			res = {}
			log_list = []
			for line in f:
				line = line.strip()
				line = to_utf8(line)
				strs = line.split("\t")
				if len(strs)==4:
					log_list.append({"account_name":account_name,"level":strs[0],"time_stamp":reformat_date(strs[1]),"source":strs[2],"content":strs[3]})
				else:
					log_list.append({"account_name":account_name,"level":"W", "source":"Unkonwn","time_stamp":"Unkonwn","content":line})
			res["m_time"] = os.stat(self.get_fname(account_name)).st_mtime
			res["seek"] = f.tell()
			res["data"] = log_list
			f.close()
		except Exception, e:
			traceback.print_exc()
			return {"ok":0,"error":e.args[1]}
		else:
			res["ok"]=1
			return res
		
class TradeHist(Log):
	"""docstring for TradeHist"""
	def __init__(self):
		super(TradeHist, self).__init__()
		self.col_template = "tradehist_%s"
		self.typename = "TRADED_HIST"

	def _get_from_file(self,account_name, seek = 0):
		try:
			filename = self.get_fname(account_name)
			f = open(filename)
			seek_safely(f,seek)
			res = {}
			state_list = []
			for line in f:
				line = line.strip()
				line = to_utf8(line)
				strs = line.split("\t")
				if len(strs)==6:
					state_list.append({"account_name":account_name,"title":strs[0],"bs":strs[1],
						"oc":strs[2],"price":strs[3],"amount":strs[4],
						"time_stamp":reformat_date(strs[5])})
				else:
					state_list.append({"account_name":account_name,"title":"?", "bs":"?",
						"oc":"?","bs":"?","price":"","amount":line,
						"time_stamp":"?"})
			res["m_time"] = os.stat(self.get_fname(account_name)).st_mtime
			res["seek"] = f.tell()
			res["data"] = state_list
			f.close()
		except Exception, e:
			traceback.print_exc()
			return {"ok":0,"error":e.args[1]}
		else:
			res["ok"]=1
			return res		

