# coding=utf-8
import time
import sys

import re

import itchat
from itchat.content import *


send_config = {
    'MUST_KEYWORDS': ['科学添加'],

    'SHOULD_KEYWORDS': [],

    'percent': 100,

    'content': [
        {
            'msg': [
                {
                    'type': PICTURE,
                    'content': 'groupsend/fushi_guanggao_31.jpg',
                },
                {
                    'type': TEXT,
                    'content': '@所有人 【今日辅食课程】请点击图片，按图示免费获取!未查收到图片的妈妈们，请关注微信公众号【科学辅食每天教】，点击每日辅食菜单。'
                },
            ]
        },
    ]
}

send_groups = []
medias_cache = {}
medias_count = {}
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

        #500, 1000, 1500, 2000, 2500
        # if not isowner or not need_send or number is None or int(number) > 3000 or int(number) < 1500:
        if not isowner or not need_send:
        # if not need_send:
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
    user_name = group_info['UserName']

    # itchat.set_chatroom_name(user_name, '骗子群')

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

            mid = medias_cache.get(content, None)
            mid_count = medias_count.get(content, 0)
            if mid_count >= 10:
                medias_count[content] = 0
                mid = None
            elif mid_count == 0:
                medias_count[content] = 0

            if mid is None:
                print('upload image {0}'.format(content))
                r = itchat.upload_file(content, isPicture=True)
                if r:
                    mid = r['MediaId']
                else:
                    print('upload image failed {0}'.format(content))
                    continue

                medias_cache[content] = mid

            medias_count[content] += 1

            if send_switch:
                itchat.send_image(content, toUserName=group_info['UserName'], mediaId=mid)

        time.sleep(2)

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

        for i in range(1):
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
    itchat.run(debug=True, blockThread=True, schedule=schedule)


if __name__ == '__main__':
    is_sending = False
    statusStorageDir = None
    if len(sys.argv) > 1:
        statusStorageDir = sys.argv[1]
    print('statusStorageDir {0}'.format(statusStorageDir))
    main(statusStorageDir)

