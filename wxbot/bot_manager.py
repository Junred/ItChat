# coding=utf-8
import logging
import itchat
from itchat import utils
from .task_manager import TaskManner

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

    @staticmethod
    def qr_callback(uuid, status, qrcode):
        logger.debug(uuid)
        logger.debug(status)

        if status != '200':
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
        chat_rooms = itchat.get_chatrooms()
        for chat_room in chat_rooms:
            if chat_room.get('IsOwner', 0) != 1:
                continue
            logger.debug('uin:{0}, nickName:{1}, userName:{2}'.format(chat_room['Uin'], chat_room['NickName'],
                                                                      chat_room['UserName']))
            for contact in chat_room['MemberList']:
                logging.debug(contact)
            # update group

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
        TaskManner.process()
        pass
