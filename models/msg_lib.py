# coding: utf-8
"""
 消息库
    消息ID
    消息类型
    消息内容
"""
from sqlalchemy import *
from . import BaseModel


class Msg(BaseModel):
    __tablename__ = 'MsgLib'

    TYPE_TEXT = 1
    TYPE_IMAGE = 2

    Type = Column('Type', Integer, nullable=False)
    Content = Column('Content', TEXT, nullable=False)

    @classmethod
    def add_msg(cls, msg_type, content):
        msg = cls(Type=msg_type, Content=content)
        return msg
