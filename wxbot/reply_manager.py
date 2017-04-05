# coding=utf-8
import time
import logging
from models.msg_reply import MsgReply
from models.msg_lib import Msg


logger = logging.getLogger('ReplyManager')


class ReplyManager(object):

    wx_account = ''

    keywords_reply = {}
    member_count_reply = {}
    kick_member_keywords_replay = {}
    kick_out_reply = {}

    last_update_time = 0

    UPDATE_SETTING_INTERVAL = 5

    @classmethod
    def refresh_settings(cls):
        now = time.time()
        if now - cls.last_update_time < cls.UPDATE_SETTING_INTERVAL:
            return

        reply_models = MsgReply.get_models_filter(MsgReply.WxAccount == cls.wx_account)
        if reply_models is None:
            logger.warn('{0} not setting replay config'.format(cls.wx_account))
            return

        logger.debug('refresh reply settings')
        cls.keywords_reply = {}
        cls.member_count_reply = {}
        cls.kick_member_keywords_replay = {}
        cls.kick_out_reply = {}

        for reply_model in reply_models:
            if reply_model.Type == MsgReply.TYPE_KEYWORDS_REPLY:
                cls.keywords_reply[reply_model.Condition] = reply_model.MsgIds
            elif reply_model.Type == MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY:
                cls.member_count_reply[reply_model.Condition] = reply_model.MsgIds
            elif reply_model.Type == MsgReply.TYPE_KICK_KEYWORDS_REPLY:
                cls.kick_member_keywords_replay[reply_model.Condition] = reply_model.MsgIds
            elif reply_model.Type == MsgReply.TYPE_KICKOUT_REPLY:
                cls.kick_out_reply[reply_model.Condition] = reply_model.MsgIds

        cls.last_update_time = time.time()

    @classmethod
    def get_keywords_reply_msgs(cls, text):
        msg_lib_ids = []
        for keywords, msg_ids in cls.keywords_reply.items():
            if keywords in text:
                msg_lib_ids = msg_ids
                break

        if len(msg_lib_ids) == 0:
            return []

        msg_models = Msg.get_models_filter(Msg.WxAccount == cls.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []
        return msg_models

    @classmethod
    def get_member_count_msgs(cls, count):
        msg_lib_ids = cls.member_count_reply.get(str(count), [])
        if len(msg_lib_ids) == 0:
            return

        msg_models = Msg.get_models_filter(Msg.WxAccount == cls.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []
        return msg_models

    @classmethod
    def get_kick_member_reply_msg(cls, text):
        msg_lib_ids = []
        for keywords, msg_ids in cls.kick_member_keywords_replay.items():
            if keywords in text:
                msg_lib_ids = msg_ids
                break

        if len(msg_lib_ids) == 0:
            return []

        msg_models = Msg.get_models_filter(Msg.WxAccount == cls.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []

        return msg_models

    @classmethod
    def get_kickout_reply_msg_models(cls, text):

        msg_lib_ids = []
        for keywords, msg_ids in cls.kick_out_reply.items():
            if keywords in text:
                msg_lib_ids = msg_ids

        if len(msg_lib_ids) == 0:
            return []

        msg_models = Msg.get_models_filter(Msg.WxAccount == cls.wx_account, Msg.Id.in_(msg_lib_ids))
        if msg_models is None:
            return []

        return msg_models
