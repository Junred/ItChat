# coding=utf-8
import fire
from models.user import User
from models.robot import Robot


class Command(object):

    def create_user(self, name, nickname, user_type, pwd):
        User.add_user(name, nickname, user_type, pwd, auto_commit=True)

    def create_root_bot(self, wx_account, user_id, nickname, robot_functions):
        Robot.add_robot(wx_account, user_id, nickname, map(str, robot_functions), auto_commit=True)


if __name__ == '__main__':
    fire.Fire(Command)
