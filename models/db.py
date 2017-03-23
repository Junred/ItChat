# coding: utf-8
import sqlalchemy
import sqlalchemy.orm

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'bot'
MYSQL_PWD = 'wxbot@2017'
MYSQL_DB = 'wxbot'
MYSQL_CHARSET = 'utf-8'
ECHO = False

engine = sqlalchemy.create_engine(
    "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_PWD, MYSQL_DB),
    encoding=MYSQL_CHARSET,
    echo=False)

db_session = sqlalchemy.orm.sessionmaker(bind=engine)
session = db_session()
