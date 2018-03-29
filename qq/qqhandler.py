# -*- coding: utf-8 -*-

"""
封装酷Q HTTP API
https://richardchien.github.io/coolq-http-api/3.3/#/API
"""
from coolq_http_server import bot
from log.my_logger import logger

import time


class QQHandler:
    send_message_permission = True

    def __init__(self):
        pass

    @classmethod
    def get_login_info(cls):
        """
        获取登录号信息
        :return:
        """
        login_info = bot.get_login_info()
        logger.debug('login_info: %s', login_info)
        return login_info

    @classmethod
    def get_group_list(cls):
        group_list = bot.get_group_list()
        logger.debug('group list: %s', group_list)
        return group_list

    @classmethod
    def send_to_private(cls, qq, message):
        bot.send_private_msg(user_id=qq, message=message)

    @classmethod
    def get_group_number(cls, group_number):
        """
        获取对应群的成员人数
        :param group_number:
        :return:
        """
        group_member_list = bot.get_group_member_list(group_id=group_number)
        return len(group_member_list)

    # 睡眠时 定时任务不发送任何信心
    @classmethod
    def send_to_groups(cls, groups, message):
        if cls.send_message_permission is True:
            for group in groups:
                bot.send_group_msg(group_id=group, message=message)

    # 睡眠时 命令任务反馈
    @classmethod
    def send_to_groups_by_order(cls, groups, message, at_sender=False):
        if cls.send_message_permission is False:
            message = '中泰机器人已睡觉,唤醒请输入 -起床'
        if at_sender:
            return {'reply': message, 'at_sender': True}
        for group in groups:
            bot.send_group_msg(group_id=group, message=message)


if __name__ == '__main__':
    pass
