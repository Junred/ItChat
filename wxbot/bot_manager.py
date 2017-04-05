# coding=utf-8
import logging
import datetime
import os
import itchat
from itchat import utils
from itchat.content import *

from .task_manager import TaskManner
from .chatroom_msg import ChatRoomMsg
from .friend_msg import FriendMsg
from .filehelper import FileHelper
from .reply_manager import ReplyManager
from models.chatroom import ChatRoom, ChatRoomMember
from models.robot import Robot

logger = logging.getLogger('BotManager')


class BotManager(object):
    bot_id = 0
    wx_account = ''
    qr_storage_file = ''
    robot_model = None

    root_path = ''

    @classmethod
    def set_bot(cls, robot_model, root_path, storage_file):
        cls.robot_model = robot_model
        cls.qr_storage_file = storage_file
        cls.root_path = root_path
        TaskManner.wx_account = robot_model.WxAccount
        ChatRoomMsg.wx_account = robot_model.WxAccount
        FileHelper.wx_account = robot_model.WxAccount
        TaskManner.wx_account = robot_model.WxAccount
        ReplyManager.wx_account = robot_model.WxAccount
        FriendMsg.wx_account = robot_model.WxAccount

    @classmethod
    def get_robot_wx_account(cls):
        return cls.robot_model.WxAccount

    @classmethod
    def get_robot_model(cls):
        return cls.robot_model

    @staticmethod
    def qr_callback(uuid, status, qrcode):
        logger.debug(uuid)
        logger.debug(status)

        if status not in ['200', '201']:
            save_file = '{0}/temp/qrcode-{1}'.format(BotManager.root_path, uuid)
            BotManager.update_robot_model()
            if BotManager.robot_model.get_status() == Robot.STATUS_STOPPED:
                return True

            BotManager.robot_model.wait_scan(save_file)
            Robot.save([BotManager.robot_model])
            with open(save_file, 'wb') as f:
                f.write(qrcode)

            utils.print_qr(save_file)
            return False

    @staticmethod
    def login_callback():
        # remove old data
        logger.info('login successfully')
        # save group to redis: hash map  key wx account, field username, value nickname
        BotManager.robot_model.logined()
        Robot.save([BotManager.robot_model])

    @staticmethod
    def init_message():
        logger.debug('--------- init message --------')
        BotManager.update_chatrooms()

        BotManager.robot_model.inited()
        Robot.save([BotManager.robot_model])

    @staticmethod
    def exit_callback():
        logger.info('exit')

        BotManager.robot_model.stop()
        Robot.save([BotManager.robot_model])
        itchat.dump_login_status()

    @staticmethod
    def group_changed():
        pass

    @staticmethod
    def update_robot_model():
        bot_id = BotManager.robot_model.Id
        wx_account = BotManager.robot_model.WxAccount
        model = Robot.get_model_filter(Robot.Id == bot_id, Robot.WxAccount == wx_account)
        if model:
            BotManager.robot_model = model
            logger.debug('robot: {0}, status: {1}'.format(model.Id, model.Status))
            if model.get_status() == Robot.STATUS_STOPPED:
                logger.debug('itchat stop')
                itchat.stop()

    @staticmethod
    def schedule(bot):
        # 更新机器人状态
        logger.debug('schedule ... ')
        TaskManner.process(BotManager.get_robot_wx_account())
        ReplyManager.refresh_settings()

        BotManager.update_robot_model()
        BotManager.robot_model.UpdateTime = datetime.datetime.now()
        Robot.save([BotManager.robot_model])

    @staticmethod
    def update_chatrooms():
        chat_rooms = itchat.get_chatrooms()
        for chat_room in chat_rooms:
            chat_room_model = ChatRoom.update_chat_room(chat_room['Uin'], BotManager.robot_model.WxAccount, chat_room['UserName'],
                                                        chat_room['NickName'])
            # logger.debug(chat_room_model)
            # logger.debug('uin:{0}, nickName:{1}, userName:{2}'.format(chat_room_model.Uin, chat_room['NickName'],
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

                chat_room_member_model = ChatRoomMember.update_member(chat_room_model.Uin, BotManager.robot_model.WxAccount,
                                                                      user_name, nick_name,
                                                                      attr_status, sex, province, city)
                update_models.append(chat_room_member_model)

            ChatRoomMember.save(update_models)
