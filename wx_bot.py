# coding: utf-8
"""
    微信机器人
"""
import logging
import sys
import os

import itchat
import models
from wxbot.bot_manager import BotManager
from models.robot import Robot
from models.topic import Topic

logging.basicConfig(format='%(asctime)s\t%(filename)s:%(lineno)d\t%(levelname)5s\t%(message)s', level=logging.DEBUG)


def main(bot_id, bot_wx_account, topic_id):
    # 检查bot_id和微信账号是否对应, 并存储process id 存入到数据当中

    logging.debug('bot starting with bot_id:{0}, bot_wx_account:{1}'.format(bot_id, bot_wx_account))

    robot_model = Robot.get_model_filter(Robot.Id == bot_id, Robot.WxAccount == bot_wx_account)
    if robot_model is None:
        logging.error('bot id:{0} bot_wx_account:{1} not created'.format(bot_id, bot_wx_account))
        return

    topic_model = Topic.get_model_by_id(topic_id)
    if topic_model is None or topic_model.UserId != robot_model.UserId:
        logging.error('bot[{0}] the topic[{1}] is not belong you'.format(bot_id, topic_id))
        return

    robot_model.TopicId = topic_id

    if robot_model.get_status() != Robot.STATUS_STOPPED:
        logging.error('robot already starting')
        return

    root_path = os.path.dirname(os.path.abspath(__file__))
    logging.debug(root_path)
    storage_dir = '{0}/data/{1}.pkl'.format(root_path, bot_wx_account)

    BotManager.set_bot(robot_model, root_path, storage_dir)

    robot_model.start()
    robot_model.Pid = os.getpid()
    Robot.save([robot_model])
    logging.info('wxbot {0} {1} {2} {3} starting'.format(bot_id, bot_wx_account, robot_model.Pid, robot_model.TopicId))

    itchat.auto_login(hotReload=True, statusStorageDir=storage_dir, qrCallback=BotManager.qr_callback,
                      loginCallback=BotManager.login_callback, exitCallback=BotManager.exit_callback,
                      initCallback=BotManager.init_message)
    itchat.run(blockThread=True, schedule=BotManager.schedule, exitCallback=BotManager.exit_callback)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        logging.debug('usage: \n    {0} bot_id bot_wx_account topic_id'.format(sys.argv[0]))
        sys.exit(1)

    bot_id = sys.argv[1]
    bot_wx_account = sys.argv[2]
    topic_id = sys.argv[3]

    models._base.metadata.create_all(models.db.engine)

    main(bot_id, bot_wx_account, topic_id)
