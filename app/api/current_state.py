# -*- coding:utf-8 -*-
from app import redis_db
from app.models import test
from flask import abort, jsonify, request
from flask import current_app as app
import json
import os
from . import api
from auth import httpAuth
from app.util.date_util import reformat_date
from app.util.file_util import read_last_line

@api.route('/stock_monitor/account_info', methods = ['GET'])
@httpAuth.login_required
def get_account_num():
	print request.headers['Authorization']
	num = app.config["BASE_CONFIG"]["ACCOUNT_NUM"]
	info = [app.config["BASE_CONFIG"]["ACCOUNT"][key] for key in app.config["BASE_CONFIG"]["ACCOUNT"]]
	info.sort()
	return json.dumps({"account_num":num,"account_name":info})

@api.route('/stock_monitor/account_state/<account_name>', methods = ['GET'])
@httpAuth.login_required
def get_account_stat(account_name):
	file_dir = app.config["FILE_PATH"]
	filename = app.config["BASE_CONFIG"]["ACCOUNT_STAT_FILE"]
	filename = filename.replace("*",account_name)
	filename = os.path.join(file_dir, filename)
	try:
		f = open(filename)
	except Exception, e:
		print e
		return json.dumps({"ok":"0","error":e.args[1]})
	else:
		def map_line(line):
			line = line.strip()
			strs = line.split("\t")
			if len(strs)>4:
				return {
					"account_name":account_name,
					"title":strs[0],
					"position_buy":strs[1],
					"position_sell":strs[2],
					"position_buy_yesterday":strs[3],
					"position_sell_yesterday":strs[4]
					}
			else:
				return None

		res = [map_line(line) for line in f]
		f.close()
		return json.dumps({"ok":"1","account_state":res})

@api.route('/stock_monitor/balance', methods = ['GET'])
@httpAuth.login_required
def get_balance():
	file_dir = app.config["FILE_PATH"]
	filename = app.config["BASE_CONFIG"]["BALANCE_FILE"]
	filename = os.path.join(file_dir, filename)
	account_name_list = [app.config["BASE_CONFIG"]["ACCOUNT"][key] for key in app.config["BASE_CONFIG"]["ACCOUNT"]]
	balance = []
	res = {}
	def map_line(line):
		if not line:
			return None
		line = line.strip()
		strs = line.split("\t")
		if len(strs)>1:
			return {
				"account_name":account_name,
				"time":reformat_date(strs[0]),
				"fund":strs[1]
				}
		else:
			return None
	for account_name in account_name_list:
		line = read_last_line(filename.replace("*",account_name))
		data = map_line(line)
		if data:
			balance.append(data)
	res["table"] = {"table_head":[
                    "账户名",
                    "时间",
                    "资金"
                ],
                "table_name":[
                    "account_name",
                    "time",
                    "fund"
			]}
	res["ok"] = 1
	res["balance"] = balance
	return json.dumps(res)
	

@api.route('/stock_monitor/strategy-state', methods = ['GET'])
@httpAuth.login_required
def get_strategy_state():
	file_dir = app.config["FILE_PATH"]
	filename = app.config["BASE_CONFIG"]["STRATEGY_STAT_FILE"]
	filename = os.path.join(file_dir, filename)
	try:
		f = open(filename)
		# 接下来每行格式：交易状态码	策略状态码	策略程序存活（0死/1活）	策略交易开关（0关/1开） 手工交易开关（0关/1开）
		res = {}
		time_stamp = f.readline()
		time_stamp = reformat_date(time_stamp)
		res["time_stamp"] = time_stamp
		def map_line(line):
			line = line.strip()
			strs = line.split("\t")
			if len(strs)>1:
				return {
					"account_name":strs[0],
					"trade_code":strs[1],
					"strategy_code":strs[2],
					"strategy_alive":strs[3],
					"strategy_switch":strs[4],
					"hand_switch":strs[5],
					"time_stamp":time_stamp
					}
			else:
				return {
					"account_name":"?",
					"trade_code":"?",
					"strategy_code":0,
					"strategy_alive":0,
					"strategy_switch":0,
					"hand_switch":0,
					"time_stamp":0
					}
		res["state"] = [map_line(line) for line in f]
		f.close()
	except Exception, e:
		print e
		return json.dumps({"ok":"0","error":e.args[1]})
	else:
		res["ok"] = 1
		res["table"] = {"table_head":[
					"账户名",
                    "策略程序存活（0死/1活)",
                    "交易状态码",
                    "策略状态码",
                    "策略交易开关（0关/1开)",
                    "手工交易开关（0关/1开)",
                    "时间戳"
					],"table_name":[
					"account_name",
                    "strategy_alive",
                    "trade_code",
                    "strategy_code",
                    "hand_switch",
                    "strategy_switch",
                    "time_stamp"
					]}
		return json.dumps(res)


@api.route('/stock_monitor/trader-state', methods = ['GET'])
@httpAuth.login_required
def get_trader_state():
	file_dir = app.config["FILE_PATH"]
	filename = app.config["BASE_CONFIG"]["TRADER_STAT_FILE"]
	filename = os.path.join(file_dir, filename)
	try:
		f = open(filename)
		res = {}
		time_stamp = f.readline()
		time_stamp = reformat_date(time_stamp)
		res["time_stamp"] = time_stamp
		state_list = []
		for line in f:
			line = line.strip()
			key = line.split('\t')[0]
			value = line.split('\t')[1]
			state_list.append({"account_name":key,"state":value,"time_stamp":time_stamp})
		res["state"] = state_list
		f.close()
	except Exception, e:
		print e
		return json.dumps({"ok":0,"error":e.args[1]})
	else:
		res["ok"]=1
		res["table"] = {"table_head":[
		            "账户名",
                    "状态",
                    "时间戳"
					],"table_name":[
					"account_name",
                    "state",
                    "time_stamp"
					]}
		return json.dumps(res)







