from flask import abort, jsonify, request, g
from flask_httpauth import HTTPTokenAuth
import hashlib
from app import db
from app.models.user import User
from . import api


ERROR_ILLEGAL_REQUEST = "illegal request"
ERROR_USER_EXIST = "username exists"
ERROR_NO_SUCH_USER = "no such user"
ERROR_PWD = "wrong password"

httpAuth = HTTPTokenAuth("token")



# @api.route('/stock_monitor/register', methods = ['POST'])
# def register():
# 	username = request.json['username']
# 	if (not username) or (get_user(username) == None):
# 		return ERROR_USER_EXIST, 405
# 	entity = User(
# 		username = username
# 		, passwd = request.json['passwd']
# 	)
# 	db.session.add(entity)
# 	db.session.commit()
# 	return jsonify({"username":username,"ok":1}), 201

@httpAuth.verify_token
def verify_token(token):
	print "token:%s"%token
	if token == '':
		g.current_user = None
		return False
	user = User.verify_auth_token(token)
	if not user:
		return False
	g.current_user = user
	return True

@api.route('/stock_monitor/login', methods = ['POST'])
def login():
	data = request.args
	if not data:
		print request
		return jsonify({"ok":0,"err":ERROR_ILLEGAL_REQUEST})
	username = data.get('username')
	passwd = data.get('password')
	user = User.get_user(username)
	if not user:
		return jsonify({"ok":0,"err":ERROR_NO_SUCH_USER})
	if user.check_passwd(passwd):
		token = user.generate_auth_token()
		return jsonify({"ok":1,"username":username,"token":token})
	else:
		return jsonify({"ok":0,"err":ERROR_PWD})
