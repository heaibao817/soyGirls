from flask import url_for
from . import api
from app.models.regression import Regression
from app.models.cnn import Network

service = Regression()
cnn = Network()
@api.route('/')
def root():
    print url_for('api.static', filename='css/app.css')
    return api.send_static_file('index.html')

@api.route('/api/datelist')
def datelist():
    return service.get_date_list()

@api.route('/api/reg/<date>')
def regression(date):
    date = int(date)
    return service.get_reg_by_date(date)

@api.route('/api/price_seq_by_len/<stock_no>/<end_date>/<seq_len>')
def price_seq(stock_no, end_date, seq_len):
    seq_len = int(seq_len)
    return service.get_price_seq(stock_no, end_date, seq_len)

@api.route('/api/network')
def get_network():
    return cnn.get_network("net_pool/stack2/14_15_test_5_1478610181.t7")