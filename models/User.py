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

    Name = Column('Name', String(64), nullable=False, unique=True)
    _Pwd = Column('Pwd', String(64), nullable=False)
    NickName = Column('NickName', String(64), nullable=False)

    @property
    def password(self):
        return self._Pwd

    @password.setter
    def password(self, pwd):
        self._Pwd = bcrypt.hashpw(pwd, bcrypt.gensalt())

    def check_password(self, pwd):
        return bcrypt.checkpw(pwd, self.password)

    @classmethod
    def add_user(cls, name, nickname, pwd):
        user = cls(Name=name, NickName=nickname)
        user.password = pwd
        return user
