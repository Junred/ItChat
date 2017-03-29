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
    UpdateTime = Column('UpdateTime', DateTime, onupdate=func.now(), server_default=func.now())

    # @classmethod
    # def __init__(cls, **kwargs):
    #     for k, v in kwargs.items():
    #         if k not in v:
    #             raise RuntimeError('not found {0} attribute'.format(k))
    #         setattr(cls, k, v)

    @classmethod
    def get_model_by_id(cls, model_id):
        return db.session.query(cls).get(model_id)

    @classmethod
    def get_model_filter(cls, *args):
        return db.session.query(cls).filter(*args).first()

    @classmethod
    def get_model_filter_by(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_models_filter(cls, *args):
        return db.session.query(cls).filter(*args).all()

    @classmethod
    def get_models_filter_by(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def clear_all(cls):
        db.session.query(cls).delete()
        cls.commit()

    @staticmethod
    def add(model):
        db.session.add(model)

    @staticmethod
    def delete(model, auto_commit=False):
        db.session.delete(model)
        if auto_commit:
            BaseModel.commit()

    @staticmethod
    def merge(model):
        db.session.merge(model)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def begin_transaction():
        db.session.begin()

    @staticmethod
    def save(models, auto_commit=True):
        if not isinstance(models, list):
            models = [models,]
        for model in models:
            db.session.add(model)
        if auto_commit:
            db.session.commit()

from . import chatroom, msg_lib, robot, task, user, msg_reply
