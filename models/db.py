# coding=utf-8
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import scoped_session, sessionmaker

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'wxbot'
MYSQL_PWD = 'wxbot20170323'
MYSQL_DB = 'wxbot'
MYSQL_CHARSET = 'utf8mb4'
ECHO = False

db_url = "mysql+pymysql://{0}:{1}@{2}/{3}?charset={4}&use_unicode=1".format(MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB, MYSQL_CHARSET)
engine = sqlalchemy.create_engine(db_url, convert_unicode=True)

db_session = sessionmaker(bind=engine)
session = scoped_session(db_session)
