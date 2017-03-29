# coding=utf-8
import time
import logging
from models.msg_reply import MsgReply
from models.msg_lib import Msg


logger = logging.getLogger('ReplyManager')


class ReplyManager(object):

    keywords_reply = {}
    member_count_reply = {}

    last_update_time = 0

    UPDATE_SETTING_INTERVAL = 5

    @classmethod
    def refresh_settings(cls):
        now = time.time()
        if now - cls.last_update_time < cls.UPDATE_SETTING_INTERVAL:
            return
        from wxbot.bot_manager import BotManager

        reply_models = MsgReply.get_models_filter(MsgReply.WxAccount == BotManager.wx_account)
        if reply_models is None:
            logger.warn('{0} not setting replay config'.format(BotManager.wx_account))
            return

        logger.debug('refresh reply settings')
        cls.keywords_reply = {}
        cls.member_count_reply = {}
        for reply_model in reply_models:
            if reply_model.Type == MsgReply.TYPE_KEYWORDS_REPLY:
                cls.keywords_reply[reply_model.Condition] = reply_model.MsgIds
            elif reply_model.Type == MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY:
                cls.member_count_reply[reply_model.Condition] = reply_model.MsgIds

        cls.last_update_time = time.time()

    @classmethod
    def get_keywords_reply_msgs(cls, text):
        from wxbot.bot_manager import BotManager

        msg_lib_ids = []
        for keywords, msg_ids in cls.keywords_reply.items():
            if keywords in text:
                msg_lib_ids = msg_ids
                break

        if len(msg_lib_ids) == 0:
            return []

        msg_models = Msg.get_models_filter(Msg.WxAccount == BotManager.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []
        return msg_models

    @classmethod
    def get_member_count_msgs(cls, count):
        from wxbot.bot_manager import BotManager

        msg_lib_ids = cls.member_count_reply.get(count, [])
        if len(msg_lib_ids) == 0:
            return

        msg_models = Msg.get_models_filter(Msg.WxAccount == BotManager.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []
        return msg_models
