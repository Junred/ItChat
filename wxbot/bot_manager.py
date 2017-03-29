# coding=utf-8
import logging
import itchat
from itchat import utils
from itchat.content import *

from .task_manager import TaskManner
from .chatroom_msg import ChatRoomMsg
from .friend_msg import FriendMsg
from .filehelper import FileHelper
from .reply_manager import ReplyManager
from models.chatroom import ChatRoom, ChatRoomMember

logger = logging.getLogger('BotManager')


class BotManager(object):
    bot_id = 0
    wx_account = ''
    qr_storage_file = ''

    @classmethod
    def set_bot(cls, bot_id, wx_account, storage_file):
        cls.bot_id = bot_id
        cls.wx_account = wx_account
        cls.qr_storage_file = storage_file
        TaskManner.wx_account = wx_account
        ChatRoomMsg.wx_account = wx_account
        FileHelper.wx_account = wx_account

    @staticmethod
    def qr_callback(uuid, status, qrcode):
        logger.debug(uuid)
        logger.debug(status)

        if status not in ['200', '201']:
            save_file = 'temp/qrcode-{0}'.format(uuid)

            with open(save_file, 'wb') as f:
                f.write(qrcode)

            utils.print_qr(save_file)

            # 将uuid 入口

    @staticmethod
    def login_callback():
        # remove old data
        logger.info('login successfully')
        # save group to redis: hash map  key wx account, field username, value nickname

    @staticmethod
    def init_message():
        logger.debug('init message')
        BotManager.update_chatrooms()

    @staticmethod
    def exit_callback():
        logger.info('exit')
        pass

    @staticmethod
    def group_changed():
        pass

    @staticmethod
    def schedule(bot):
        # 更新机器人状态
        logger.debug('schedule ... ')
        TaskManner.wx_account = BotManager.wx_account
        TaskManner.process(BotManager.wx_account)
        ReplyManager.refresh_settings()

    @staticmethod
    def update_chatrooms():
        chat_rooms = itchat.get_chatrooms()
        for chat_room in chat_rooms:
            chat_room_model = ChatRoom.update_chat_room(chat_room['Uin'], BotManager.wx_account, chat_room['UserName'],
                                                        chat_room['NickName'])
            # logger.debug(chat_room_model)
            # logger.debug('uin:{0}, nickName:{1}, userName:{2}'.format(chat_room['Uin'], chat_room['NickName'],
            #                                                           chat_room['UserName']))
            update_models = [chat_room_model]

            for contact in chat_room['MemberList']:
                # logging.debug(contact)
                utils.emoji_formatter(contact, 'NickName')
                user_name = contact['UserName']
                nick_name = contact['NickName']
                attr_status = contact.get('AttrStatus', None)
                sex = contact.get('Sex', 0)
                province = contact.get('Province', None)
                city = contact.get('City', None)

                chat_room_member_model = ChatRoomMember.update_member(chat_room_model.Uin, BotManager.wx_account,
                                                                      user_name, nick_name,
                                                                      attr_status, sex, province, city)
                update_models.append(chat_room_member_model)

            ChatRoomMember.save(update_models)
