# coding: utf-8
"""
    微信机器人
"""
import logging
import sys

import itchat
from wxbot.bot_manager import BotManager

logging.basicConfig(format='%(asctime)s\t%(filename)s:%(lineno)d\t%(levelname)5s\t%(message)s', level=logging.DEBUG)


def main(bot_id, bot_wx_account):
    # 检查bot_id和微信账号是否对应, 并存储process id 存入到数据当中

    logging.debug('bot starting with bot_id:{0}, bot_wx_account:{1}'.format(bot_id, bot_wx_account))

    storage_dir = 'data/{0}.pkl'.format(bot_wx_account)

    BotManager.set_bot(bot_id, bot_wx_account, storage_dir)

    itchat.auto_login(hotReload=True, statusStorageDir=storage_dir, qrCallback=BotManager.qr_callback,
                      loginCallback=BotManager.login_callback, exitCallback=BotManager.exit_callback,
                      initCallback=BotManager.init_message)
    itchat.run(blockThread=True, schedule=BotManager.schedule)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.debug('usage: \n    {0} bot_id bot_wx_account'.format(sys.argv[0]))
        sys.exit(1)

    bot_id = sys.argv[1]
    bot_wx_account = sys.argv[2]

    main(bot_id, bot_wx_account)
