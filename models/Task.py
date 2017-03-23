# coding: utf-8
"""
 任务
    任务ID
    任务所属用户ID
    任务所属机器人ID
    任务类型： 立即刷新群列表，
    任务内容
    任务状态
"""
from sqlalchemy import *
from . import BaseModel


class Task(BaseModel):
    __tablename__ = 'Task'

    TASK_TYPE_REFRESH_GROUP = 1
    TASK_TYPE_SEND_MSG = 20

    UserId = Column('UserId', Integer, nullable=False, index=True)
    RobotId = Column('RobotId', Integer, nullable=False, index=True)
    TaskType = Column('TaskType', Integer, nullable=False)
    Content = Column('Content', String(32), nullable=False)

    @classmethod
    def add_task(cls, user_id, robot_id, task_type, content):
        task = cls(UserId=user_id, RobotId=robot_id, TaskType=task_type, Content=content)
        return task
