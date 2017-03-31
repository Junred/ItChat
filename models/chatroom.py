# coding=utf-8
import base64
from sqlalchemy import *
from . import BaseModel


def encode_nickname(value):
    return value.encode('utf-8')


def decode_nickname(value):
    return value.decode('utf-8')


class ChatRoom(BaseModel):
    __tablename__ = 'ChatRoom'

    Uin = Column('Uin', String(64), index=True)
    WxAccount = Column('WxAccount', String(64), index=True)
    UserName = Column('UserName', String(256), index=True)
    _NickName = Column('NickName', Binary)
    IsManager = Column('IsManager', Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(Uin.name, WxAccount.name, name='uin_wx_account_unique_id'),
    )

    @property
    def NickName(self):
        return decode_nickname(self._NickName)

    @NickName.setter
    def NickName(self, value):
        self._NickName = encode_nickname(value)

    @classmethod
    def update_chat_room(cls, uin, wx_account, user_name, nick_name):
        room = cls.get_model_filter_by(WxAccount=wx_account, Uin=uin)
        if room is None:
            room = ChatRoom(Uin=uin, WxAccount=wx_account)
        room.UserName = user_name
        room.NickName = nick_name
        return room


class ChatRoomMember(BaseModel):
    __tablename__ = 'ChatRoomMember'

    ChatRoomUin = Column('ChatRoomUin', String(128), index=True)
    WxAccount = Column('WxAccount', String(64), index=True)
    UserName = Column('UserName', String(256), index=True)
    _NickName = Column('NickName', Binary)
    AttrStatus = Column('AttrStatus', BigInteger, index=True)
    Sex = Column('Sex', Integer, default=0)
    Province = Column('Province', String(128), default=None)
    City = Column('City', String(128), default=None)

    SendTextCount = Column('SendTextCount', Integer, default=0)
    SendImageCount = Column('SendImageCount', Integer, default=0)
    SendShareLinkCount = Column('SendShareLinkCount', Integer, default=0)
    SendOtherCount = Column('SendOtherCount', Integer, default=0)
    InviteCountCount = Column('InviteCount', Integer, default=0)

    @property
    def NickName(self):
        return decode_nickname(self._NickName)

    @NickName.setter
    def NickName(self, value):
        self._NickName = encode_nickname(value)

    def __init__(self, **kwargs):
        super(ChatRoomMember, self).__init__(**kwargs)
        self.SendTextCount = 0
        self.SendImageCount = 0
        self.SendShareLinkCount = 0
        self.SendOtherCount = 0
        self.InviteCountCount = 0

    @classmethod
    def update_member(cls, chatroom_uin, wx_account, user_name, nick_name, attr_status=0, sex=0, province=None,
                      city=None, auto_commit=False):
        members = cls.get_models_filter(cls.ChatRoomUin == chatroom_uin,
                                        cls.WxAccount == wx_account,
                                        or_(cls.UserName == user_name, cls._NickName == encode_nickname(nick_name)))
        member = None
        if members is not None and len(members) > 0:
            for model in members:
                if model.UserName == user_name:
                    member = model
                    break
                if model.AttrStatus == attr_status:
                    member = model
                    break
        if member is None:
            member = cls(ChatRoomUin=chatroom_uin, WxAccount=wx_account, UserName=user_name, NickName=nick_name,
                         AttrStatus=attr_status, Sex=sex, Province=province, City=city)
            if auto_commit:
                cls.add(member)
                cls.commit()

        return member

    @classmethod
    def del_member(cls, chatroom_uin, wx_account, user_name, nickname):
        model = cls.get_model_filter(cls.ChatRoomUin == chatroom_uin, cls.WxAccount == wx_account,
                                     or_(cls.UserName == user_name, cls._NickName == encode_nickname(nickname)))
        if model:
            cls.delete(model)
        return model
