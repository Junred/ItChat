# coding=utf-8
import time
import sys

import re

import itchat
from itchat.content import *



def send_chatrooms():
    chatrooms = itchat.search_chatrooms(name='国学')
    for chatroom in chatrooms:
        itchat.send_msg(chatroom['NickName'], toUserName=chatroom['UserName'])

start_index = 650
end = 2000

t = time.time()

def create_chatrooms():
    global start_index
    member = itchat.search_friends(name='斐')
    username = member[0]['UserName']

    print(itchat.originInstance.storageClass.userName)

    chatroom_name = '国学小私塾-A{0}班'.format(start_index)
    room = itchat.create_chatroom([{'UserName': username}, {'UserName': itchat.originInstance.storageClass.userName}], chatroom_name)
    if room:
        itchat.send_msg(chatroom_name, room['ChatRoomName'])
    else:
        print(room)

    start_index += 1


def schedule(core):
    print('schedule ---- init: {0}'.format(core.wx_init))

    global t
    now = time.time()
    if core.wx_init:
        if now - t > 5:
            t = now
            create_chatrooms()
            # send_chatrooms()

    # time.sleep(2)


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

