# coding: utf-8
""""
    机器人信息

    机器人ID
    机器人对应微信号
    机器人所属用户ID
    微信登录二维码 只有在等待启动时有效
    机器人类型
    机器人功能列表
    状态
    状态持续最后更新时间
"""
import datetime
from sqlalchemy import *
from . import BaseModel


class Robot(BaseModel):
    __tablename__ = 'Robot'

    # 机器人状态
    STATUS_STOPPED = 0
    STATUS_WAIT_START = 1
    STATUS_WAIT_SCAN = 2
    STATUS_WAIT_LOGIN = 3
    STATUS_WAIT_INIT = 4
    STATUS_STARTED = 5

    # 机器人功能
    FUNCTION_TYPE_CREATE_ROBOT = 1
    FUNCTION_TYPE_REPLY_MSG = 2
    FUNCTION_TYPE_KICK_OUT = 3
    FUNCTION_TYPE_GROUP_SEND = 4
    FUNCTION_TYPE_STATISTICS = 5
    FUNCTION_TYPE_CHAT_ROBOT = 6
    FUNCTION_TYPE_CREATE_TOPIC = 7

    # 同一个用户下可见
    UserId = Column('UserId', Integer, index=True)
    WxAccount = Column('WxAccount', String(64), index=True)
    TopicId = Column('TopicId', Integer, nullable=False)
    NickName = Column('NickName', String(64), nullable=False)
    LoginQrUrl = Column('LoginQrUrl', String(256), nullable=True)
    _RobotFunctions = Column('RobotFunctions', String(128), nullable=False)
    Pid = Column('Pid', String(16), nullable=True)

    @property
    def RobotFunctions(self):
        if len(self._RobotFunctions) == 0:
            return []
        return self._RobotFunctions.split(',')

    @RobotFunctions.setter
    def RobotFunctions(self, values):
        self._RobotFunctions = ','.join(map(str, values))

    @classmethod
    def add_robot(cls, wx_account, user_id, topic_id, nickname, robot_functions, auto_commit=False):
        robot = cls(WxAccount=wx_account, TopicId=topic_id, UserId=user_id, NickName=nickname, RobotFunctions=robot_functions)
        if robot and auto_commit:
            cls.save([robot])
        return robot

    def add_function(self, function_type):
        func_list = self.RobotFunctions
        if str(function_type) not in func_list:
            func_list.append(str(function_type))
            self.RobotFunctions = func_list
        return True

    def del_function(self, function_type):
        func_list = self.RobotFunctions
        if str(function_type) in func_list:
            func_list.remove(str(function_type))
            self.RobotFunctions = func_list

    def check_function(self, function_type):
        return str(function_type) in self.RobotFunctions

    def start(self):
        self.Status = self.STATUS_WAIT_START
        self.LoginQrUrl = None

    def wait_scan(self, login_url):
        self.Status = self.STATUS_WAIT_SCAN
        self.LoginQrUrl = login_url

    def is_wait_scan(self):
        if self.Status != self.STATUS_WAIT_SCAN:
            return False
        if not self.LoginQrUrl:
            return False
        if datetime.datetime.now() - self.UpdateTime >= datetime.timedelta(minutes=5):
            return False
        return True

    def logined(self):
        self.Status = self.STATUS_WAIT_INIT

    def inited(self):
        self.Status = self.STATUS_STARTED

    def stop(self):
        self.Status = self.STATUS_STOPPED
        self.Pid = None
        self.LoginQrUrl = None

    def started(self):
        return self.Status == self.STATUS_STARTED and func.now() - self.UpdateTime <= datetime.timedelta(minutes=1)

    def get_status(self):
        if self.Status == self.STATUS_WAIT_SCAN and datetime.datetime.now() - self.UpdateTime >= datetime.timedelta(minutes=5):
            return self.STATUS_WAIT_START
        return self.Status

    def get_status_name(self):
        l = {
            self.STATUS_STOPPED: '已停止',
            self.STATUS_WAIT_START: '启动中',
            self.STATUS_WAIT_SCAN: '等待扫码',
            self.STATUS_WAIT_LOGIN: '已启动',
            self.STATUS_WAIT_INIT: '已登录',
            self.STATUS_STARTED: '已初始化',
        }
        return l.get(self.get_status(), '未知')

    def get_robot_function_name(self, function_type):
        l = {
            self.FUNCTION_TYPE_CREATE_ROBOT: '创建机器人',
            self.FUNCTION_TYPE_REPLY_MSG: '发送/回复消息',
            self.FUNCTION_TYPE_KICK_OUT: '踢人',
            self.FUNCTION_TYPE_GROUP_SEND: '群发',
            self.FUNCTION_TYPE_STATISTICS: '统计',
            self.FUNCTION_TYPE_CHAT_ROBOT: '聊天机器人',
        }
        return l.get(function_type, '未知')
