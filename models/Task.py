# coding: utf-8
"""
 任务
    任务ID
    任务所属微信账号
    任务类型：立即刷新群列表，
    任务内容
"""
from sqlalchemy import *
from . import BaseModel


class Task(BaseModel):
    __tablename__ = 'Task'

    # 刷新群列表
    TASK_TYPE_REFRESH_GROUP = 1
    # 从消息库选择消息发送, 对应Content为 消息ID数组
    TASK_TYPE_SEND_MSG = 20

    WxAccount = Column('WxAccount', String(64), nullable=False, index=True)
    TaskType = Column('TaskType', Integer, nullable=False)
    Content = Column('Content', String(32), nullable=False)
    ToUserName = Column('ToUserName', String(128), nullable=True)
    SendTime = Column('SendTime', DateTime, nullable=False, server_default=func.now(), index=True)

    @classmethod
    def add_task(cls, wx_account, task_type, content, to_username=None, send_time=None, auto_commit=False):
        args = {
            'WxAccount': wx_account,
            'TaskType': task_type,
            'Content': content,
            'ToUserName': to_username,
        }
        if send_time:
            args.update({
                'SendTime': send_time
            })

        task = cls(**args)
        if task and auto_commit:
            cls.commit()
        return task

    @classmethod
    def get_task(cls, wx_account):
        task_models = cls.get_models_filter(cls.WxAccount==wx_account, cls.SendTime < func.now())
        if task_models is None or len(task_models) == 0:
            return None
        return task_models[0]
