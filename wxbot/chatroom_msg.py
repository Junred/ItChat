# coding=utf-8
import logging
import re
import time
import itchat
from itchat import content, utils
from itchat.content import *
from models.chatroom import ChatRoom, ChatRoomMember
from wxbot.reply_manager import ReplyManager

logger = logging.getLogger('GroupMsg')


class ChatRoomMsg(object):

    wx_account = ''

    @staticmethod
    def log(msg):
        logger.debug('-' * 25 + msg['Type'] + '-' * 25)
        logger.debug(msg)
        logger.debug('=' * 50)

    @staticmethod
    def get_invite_in_username(data):
        """
        :return inviteUser, invitedUser
        """
        if '邀请' not in data or '加入' not in data:
            return None, None
        invite_username, invited_username = None, None
        r = re.match('"(.*)"邀请"(.*)"加入', data)
        if r:
            invite_username, invited_username = r.groups()
        return invite_username, invited_username

    @staticmethod
    def get_scan_in_username(data):
        """
        :return username
        """
        if '扫描' not in data or '二维码' not in data:
            return None
        username = None
        r = re.match('"(.*)"通过', data)
        if r:
            username = r.group(1)
        return username

    @staticmethod
    def send_chatroom_msg(msg_lib_models, user_name):
        if len(msg_lib_models) == 0:
            return

        n = 0
        for msg_model in msg_lib_models:
            if n > 0:
                time.sleep(1)

            if msg_model.Type == TEXT:
                itchat.send_msg(msg_model.Content, toUserName=user_name)
            elif msg_model.Type == PICTURE:
                itchat.send_image(msg_model.Content, toUserName=user_name)

            n += 1

    @staticmethod
    @itchat.msg_register(content.TEXT, isGroupChat=True)
    def process_text(msg):
        from .bot_manager import BotManager

        ChatRoomMsg.log(msg)

        actual_username = msg['ActualUserName']
        from_username = msg['FromUserName']
        to_username = msg['ToUserName']

        if from_username == itchat.originInstance.storageClass.userName:
            logger.debug('msg is from my own')
            return

        room_model = ChatRoom.get_model_filter(ChatRoom.WxAccount == BotManager.wx_account,
                                               ChatRoom.UserName == from_username)
        if room_model is None:
            logger.warn('{0} not found in db'.format(msg.get('NickName', None)))
            return

        if not room_model.IsManager:
            logger.debug('{0} is not manager'.format(room_model.NickName))
            return

        ChatRoomMsg.send_chatroom_msg(ReplyManager.get_keywords_reply_msgs(msg.get('Content', '')), from_username)

    @staticmethod
    @itchat.msg_register(content.NOTE, isGroupChat=True)
    def process_note(msg):
        from .bot_manager import BotManager
        """\
        记录
            邀请入群: Content "书城小号"邀请"肖书成"加入了群聊\
            扫码入群: Content "书城小号"通过扫描你分享的二维码加入群聊\
            移除群:   Content 你将"肖书成"移出了群聊\
            主动推出群聊:  无\
            红包:  收到红包，请在手机上查看\
        """
        from_username = msg['FromUserName']
        is_user_in_msg = False
        invite_username, invited_username = ChatRoomMsg.get_invite_in_username(msg['Content'])
        if invite_username and invited_username:
            # 邀请入群
            logger.info('{0} 邀请 {1} 加入群聊'.format(invite_username, invited_username))
            is_user_in_msg = True
            nickname = invited_username
        else:
            nickname = ChatRoomMsg.get_scan_in_username(msg['Content'])
            if nickname:
                # 扫码入群
                logger.info('{0} 通过扫码 加入群聊'.format(nickname))
                is_user_in_msg = True

        if is_user_in_msg:
            # 如果是有人进群, from_username 就是群的UserName
            chatroom = itchat.search_chatrooms(userName=from_username)
            chatroom_model = ChatRoom.get_model_filter_by(UserName=from_username, WxAccount=BotManager.wx_account)
            if chatroom and chatroom_model:
                contact_info = utils.search_dict_list(chatroom['MemberList'], 'NickName', nickname)
                if contact_info:
                    # add contact_info to db
                    ChatRoomMember.update_member(chatroom_model.Uin, BotManager.wx_account, contact_info['UserName'],
                                                 nickname, contact_info.get('AttrStatus', 0),
                                                 contact_info.get('Sex', 0), contact_info.get('Province', None),
                                                 contact_info.get('City', None), auto_commit=True)
            else:
                logging.error('chat room not found in note message: {0}'.format(from_username))

            ChatRoomMsg.send_chatroom_msg(ReplyManager.get_member_count_msgs(len(chatroom['MemberList'])),
                                          from_username)

        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.PICTURE, isGroupChat=True)
    def process_image(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.CARD)
    def process_card(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.ATTACHMENT)
    def process_attachment(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.MAP)
    def process_map(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.RECORDING)
    def process_recording(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.SHARING)
    def process_sharing(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.SYSTEM)
    def process_system(msg):
        from .bot_manager import BotManager
        ChatRoomMsg.log(msg)
        # 被管理员踢出群聊 或 自己主动退出群聊 会在系统消息中 DelContactList
        for contact in msg.get('DelContactList', []):
            chatroom_username = contact['UserName']
            chatroom_model = ChatRoom.get_model_filter_by(UserName=chatroom_username, WxAccount=BotManager.wx_account)
            if chatroom_model is None:
                logger.error('{0} not found in data'.format(chatroom_username))
                continue

            for member in contact['DelMemberList']:
                member_username = member['UserName']
                member_model = ChatRoomMember.del_member(chatroom_model.Uin, BotManager.wx_account, member_username,
                                                         member['NickName'])
                if member_model:
                    logger.info(
                        'delete chatroom [{0}] member: {1}'.format(chatroom_model.NickName, member_model.NickName))

            ChatRoomMember.commit()

        if msg.get('SystemInfo', '') == 'uins' and msg.get('StatusNotifyCode', 0) == 4:
            BotManager.init_message()

    @staticmethod
    @itchat.msg_register(content.VIDEO)
    def process_video(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.FRIENDS)
    def process_friends(msg):
        ChatRoomMsg.log(msg)
