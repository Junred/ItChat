# coding=utf-8
"""
  任务管理
"""
import logging
from models.task import Task
from models.msg_lib import Msg

logger = logging.getLogger('TaskManager')


class TaskManner(object):
    SEND_MSG_INTERVAL = 1

    COUNT_PER_ONCE = 10

    robot_model = None

    @classmethod
    def process(cls):
        task_model = Task.get_task(cls.robot_model.WxAccount)
        if task_model is None:
            return

        ret = True
        if task_model.TaskType == Task.TASK_TYPE_SEND_MSG:
            cls.process_send_msg(task_model.ToUserName, task_model.Content)
        elif task_model.TaskType == Task.TASK_TYPE_REFRESH_GROUP:
            cls.process_refresh_chatrooms()
        else:
            ret = False

        Task.delete(task_model, True)

        logger.debug('process task ret:{0}'.format('成功' if ret else '失败'))

    @classmethod
    def process_send_msg(cls, to_username, content):
        from .chatroom_msg import ChatRoomMsg
        msg_ids = list(map(int, content.split(',')))
        if len(msg_ids) == 0:
            logger.warn('msg ids is None: {0}'.format(content))
            return

        logger.debug(msg_ids)

        msg_lib_models = Msg.get_models_filter(Msg.TopicId == cls.robot_model.TopicId, Msg.Id.in_(msg_ids))
        if msg_lib_models is None or len(msg_lib_models) == 0:
            logger.warn('msg not found in db: {0}'.format(content))
            return

        ChatRoomMsg.send_chatroom_msg(msg_lib_models, to_username)

    @classmethod
    def process_refresh_chatrooms(cls):
        from wxbot.bot_manager import BotManager
        BotManager.update_chatrooms()
