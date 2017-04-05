# coding=utf-8
import logging
import re
import time
import itchat
from itchat import content, utils
from itchat.content import *
# from models.chatroom import ChatRoom, ChatRoomMember
from wxbot.reply_manager import ReplyManager

logger = logging.getLogger('GroupMsg')


class ChatRoomMsg(object):
    wx_account = ''

    username_white_list = []

    OTHER_KICK_KEYWORDS = '其他踢人消息回复'

    # 媒体文件缓存
    medias_cache = {}
    # 媒体文件技术
    medias_count = {}

    @staticmethod
    def log(msg):
        logger.debug('-' * 25 + msg['Type'] + '-' * 25)
        logger.debug(msg)
        logger.debug('=' * 50)

    @classmethod
    def send_image(cls, image, to_username):
        cnt = cls.medias_count.get(image, 0)
        if cnt >= 10:
            cnt = 0
            mid = None
        else:
            cnt += 1
            mid = cls.medias_cache.get(image, None)

        if mid is None:
            mid = itchat.upload_file(image, isPicture=True)

        if not mid:
            logger.error('upload image failed')
            logger.error(mid)
            return

        cls.medias_cache[image] = mid
        cls.medias_count[image] = cnt
        itchat.send_image(image, toUserName=to_username, mediaId=mid)

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
    def send_chatroom_msg(msg_lib_models, user_name, nickname='', is_at=False):
        if msg_lib_models is None or len(msg_lib_models) == 0:
            return

        n = 0
        if is_at:
            itchat.send_msg('@{0}'.format(nickname), toUserName=user_name)

        for msg_model in msg_lib_models:
            if n > 0:
                time.sleep(1)

            if msg_model.Type == TEXT:
                itchat.send_msg(msg_model.Content, toUserName=user_name)
            elif msg_model.Type == PICTURE:
                # todo image 需要复用
                ChatRoomMsg.send_image(msg_model.Content, user_name)

            n += 1

    @staticmethod
    @itchat.msg_register(content.TEXT, isGroupChat=True)
    def process_text(msg):
        # from .bot_manager import BotManager

        ChatRoomMsg.log(msg)

        actual_username = msg['ActualUserName']
        from_username = msg['FromUserName']
        to_username = msg['ToUserName']
        actual_nickname = msg['ActualNickName']

        if from_username == itchat.originInstance.storageClass.userName:
            logger.debug('msg is from my own')
            return

        # room_model = ChatRoom.get_model_filter(ChatRoom.WxAccount == BotManager.get_robot_wx_account(),
        #                                        ChatRoom.UserName == from_username)
        # if room_model is None:
        #     logger.warn('{0} not found in db'.format(msg.get('NickName', None)))
        #     return
        #
        # if not room_model.IsManager:
        #     logger.debug('{0} is not manager'.format(room_model.NickName))
        #     return
        chatroom = itchat.search_chatrooms(userName=from_username)
        if not chatroom.get('IsOwner', 0):
            logger.debug('is not my own chatroom: {0}'.format(chatroom.get('NickName')))
            return

        if chatroom['NickName'] == '管理员总群' and msg.get('Content') == '获取全部群成员93812':
            ChatRoomMsg.update_white_list(chatroom)

        msg_content = msg.get('Content', '')
        ChatRoomMsg.send_chatroom_msg(ReplyManager.get_keywords_reply_msgs(msg.get('Content', '')), from_username)

        kick_out_reply_msg_models = ReplyManager.get_kick_member_reply_msg(msg_content)
        if len(kick_out_reply_msg_models) > 0:
            ChatRoomMsg.send_kickout(from_username, actual_username,
                                     kick_out_reply_msg_models=kick_out_reply_msg_models)

    @staticmethod
    def send_kickout(from_username, member_username, kick_out_reply_msg_models=None, msg_content=None):
        from wxbot.bot_manager import BotManager
        from models.robot import Robot

        if member_username in ChatRoomMsg.username_white_list:
            logger.info('{0} in the white list'.format(member_username))
            return

        chatroom = itchat.search_chatrooms(userName=from_username)
        if chatroom is None:
            logger.error('chat room not found: {0}'.format(from_username))
            return

        if not chatroom.get('IsOwner', 0):
            logger.debug('is not my own chatroom: {0}'.format(chatroom.get('NickName')))
            return

        contact_info = utils.search_dict_list(chatroom['MemberList'], 'UserName', member_username)
        if contact_info is None:
            logger.error('member {0} not found int chatroom {1}'.format(from_username, member_username))
            return

        if not BotManager.robot_model.check_function(Robot.FUNCTION_TYPE_KICK_OUT):
            logger.warn('robot {0} kick out closed'.format(BotManager.robot_model.Id))
            return

        if kick_out_reply_msg_models is None:
            kick_out_reply_msg_models = ReplyManager.get_kick_member_reply_msg(msg_content)

        if kick_out_reply_msg_models is None and len(kick_out_reply_msg_models) == 0:
            logger.warn('kickout reply msg is None')
            return

        ChatRoomMsg.send_chatroom_msg(kick_out_reply_msg_models, from_username, contact_info['NickName'], True)
        itchat.delete_member_from_chatroom(from_username, [contact_info])

    @staticmethod
    @itchat.msg_register(content.NOTE, isGroupChat=True)
    def process_note(msg):
        # from .bot_manager import BotManager
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
            # chatroom_model = ChatRoom.get_model_filter_by(UserName=from_username, WxAccount=ChatRoomMsg.wx_account)
            # if chatroom and chatroom_model:
            #     contact_info = utils.search_dict_list(chatroom['MemberList'], 'NickName', nickname)
            #     if contact_info:
            #         # add contact_info to db
            #         ChatRoomMember.update_member(chatroom_model.Uin, ChatRoomMsg.wx_account, contact_info['UserName'],
            #                                      nickname, contact_info.get('AttrStatus', 0),
            #                                      contact_info.get('Sex', 0), contact_info.get('Province', None),
            #                                      contact_info.get('City', None), auto_commit=True)
            # else:
            #     logging.error('chat room not found in note message: {0}'.format(from_username))

            if chatroom and chatroom.get('IsOwner', 0):
                ChatRoomMsg.send_chatroom_msg(ReplyManager.get_member_count_msgs(len(chatroom['MemberList'])),
                                              from_username)

        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.PICTURE, isGroupChat=True)
    def process_image(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.CARD, isGroupChat=True)
    def process_card(msg):
        ChatRoomMsg.log(msg)
        ChatRoomMsg.send_kickout(msg.get('FromUserName'), msg.get('ActualUserName'),
                                 msg_content=ChatRoomMsg.OTHER_KICK_KEYWORDS)

    @staticmethod
    @itchat.msg_register(content.ATTACHMENT, isGroupChat=True)
    def process_attachment(msg):
        ChatRoomMsg.log(msg)

    @staticmethod
    @itchat.msg_register(content.MAP, isGroupChat=True)
    def process_map(msg):
        ChatRoomMsg.log(msg)
        ChatRoomMsg.send_kickout(msg.get('FromUserName'), msg.get('ActualUserName'),
                                 msg_content=ChatRoomMsg.OTHER_KICK_KEYWORDS)

    @staticmethod
    @itchat.msg_register(content.RECORDING, isGroupChat=True)
    def process_recording(msg):
        ChatRoomMsg.log(msg)
        ChatRoomMsg.send_kickout(msg.get('FromUserName'), msg.get('ActualUserName'),
                                 msg_content=ChatRoomMsg.OTHER_KICK_KEYWORDS)

    @staticmethod
    @itchat.msg_register(content.SHARING, isGroupChat=True)
    def process_sharing(msg):
        ChatRoomMsg.log(msg)
        ChatRoomMsg.send_kickout(msg.get('FromUserName'), msg.get('ActualUserName'),
                                 msg_content=ChatRoomMsg.OTHER_KICK_KEYWORDS)

    @staticmethod
    @itchat.msg_register(content.SYSTEM)
    def process_system(msg):
        from .bot_manager import BotManager
        ChatRoomMsg.log(msg)
        # 被管理员踢出群聊 或 自己主动退出群聊 会在系统消息中 DelContactList
        # for contact in msg.get('DelContactList', []):
        #     chatroom_username = contact['UserName']
        #     chatroom_model = ChatRoom.get_model_filter_by(UserName=chatroom_username, WxAccount=ChatRoomMsg.wx_account)
        #     if chatroom_model is None:
        #         logger.error('{0} not found in data'.format(chatroom_username))
        #         continue
        #
        #     for member in contact['DelMemberList']:
        #         member_username = member['UserName']
        #         member_model = ChatRoomMember.del_member(chatroom_model.Uin, ChatRoomMsg.wx_account, member_username,
        #                                                  member['NickName'])
        #         if member_model:
        #             logger.info(
        #                 'delete chatroom [{0}] member: {1}'.format(chatroom_model.NickName, member_model.NickName))
        #
        #     ChatRoomMember.commit()

        if msg.get('SystemInfo', '') == 'uins' and msg.get('StatusNotifyCode', 0) == 4:
            BotManager.init_message()

    @staticmethod
    @itchat.msg_register(content.VIDEO, isGroupChat=True)
    def process_video(msg):
        ChatRoomMsg.log(msg)
        ChatRoomMsg.send_kickout(msg.get('FromUserName'), msg.get('ActualUserName'),
                                 msg_content=ChatRoomMsg.OTHER_KICK_KEYWORDS)

    @classmethod
    def update_white_list(cls, chatroom):
        cls.username_white_list = []
        for member in chatroom['MemberList']:
            logger.info('add white {0} {1}'.format(member['NickName'], member['UserName']))
            cls.username_white_list.append(member['UserName'])
