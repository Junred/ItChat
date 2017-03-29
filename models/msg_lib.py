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

    WxAccount = Column('WxAccount', String(64), nullable=False, index=True)
    Type = Column('Type', String(32), nullable=False)
    Content = Column('Content', TEXT, nullable=False)

    @classmethod
    def add_msg(cls, wx_account, msg_type, content, auto_commit=False):
        msg = cls(WxAccount=wx_account, Type=msg_type, Content=content)
        if auto_commit:
            cls.add(msg)
            cls.commit()

        return msg
