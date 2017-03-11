# -*- coding:utf-8 -*-
from app import redis_db
from app.models import test
from flask import abort, jsonify, request
from flask import current_app as app
import datetime
import json
from datetime import datetime,timedelta
import os
from . import api
from auth import httpAuth
from app.util.date_util import reformat_date,get_js_date
from app.util.file_util import to_utf8
from app.models.history import Log,TradeHist,Settlement,Balance

@api.route('/stock_monitor/plot-fund/date', methods = ['GET'])
def get_plot_date():
	try:
		start = get_js_date(request.args.get("start"))
		end = get_js_date(request.args.get("end"))
	except Exception, e:
		print e
		start = datetime.today()
		end = start
	service = Settlement()
	# res = service.get_data_all()
	res = service.get_data_all_by_time(start.isoformat(),end.isoformat())
	res["ok"] = 1
	return json.dumps(res)

@api.route('/stock_monitor/plot-fund/hour', methods = ['GET'])
def get_plot_hour():
	try:
		start = get_js_date(request.args.get("start"))
		end = get_js_date(request.args.get("end"))
	except Exception, e:
		print e
		start = datetime.today()
		end = start
	service = Balance()
	# res = service.get_data_all()
	res = service.get_data_all_by_time(start.isoformat(),end.isoformat())
	res["ok"] = 1
	return json.dumps(res)

@api.route('/stock_monitor/system-log/<account_name>/<skip>/<limit>', methods = ['GET'])
def get_log(account_name,skip,limit):
	service = Log()
	try:
		start = get_js_date(request.args.get("start"))
		end = get_js_date(request.args.get("end"))
		level_data = request.args.get('level')
		level_data = json.loads(level_data)
		level_list = [key for key in level_data.keys() if level_data[key]]
		query = {"level":{"$in":level_list},"time_stamp":{"$gte":start.isoformat(),"$lte":end.isoformat()}}
	except Exception, e:
		query = None
	res = service.get_data(account_name,query,skip,limit)
	if res["ok"]==1:
		res["table"] = {"table_head":[
					"账户名",
					"级别",
                    "时间戳",
                    "来源",
                    "内容"
					],"table_name":[
					"account_name",
					"level",
                    "time_stamp",
                    "source",
                    "content"
					]}
	return json.dumps(res)

@api.route('/stock_monitor/trade-hist/<account_name>/<skip>/<limit>', methods = ['GET'])
def get_traded_hist(account_name,skip,limit):
	service = TradeHist()
	try:	
		start = get_js_date(request.args.get("start"))
		end = get_js_date(request.args.get("end"))
		query = {"time_stamp":{"$gte":start.isoformat(),"$lte":end.isoformat()}}
	except Exception, e:
		query = None
	res = service.get_data(account_name,query,skip,limit)
	res["ok"]=1
	res["table"] = {"table_head":[
				"账户名",
				"合约",
                "买(B)/卖(S)",
                "开仓(O)/平仓(C)",
                "成交价",
                "手数",
                "成交时间"
				],"table_name":[
				"account_name",
				"title",
                "bs",
                "oc",
                "price",
                "amount",
                "time_stamp"
				]}
	return json.dumps(res)