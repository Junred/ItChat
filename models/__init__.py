# coding: utf-8
from datetime import datetime
from sqlalchemy import *
import sqlalchemy.ext.declarative
from . import db

_base = sqlalchemy.ext.declarative.declarative_base()


class BaseModel(_base):

    __abstract__ = True

    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    Id = Column('Id', Integer, primary_key=True, autoincrement=True)
    Status = Column('Status', SmallInteger, default=0)
    CreateTime = Column('CreateTime', DateTime, nullable=False, server_default=func.now())
    UpdateTime = Column('UpdateTime', DateTime, onupdate=func.now())

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in v:
                raise RuntimeError('not found {0} attribute'.format(k))
            setattr(self, k, v)

    @classmethod
    def get_model_by_id(cls, model_id):
        return db.session.query(cls).get(model_id)

    @classmethod
    def get_model_filter(cls, *args):
        return db.session.query(cls).filter(*args).one()

    @classmethod
    def get_model_filter_by(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs).one()

    @classmethod
    def get_models_filter(cls, *args):
        return db.session.query(cls).filter(*args).all()

    @classmethod
    def get_models_filter_by(cls, **kwargs):
        return db.session.qeury(cls).filter_by(**kwargs).all()

    @staticmethod
    def add(model):
        db.session.add(model)

    @staticmethod
    def merge(model):
        db.session.merge(model)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def begin_transaction():
        db.session.begin()
