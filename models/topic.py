# coding: utf-8
"""
 主题  其他消息以这个主题为主
    主题ID
    主题名称
    所属用户
"""
from sqlalchemy import *
from . import BaseModel


class Topic(BaseModel):

    __tablename__ = 'Topic'

    UserId = Column('UserId', Integer, index=True)
    TopicName = Column('TopicName', String(128), unique=True)

    @classmethod
    def add_topic(cls, user_id, name, auto_commit=False):
        topic = cls(UserId=user_id, TopicName=name)
        if auto_commit:
            cls.save([topic], auto_commit=True)
        return topic
