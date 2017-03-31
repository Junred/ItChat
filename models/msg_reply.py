# coding=utf-8

from sqlalchemy import *

from . import BaseModel


class MsgReply(BaseModel):
    __tablename__ = 'MsgReply'

    TYPE_KEYWORDS_REPLY = 1
    TYPE_CHAT_ROOM_COUNT_REPLY = 2
    TYPE_KICK_KEYWORDS_REPLY = 3

    WxAccount = Column('WxAccount', String(64), index=True)
    Type = Column('Type', Integer, nullable=False)
    Condition = Column('Condition', String(128), nullable=False, index=True)
    _MsgIds = Column('MsgIds', String(256), nullable=False)

    @property
    def MsgIds(self):
        if len(self._MsgIds) == 0:
            return []
        return self._MsgIds.split(',')

    @MsgIds.setter
    def MsgIds(self, value):
        if len(value) > 0:
            self._MsgIds = ','.join(value)
        else:
            self._MsgIds = ''

    @classmethod
    def get_reply_type_name(cls, reply_type):
        if reply_type == cls.TYPE_KEYWORDS_REPLY:
            return '关键字'
        elif reply_type == cls.TYPE_CHAT_ROOM_COUNT_REPLY:
            return '群人数'
        elif reply_type == cls.TYPE_KICK_KEYWORDS_REPLY:
            return '踢人关键字'
        return 'unknown'

    @classmethod
    def add_reply(cls, wx_account, reply_type, condition, msg_ids, auto_commit=False):
        msg_reply_model = cls(WxAccount=wx_account, Type=reply_type, Condition=condition, MsgIds=msg_ids)
        if auto_commit:
            cls.add(msg_reply_model)
            cls.commit()
        return msg_reply_model
