from . import api
from app import db
from app.models import test
from flask import abort, jsonify, request
import datetime
import json

@api.route('/stock_monitor/tests', methods = ['GET'])
def get_all_tests():
    entities = test.Test.query.all()
    return json.dumps([entity.to_dict() for entity in entities])

@api.route('/stock_monitor/tests/<int:id>', methods = ['GET'])
def get_test(id):
    entity = test.Test.query.get(id)
    if not entity:
        abort(404)
    return jsonify(entity.to_dict())

@api.route('/stock_monitor/tests', methods = ['POST'])
def create_test():
    entity = test.Test(
        user = request.json['user']
        , passwd = request.json['passwd']
    )
    db.session.add(entity)
    db.session.commit()
    return jsonify(entity.to_dict()), 201

@api.route('/stock_monitor/tests/<int:id>', methods = ['PUT'])
def update_test(id):
    entity = test.Test.query.get(id)
    if not entity:
        abort(404)
    entity = test.Test(
        user = request.json['user'],
        passwd = request.json['passwd'],
        id = id
    )
    db.session.merge(entity)
    db.session.commit()
    return jsonify(entity.to_dict()), 200

@api.route('/stock_monitor/tests/<int:id>', methods = ['DELETE'])
def delete_test(id):
    entity = test.Test.query.get(id)
    if not entity:
        abort(404)
    db.session.delete(entity)
    db.session.commit()
    return '', 204
