# coding=utf-8
import time
import sys

import re

import itchat
from itchat.content import *


send_config = {
    'MUST_KEYWORDS': ['科学添加'],

    'SHOULD_KEYWORDS': [],

    'percent': 20,

    'content': [
        # {
        #     'percent': 100,
        #     'msg': [
        #         {
        #             'type': CONTENT_TYPE_TEXT,
        #             'content': '（图文课程）http://mp.weixin.qq.com/s/EraJ7gQhN0qzqlcJQEu9kQ',
        #         },
        #         {
        #             'type': CONTENT_TYPE_TEXT,
        #             'content': '【小儿推拿妈妈学习班】今日课程，请查看上方图文↑↑↑ 往期课程可以在【亲宝听听听】公众号“妈妈课堂”栏目找到，爱学习的妈妈们赶紧关注吧！',
        #         },
        #     ]
        # },
        {
            'percent': 14,
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/kexuefushi.jpg',
                },
                {
                    'type': TEXT,
                    'content': '【科学辅食今日课程】给大家普及的辅食小知识是：科学喂养，莫入辅食添加“雷区”，更多月龄科学添加辅食指南，请长按识别二维码↑↑↑，关注微信公众号获取… 科学喂养，莫入辅食添加“雷区”=> http://mp.weixin.qq.com/s/XphSD_N-PV5BlqlzjbOaBQ',
                },
            ]
        },
        {
            'percent': 14,
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/mamafushiriji.jpg',
                },
                {
                    'type': TEXT,
                    'content': '【科学辅食今日课程】给大家普及的辅食小知识是：科学喂养，莫入辅食添加“雷区”，更多月龄科学添加辅食指南，请长按识别二维码↑↑↑，关注微信公众号获取… 科学喂养，莫入辅食添加“雷区”=> http://mp.weixin.qq.com/s/qowDfohSp3CNvy_QCzCnww',
                },
            ]
        },
        {
            # 每日一辅食
            'percent': 14,
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/meiriyifushi.jpg',
                },
                {
                    'type': TEXT,
                    'content': '【科学辅食今日课程】给大家普及的辅食小知识是：科学喂养，莫入辅食添加“雷区”，更多月龄科学添加辅食指南，请长按识别二维码↑↑↑，关注微信公众号获取… 科学喂养，莫入辅食添加“雷区”=> http://mp.weixin.qq.com/s/Nm2OaQqVFaRHp2DSO-eh8A',
                }
            ]
        },
        {
            'percent': 14,
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/kexuefushimeitianjiao.jpg',
                },
                {
                    'type': TEXT,
                    'content': '【科学辅食今日课程】给大家普及的辅食小知识是：科学喂养，莫入辅食添加“雷区”，更多月龄科学添加辅食指南，请长按识别二维码↑↑↑，关注微信公众号获取… 科学喂养，莫入辅食添加“雷区”=> http://mp.weixin.qq.com/s/CQEJJ0KlMXvOBEj58dNOcg',
                }
            ]
        },
        {
            'percent': 14,
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/baobaofushitianjiajiqiao.jpg',
                },
                {
                    'type': TEXT,
                    'content': '【科学辅食今日课程】给大家普及的辅食小知识是：科学喂养，莫入辅食添加“雷区”，更多月龄科学添加辅食指南，请长按识别二维码↑↑↑，关注微信公众号获取… 科学喂养，莫入辅食添加“雷区”=>  http://mp.weixin.qq.com/s/q-QtPQl_pKGk1HDB50RePA',
                }
            ]
        }
    ]
}

send_groups = []
medias_cache = {}
send_switch = True
in_sending = False


def show_chatrooms(core):
    print('show all chatrooms')
    chatrooms = core.get_chatrooms()
    if chatrooms is None:
        print('chatrooms is None')
        return

    if len(send_groups) > 0:
        return

    must_keywords = send_config['MUST_KEYWORDS']
    should_keywords = send_config['SHOULD_KEYWORDS']

    for chatroom in chatrooms:
        try:
            nickname = chatroom['NickName']
            username = chatroom['UserName']
            isowner = chatroom['IsOwner']
        except Exception as e:
            print(chatroom)
            print(e)
            continue

        need_send = True
        if len(must_keywords) > 0:
            for keywords in must_keywords:
                if keywords not in nickname:
                    need_send = False
                    break
            if not need_send:
                print('not need send to {0}, {1}'.format(nickname, username))
                continue

        # need_send = False
        # for keywords in should_keywords:
        #     if nickname in keywords or keywords is '*':
        #         need_send = True
        #         break

        number = get_group_number(nickname)

        if not isowner or not need_send or number is None or int(number) > 1000:
            print('not need send to {0}, {1}, isOwner: {2}, number: {3}'.format(nickname, username, isowner, number))
            continue

        print('---- send msg to group: {0}, {1}, isOwner: {2}, number: {3}'.format(nickname, username, isowner, number))
        send_groups.append(chatroom)


def get_group_number(nickname):
    rs = '\d+班'
    l = re.search(r'%s' % rs, nickname)
    if l:
        number = l.group()
        l = re.search(r'\d+', number)
        if l:
            return int(l.group())


def send_msg_to_group(group_info, content_arr):

    print('send msg to group: {0}'.format(group_info['NickName']))
    for item in content_arr:
        content_type = item['type']
        content = item['content']

        if content_type == TEXT:
            print('send text: {0}'.format(content))

            if send_switch:
                itchat.send_msg(content, group_info['UserName'])

        elif content_type == PICTURE:

            print('send image {0}'.format(content))

            # mid = medias_cache.get(content, None)
            mid = None
            if mid is None:
                print('upload image {0}'.format(content))
                r = itchat.upload_file(content, isPicture=True)
                if r:
                    mid = r['MediaId']
                else:
                    print('upload image failed {0}'.format(content))
                    return

                medias_cache[content] = mid

            if send_switch:
                itchat.send_image(content, toUserName=group_info['UserName'], mediaId=mid)

        time.sleep(1)

    return True


def send_groups_msg():

    send_count = len(send_groups)
    if send_count == 0:
        return

    print('send groups count: {0}'.format(send_count))

    def get_send_msg_arr(n, send_count):

        contents = send_config['content']
        n = 0
        percent = send_config['percent']
        for msg_item in contents:
            cnt = int(n * percent / 100.0 * send_count)

            if send_count <= cnt:
                # print json.dumps(msg_item)
                return msg_item['msg']
            n += 1

        return contents[len(contents) - 1]['msg']

    n = 0
    for group_info in send_groups:
        msg_arr = get_send_msg_arr(n, send_count)
        send_msg_to_group(group_info, msg_arr)
        time.sleep(4)


def schedule(core):
    print('schedule ---- init: {0}'.format(core.wx_init))

    if core.wx_init:
        if len(send_groups) > 0:
            return

        show_chatrooms(core)

        send_groups_msg()

    time.sleep(2)


def main(hotStorageDir=None):
    itchat.auto_login(hotReload=True, statusStorageDir=hotStorageDir)
    itchat.run(debug=True, schedule=schedule)


if __name__ == '__main__':
    is_sending = False
    statusStorageDir = None
    if len(sys.argv) > 1:
        statusStorageDir = sys.argv[1]
    print('statusStorageDir {0}'.format(statusStorageDir))
    main(statusStorageDir)

