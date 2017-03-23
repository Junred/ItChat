# coding=utf-8
"""
  任务管理
"""
from models.task import Task


class TaskManner(object):

    SEND_MSG_INTERVAL = 1

    COUNT_PER_ONCE = 10

    @classmethod
    def process(cls):
        pass

    @classmethod
    def process_send_msg(cls, robot_id, msg_id):
        pass

    @classmethod
    def process_refresh_chatrooms(cls, robot_id):
        pass

