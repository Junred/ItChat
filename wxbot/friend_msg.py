# coding=utf-8
import logging
import itchat
import time
from itchat.content import *
from .filehelper import FileHelper

logger = logging.getLogger('GroupMsg')


class FriendMsg(object):
    @staticmethod
    def log(msg):
        logger.debug('-' * 25 + msg['Type'] + '-' * 25)
        logger.debug(msg)
        logger.debug('=' * 50)

    @staticmethod
    @itchat.msg_register(TEXT, isFriendChat=True)
    def process_text(msg):
        FriendMsg.log(msg)
        to_username = msg['ToUserName']
        from_username = msg['FromUserName']

        if itchat.originInstance.storageClass.userName == from_username and to_username == 'filehelper':
            logger.debug('receive msg from filehelper: {0}'.format(msg['Content']))
            FileHelper.process_text(content=msg['Content'])

    @staticmethod
    @itchat.msg_register(PICTURE, isFriendChat=True)
    def process_image(msg):
        FriendMsg.log(msg)

        to_username = msg['ToUserName']
        from_username = msg['FromUserName']

        if itchat.originInstance.storageClass.userName == from_username and to_username == 'filehelper':
            logger.debug('receive msg from filehelper: {0}'.format(msg['Content']))
            save_to = 'data/images/{0}'.format(msg['FileName'])
            download_fn = msg['Text']
            ret = download_fn(save_to)
            if ret:
                logger.debug('download iamge to {0}'.format(save_to))
                FileHelper.process_image(save_to)
            else:
                logger.error('download image failed')
