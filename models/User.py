# coding: utf-8
"""
用户信息
    账号
    密码
    昵称
"""
import bcrypt
from sqlalchemy import *
from . import BaseModel


class User(BaseModel):

    __tablename__ = 'User'

    # 管理愿用户，可以管理其他用户
    USER_TYPE_ADMIN = 1
    # 普通用户
    USER_TYPE_NORMAL = 2

    Name = Column('Name', String(64), nullable=False, unique=True)
    _Pwd = Column('Pwd', String(64), nullable=False)
    NickName = Column('NickName', String(64), nullable=False)
    UserType = Column('UserType',SmallInteger, nullable=False, default=USER_TYPE_NORMAL)

    @property
    def password(self):
        return self._Pwd

    @password.setter
    def password(self, pwd):
        self._Pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, pwd):
        return bcrypt.checkpw(pwd.encode('utf-8'), self.password)

    @classmethod
    def add_user(cls, name, nickname, user_type, pwd, auto_commit=False):
        user = cls(Name=name, NickName=nickname, password=pwd, UserType=user_type)
        if user and auto_commit:
            cls.save([user])
        return user
