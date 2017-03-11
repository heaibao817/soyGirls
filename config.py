import os
basedir = os.path.abspath(os.path.dirname(__file__))

SALT = "stock_monitor"
SECRET_KEY = "bmyy,qmwk"
EXPIRE = 3600 # expire time of a token (unit:s)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
REDIS_PORT = 6379
REDIS_HOST = "localhost"
MONGO_HOST = "10.0.1.232"
MONGO_PORT = 27017
MONGO_USER = "admin"
MONGO_PASS = "hpc1234"
MONGO_DB_NAME = "stock"

FILE_PATH =	"C:\Users\liuyn\Desktop\\trader_exec\log"
# FILE_PATH = os.path.join(basedir,"examples")