# -*- coding: utf-8 -*-

from qqbot import qqbotsched
from qqbot.utf8logger import DEBUG, INFO
from weibo.weibo_handler import WeiboMonitor
from qq.qqhandler import QQHandler
from utils.config_reader import ConfigReader
from utils import global_config

weibo_monitor = None


def onStartupComplete(bot):
    # 启动完成时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    global weibo_monitor

    global_config.MEMBER_WEIBO_GROUPS = ConfigReader.get_property('qq_conf', 'member_weibo_groups').split(';')
    weibo_monitor = WeiboMonitor()
    weibo_monitor.login('15018433261', 'boa-85880907-BOA')
    name = ConfigReader.get_property('root', 'member_name')
    uid = ConfigReader.get_property('weibo', name)
    # uid = 1134206783
    weibo_monitor.getWBQueue(uid)


@qqbotsched(minute='*/35')
def update_weibo_conf(bot):
    global weibo_monitor

    DEBUG('读取微博配置')
    global_config.MEMBER_WEIBO_GROUPS = ConfigReader.get_property('qq_conf', 'member_weibo_groups').split(';')

    member_name = ConfigReader.get_property('root', 'member_name')
    if global_config.MEMBER_NAME == '' or global_config.MEMBER_NAME != member_name:
        DEBUG('微博监控变更')
        global_config.MEMBER_NAME = member_name
        uid = ConfigReader.get_property('weibo', member_name)
        if uid != '':
            weibo_monitor.getWBQueue(uid)
        else:
            INFO('没有微博UID')


@qqbotsched(second='*/55')
def monitor_member_weibo(bot):
    global weibo_monitor

    newWB = weibo_monitor.startMonitor()
    if newWB is not None:
        DEBUG(newWB)
        member_weibo_groups = QQHandler.list_group(global_config.MEMBER_WEIBO_GROUPS)
        message = '官博有新消息啦:\n %s\n发送时间: %s' % (newWB['scheme'], newWB['created_at'])
        if newWB['created_at'] == '刚刚':
            QQHandler.send_to_groups(member_weibo_groups, message)
