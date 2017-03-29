# coding=utf-8
import time
import datetime

import itchat
from itchat.content import *
from models.msg_lib import Msg
from models.msg_reply import MsgReply
from models.chatroom import ChatRoom
from models.task import Task


class FileHelper(object):
    """
    与文件助手对话
    """

    STATUS_START_ADD_MSG_LIB = False
    media_caches = {}

    STATUS_START_MODIFY_MSG_LIB = False
    MSG_LIB_ID = 0

    wx_account = ''

    @classmethod
    def send_text_msg(cls, content):
        itchat.send_msg('>>>\n{0}'.format(content), toUserName='filehelper')

    @classmethod
    def send_image_msg(cls, content):
        mid = cls.media_caches.get(content, None)
        if mid is None:
            ret = itchat.upload_file(content, isPicture=True, toUserName='filehelper')
            if ret:
                mid = ret['MediaId']
                cls.media_caches[content] = mid
        itchat.send_image(content, toUserName='filehelper', mediaId=mid)

    @classmethod
    def process_text(cls, content):
        if content.startswith('查看帮助'):
            cls.send_all_help()
            return

        elif content.startswith('查看群列表'):
            cls.show_all_chatrooms()
            return

        elif content.startswith('搜索群列表'):
            cls.search_chatrooms(content)
            return
        elif content.startswith('添加群管理'):
            cls.update_chatroom_manager(content, True)
            return

        elif content.startswith('取消群管理'):
            cls.update_chatroom_manager(content, False)
            return

        elif content.startswith('查看所有消息'):
            cls.show_all_msg_lib()
            return

        elif content.startswith('开始添加消息'):
            cls.STATUS_START_ADD_MSG_LIB = True
            cls.send_text_msg('接下来你所发送的文字或图片消息会加入到消息库，一次发送作为一条消息')
            return

        elif content.startswith('结束添加消息'):
            cls.STATUS_START_ADD_MSG_LIB = False
            cls.send_text_msg('消息录入已停止')
            return

        elif content.startswith('开始修改消息'):
            content_arr = content.split(' ')
            if len(content_arr) != 2:
                cls.send_text_msg('格式错误\n开始修改消息 消息编号')
                return
            cls.STATUS_START_MODIFY_MSG_LIB = True
            cls.MSG_LIB_ID = int(content_arr[1])
            cls.send_text_msg('接下来你说发送的文字或图片会修改消息编号 {0}'.format(cls.MSG_LIB_ID))
            return

        elif content.startswith('结束修改消息'):
            cls.STATUS_START_MODIFY_MSG_LIB = False
            cls.send_text_msg('消息修改已停止')
            return

        elif content.startswith('查看关键字消息回复策略'):
            cls.show_all_msg_reply(MsgReply.TYPE_KEYWORDS_REPLY)
            return

        elif content.startswith('删除关键字消息回复策略'):
            cls.del_keyword_msg_reply(content, MsgReply.TYPE_KEYWORDS_REPLY)
            return

        elif content.startswith('添加关键字消息回复策略'):
            cls.add_keyword_msg_reply(content, MsgReply.TYPE_KEYWORDS_REPLY)
            return

        elif content.startswith('修改关键字消息回复策略'):
            cls.modify_keywords_msg_reply(content, MsgReply.TYPE_KEYWORDS_REPLY)
            return

        elif content.startswith('查看群人数消息回复策略'):
            cls.show_all_msg_reply(MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY)
            return

        elif content.startswith('删除群人数消息回复策略'):
            cls.del_keyword_msg_reply(content, MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY)
            return

        elif content.startswith('添加群人数消息回复策略'):
            cls.add_keyword_msg_reply(content, MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY)
            return

        elif content.startswith('修改群人数消息回复策略'):
            cls.modify_keywords_msg_reply(content, MsgReply.TYPE_CHAT_ROOM_COUNT_REPLY)
            return

        elif content.startswith('我要群发'):
            cls.group_send(content)
            return

        if cls.STATUS_START_ADD_MSG_LIB:
            cls.add_msg_lib(TEXT, content)
        elif cls.STATUS_START_MODIFY_MSG_LIB:
            cls.modify_msg_lib(TEXT, content)

    @classmethod
    def process_image(cls, content, ):
        if cls.STATUS_START_ADD_MSG_LIB:
            cls.add_msg_lib(PICTURE, content)
        elif cls.STATUS_START_MODIFY_MSG_LIB:
            cls.modify_msg_lib(PICTURE, content)

        return None

    @classmethod
    def send_all_help(cls):
        msg = '输入 "查看帮助"\n显示所有的帮助信息\n\n'
        msg += '输入 "查看群列表"\n显示所有群名称列表,并标记我是否是群主\n'
        msg += '输入 "搜索群列表 群昵称\n"'
        msg += '输入 "添加群管理 群昵称\n"'
        msg += '输入 "取消群管理 群昵称\n\n"'

        msg += '输入 "查看所有消息"\n显示消息库所有消息\n'
        msg += '输入 "开始添加消息"\n后面输入的所有消息都会添加到消息库\n'
        msg += '输入 "结束添加消息"\n添加消息结束\n\n'
        msg += '输入 "开始修改消息 消息编号"\n后面输入的消息会修改这个编号\n'
        msg += '输入 "结束修改消息"\n\n'
        cls.send_text_msg(msg)

        msg = ''
        msg += '输入 "查看关键字消息回复策略"\n会显示所有关键字对应的回复消息编号\n'
        msg += '输入 "删除关键字消息回复策略 关键字"\n删除关键字对应的消息回复\n'
        msg += '输入 "添加关键字消息回复策略 关键字 消息编号(多个用英文,分割)"\n'
        msg += '输入 "修改关键字消息回复策略 关键字 消息编号(多个用英文,分割)"\n\n'

        msg += '输入 "查看群人数消息回复策略"\n会显示所有群人数对应的回复消息编号\n'
        msg += '输入 "删除群人数消息回复策略 群人数"\n删除群人数对应的消息回复\n'
        msg += '输入 "添加群人数消息回复策略 群人数 消息编号(多个用英文,分割)"\n'
        msg += '输入 "修改群人数消息回复策略 群人数 消息编号(多个用英文,分割)"\n\n'

        msg += '输入 "我要群发 群主/成员 群名关键字 消息编号(多个用逗号分割)"\n群主:表示只发自己是群主的群，成员:表示只要自己在群内\n\n'

        cls.send_text_msg(msg)

    @classmethod
    def output_chatrooms(cls, chat_rooms):
        from wxbot.bot_manager import BotManager
        n = 0
        msg = ''
        for chat_room in chat_rooms:
            is_owner = ''
            if chat_room.get('IsOwner', 0) != 0:
                is_owner = '我是群主'

            room_model = ChatRoom.get_model_filter(ChatRoom.WxAccount == BotManager.wx_account,
                                                   ChatRoom.UserName == chat_room['UserName'])
            if room_model is None:
                cls.send_text_msg('{0} 在数据库中未找到'.format(chat_room['NickName']))
                continue
            msg += '{0}-{1}-{2}\n'.format(chat_room['NickName'], is_owner, '已管理' if room_model.IsManager else '')
            n += 1
            if n % 15 == 0:
                itchat.send_msg(msg)
                cls.send_text_msg(msg)
                msg = ''
                time.sleep(1)

        if len(msg) > 0:
            cls.send_text_msg(msg)

    @classmethod
    def show_all_chatrooms(cls):
        chat_rooms = itchat.get_chatrooms()
        cls.output_chatrooms(chat_rooms)

    @classmethod
    def search_chatrooms(cls, content):
        content_arr = content.split(' ')
        if len(content_arr) != 2:
            cls.send_text_msg('格式不正确\n搜索群列表 群昵称')
            return

        chat_rooms = itchat.search_chatrooms(name=content_arr[1])
        if chat_rooms is None or len(chat_rooms) == 0:
            cls.send_text_msg('没有找到对应的群')
            return
        cls.output_chatrooms(chat_rooms)

    @classmethod
    def update_chatroom_manager(cls, content, is_manager):
        from wxbot.bot_manager import BotManager
        content_arr = content.split(' ')
        if len(content_arr) != 2:
            cls.send_text_msg('格式不正确\n添加群管理 群昵称')
            return
        chat_rooms = itchat.search_chatrooms(name=content_arr[1])
        if chat_rooms is None or len(chat_rooms) == 0:
            cls.send_text_msg('没有找到相应的群')
            return

        msg = ''
        update_models = []
        for chat_room in chat_rooms:
            room_model = ChatRoom.get_model_filter(ChatRoom.WxAccount == BotManager.wx_account,
                                                   ChatRoom.UserName == chat_room['UserName'])
            if room_model is None:
                continue

            room_model.IsManager = is_manager
            update_models.append(room_model)

            msg += '{0} {1} 管理成功\n'.format(chat_room['NickName'], '添加' if is_manager else '取消')

            if len(update_models) % 15 == 0:
                ChatRoom.save(update_models, auto_commit=True)
                cls.send_text_msg(msg)
                update_models = []

        if len(update_models) > 0:
            ChatRoom.save(update_models, auto_commit=True)
            cls.send_text_msg(msg)

    @classmethod
    def show_all_msg_lib(cls):
        from wxbot.bot_manager import BotManager

        msg_models = Msg.get_models_filter_by(WxAccount=BotManager.wx_account)
        if msg_models is None or len(msg_models) == 0:
            cls.send_text_msg('抱歉，你的消息库为空')
            return None

        msg = ''
        n = 0
        for msg_model in msg_models:
            if msg_model.Type == TEXT:
                msg += '{0}. {1}\n'.format(msg_model.Id, msg_model.Content)
                n += 1
                if n % 15 == 0:
                    cls.send_text_msg(msg)
                    msg = ''
            elif msg_model.Type == PICTURE:
                cls.send_text_msg('{0}'.format(msg_model.Id))
                cls.send_image_msg(msg_model.Content)
                time.sleep(1)
        if len(msg) > 0:
            cls.send_text_msg(msg)

    @classmethod
    def add_msg_lib(cls, content_type, content):
        from wxbot.bot_manager import BotManager

        tips = '失败'
        if Msg.add_msg(BotManager.wx_account, content_type, content, auto_commit=True):
            tips = '成功'

        cls.send_text_msg('添加{0}'.format(tips))

    @classmethod
    def show_all_msg_reply(cls, reply_type):
        from wxbot.bot_manager import BotManager

        reply_models = MsgReply.get_models_filter_by(WxAccount=BotManager.wx_account, Type=reply_type)
        if reply_models is None or len(reply_models) == 0:
            cls.send_text_msg('你还没有{0}回复'.format(MsgReply.get_reply_type_name(reply_type)))
            return None

        msg = ''
        n = 0
        for reply_model in reply_models:
            msg += '{0} 回复消息编号: {1}\n'.format(reply_model.Condition, reply_model._MsgIds)
            n += 1
            if n % 15 == 0:
                cls.send_text_msg(msg)
                msg = ''

        if len(msg) > 0:
            cls.send_text_msg(msg)

    @classmethod
    def modify_msg_lib(cls, content_type, content):
        from wxbot.bot_manager import BotManager

        msg_model = Msg.get_model_filter(Msg.WxAccount == BotManager.wx_account, Msg.Id == cls.MSG_LIB_ID)
        if msg_model is None:
            cls.send_text_msg('消息编号 [{0}] 不存在'.format(cls.MSG_LIB_ID))
            return
        msg_model.Type = content_type
        msg_model.Content = content
        Msg.save([msg_model], auto_commit=True)
        cls.send_text_msg('修改消息[{0}]成功'.format(cls.MSG_LIB_ID))

    @classmethod
    def add_keyword_msg_reply(cls, content, reply_type):
        # 添加关键字消息回复策略 关键字 消息编号(多个用英文,分割)
        from wxbot.bot_manager import BotManager

        reply_type_name = MsgReply.get_reply_type_name(reply_type)

        content_arr = content.split(' ')
        if len(content_arr) != 3:
            cls.send_text_msg('格式不正确\n添加{0}消息回复策略 {1} 消息编号(多个用英文,分割)'.format(reply_type_name, reply_type_name))
            return
        keyword, msg_number = content_arr[1], content_arr[2]

        reply_model = MsgReply.get_model_filter(MsgReply.WxAccount == BotManager.wx_account,
                                                MsgReply.Condition == keyword,
                                                MsgReply.Type == reply_type)
        if reply_model:
            cls.send_text_msg('{0} [{1}] 已存在'.format(reply_type_name, keyword))
            return

        msg_numbers = msg_number.split(',')
        if len(msg_numbers) == 0:
            cls.send_text_msg('请输入消息编号')
            return

        msg_lib_models = Msg.get_models_filter(Msg.WxAccount == BotManager.wx_account, Msg.Id.in_(msg_numbers))
        if msg_lib_models is None or len(msg_numbers) != len(msg_lib_models):
            cls.send_text_msg('消息编号错误')
            return

        tips = '失败'
        if MsgReply.add_reply(BotManager.wx_account, reply_type, keyword, msg_numbers,
                              auto_commit=True):
            tips = '成功'
        cls.send_text_msg('添加{0}消息回复策略-{1}'.format(reply_type_name, tips))

    @classmethod
    def del_keyword_msg_reply(cls, content, reply_type):
        """删除关键字消息回复策略 关键字"""
        from wxbot.bot_manager import BotManager
        content_arr = content.split(' ')
        if len(content_arr) != 2:
            cls.send_text_msg('格式不正确\n删除{0}消息回复策略 {1}'.format(MsgReply.get_reply_type_name(reply_type),
                                                              MsgReply.get_reply_type_name(reply_type)))
            return

        keywords = content_arr[1]
        reply_model = MsgReply.get_model_filter(MsgReply.WxAccount == BotManager.wx_account,
                                                MsgReply.Condition == keywords,
                                                MsgReply.Type == reply_type)
        if reply_model is None:
            cls.send_text_msg('{0} [{1}] 消息回复不存在'.format(MsgReply.get_reply_type_name(reply_type), keywords))
            return

        MsgReply.delete(reply_model, True)
        cls.send_text_msg('删除成功')

    @classmethod
    def modify_keywords_msg_reply(cls, content, reply_type):
        # 添加关键字消息回复策略 关键字 消息编号(多个用英文,分割)
        from wxbot.bot_manager import BotManager

        reply_type_name = MsgReply.get_reply_type_name(reply_type)

        content_arr = content.split(' ')
        if len(content_arr) != 3:
            cls.send_text_msg('格式不正确\n添加{0}消息回复策略 {1} 消息编号(多个用英文,分割)'.format(reply_type_name, reply_type_name))
            return
        keyword, msg_number = content_arr[1], content_arr[2]

        reply_model = MsgReply.get_model_filter(MsgReply.WxAccount == BotManager.wx_account,
                                                MsgReply.Condition == keyword,
                                                MsgReply.Type == reply_type)
        if reply_model is None:
            cls.send_text_msg('{0} [{1}] 不存在'.format(reply_type_name, keyword))
            return

        msg_numbers = msg_number.split(',')
        if len(msg_numbers) == 0:
            cls.send_text_msg('请输入消息编号')
            return

        msg_lib_models = Msg.get_models_filter(Msg.WxAccount == BotManager.wx_account, Msg.Id.in_(msg_numbers))
        if msg_lib_models is None or len(msg_numbers) != len(msg_lib_models):
            cls.send_text_msg('消息编号错误')
            return

        reply_model.MsgIds = msg_numbers
        MsgReply.save([reply_model], True)
        cls.send_text_msg('修改{0}消息回复策略成功'.format(reply_type_name))

    @classmethod
    def group_send(cls, content):
        # '我要群发 群主/成员 群名关键字 消息编号(多个用逗号分割)"\n群主:表示只发自己是群主的群，成员:表示只要自己在群内'
        content_arr = content.split(' ')
        if len(content_arr) != 4:
            cls.send_text_msg('消息格式不正确\n我要群发 群主/成员 群名关键字 消息编号(多个用逗号分割)"\n群主:表示只发自己是群主的群，成员:表示只要自己在群内')
            return

        room_models = ChatRoom.get_models_filter(ChatRoom.WxAccount == cls.wx_account, ChatRoom.IsManager == True)
        # username => room_model
        room_model_map = {}
        if room_models:
            for room_model in room_models:
                room_model_map[room_model.UserName] = room_model

        now = datetime.datetime.now()
        check_is_owner = True if content_arr[1] == '群主' else False
        chatrooms = itchat.search_chatrooms(name=content_arr[2])
        if chatrooms:
            update_models = []
            for chatroom in chatrooms:
                username = chatroom['UserName']
                if check_is_owner and not chatroom.get('IsOwner', 0):
                    continue

                if room_model_map.get(username, None) is None:
                    continue

                # need to send
                now += datetime.timedelta(seconds=6)
                model = Task.add_task(cls.wx_account, Task.TASK_TYPE_SEND_MSG, content_arr[3], username, now)
                if model:
                    update_models.append(model)

                if len(update_models) % 15 == 0:
                    Task.save(update_models, True)
                    update_models = []

            if len(update_models) > 0:
                Task.save(update_models, True)
