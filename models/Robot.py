# coding: utf-8
""""
    机器人信息

    机器人ID
    机器人对应微信号
    机器人所属用户ID
    微信登录二维码
    二维码有效期
    状态
    状态持续最后更新时间
"""
from sqlalchemy import *
from . import BaseModel


class Robot(BaseModel):
    __tablename__ = 'Robot'

    STATUS_STOPPED = 0
    STATUS_WAIT_START = 1
    STATUS_WAIT_LOGIN = 2
    STATUS_WAIT_INIT = 3
    STATUS_STARTED = 4

    WxAccount = Column('WxAccount', String(32), nullable=False, unique=True)
    UserId = Column('UserId', Integer, index=True)
    LoginQrUrl = Column('LoginQrUrl', String(32), nullable=True)

    @classmethod
    def add_robot(cls, wx_account, user_id):
        robot = cls(WxAccount=wx_account, UserId=user_id)
        return robot

    def start(self):
        self.Status = self.STATUS_WAIT_START

    def logined(self):
        self.Status = self.STATUS_WAIT_INIT

    def inited(self):
        self.Status = self.STATUS_STARTED

    def stop(self):
        self.Status = self.STATUS_STOPPED

    def started(self):
        return self.Status == self.STATUS_STARTED
