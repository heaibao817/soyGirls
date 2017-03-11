# -*- coding: utf-8 -*-
import chardet
import datetime
import re
import os

class SeekError(Exception):
    """docstring for SeekError"""
    def __init__(self, value):
        super(SeekError, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)
        
def read_last_line(filename,buffer_size=60):
    res = read_last_n_line(filename,1,buffer_size)
    if res and len(res)>0:
        return res[0]
    else:
        return res

def read_last_n_line(filename,n,buffer_size=120):
    res = None
    shouldContinue = True
    try:
        f = open(filename)
        f.seek(0,2)
        offset = seek_end = f.tell()
        while shouldContinue:
            if buffer_size > seek_end:
                offset = seek_end
            else:
                offset = buffer_size
            f.seek(offset,0)
            lines = [line for line in f]
            if (len(lines)>n) or (offset==seek_end):
                if offset==seek_end:
                    res = lines
                else:
                    res = lines[-n:]
                shouldContinue = False
            else:
                buffer_size *= 2
        f.close()
    except Exception, e:
        print e
    return res

def seek_safely(f,seek):
    f.seek(0,2)
    seek_end = f.tell()
    if seek > seek_end:
        f.seek(0,0)
        raise SeekError("seek %s is larger than seek_end %s"%(seek,seek_end))
    else:
        f.seek(seek,0)

def to_utf8(line):
    res = chardet.detect(line)
    confidence = res["confidence"]
    if confidence<0.8:
        encoding = "gb2312"
    else:
        encoding = res["encoding"]
    s = line.decode(encoding)
    return s.encode("utf-8")

def get_stock_no(id_stock):
    id_stock = int(id_stock)
    if (id_stock==700001): #貌似没有
        return "SH000001"
    else:
        if (id_stock>=600000): # 沪市
            return "SH%06ld"%id_stock
        else:
            return "SZ%06ld"%id_stock

def get_stock_id(stock_fname):
    fname_text = os.path.splitext(stock_fname)[0]
    stock_id = int(fname_text[2:])
    return stock_id

def generate_stock_json(input_name):
    res = []
    date_format = lambda date:datetime.datetime.strptime(date,'%m/%d/%Y').strftime('%Y%m%d')
    try:
        f = open(input_name)
        f.readline()
        f.readline()
        fname = os.path.split(input_name)[-1] # SH00001.txt
        stock_no = os.path.splitext(fname)[0] # SH00001
        id_stock = get_stock_id(fname) # 1
        KEY_LIST = ["id_stock","stock_no","date","open","max","min","close","trade_volumn","trade_money"]
        HEAD_LIST = [id_stock, stock_no]
        pattern = re.compile('\d{2}/\d{2}/\d{4}\t.*')
        for line in f:
            line = to_utf8(line)
            if pattern.match(line): 
                line = line.replace('\r\n','')
                values = HEAD_LIST + line.split('\t')
                item = dict(zip(KEY_LIST, values))
                item["date"] = date_format(item["date"])
                res.append(item)
    except Exception, e:
        print e
        return []
    return res

def get_predict_json(input_name):
    res = []
    try:
        f = open(input_name)
        f.readline()
        fname = os.path.split(input_name)[-1]
        for line in f:
            strs = line.split('\t')
            if len(strs)>5:
                stock_id = strs[5]
                stock_no = get_stock_no(stock_id)
                score = strs[6]
                item = {"stock_id":stock_id,"stock_no":stock_no,"date":fname,"5_day_3":score}
                res.append(item)
    except Exception, e:
        print e
        return []
    return res

def get_stock_json_by_stockno(data_dir, id_stock):
    stock_no = get_stock_no(id_stock)
    input_name = os.path.join(data_dir, stock_no+".txt")
    return generate_stock_json(input_name)
