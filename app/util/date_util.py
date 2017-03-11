from datetime import datetime,timedelta
def reformat_date(time_stamp,format="%Y%m%d%H%M%S"):
	time_stamp = datetime.strptime(time_stamp.strip(),format)
	return time_stamp.isoformat()

def get_js_date(start):
	return datetime.strptime(start[:-5],"%Y-%m-%dT%H:%M:%S")