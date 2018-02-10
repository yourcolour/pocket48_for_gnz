# -*- coding: utf-8 -*-
from qqbot import qqbotsched
from qqbot.utf8logger import DEBUG, INFO, ERROR
import time

from utils.config_reader import ConfigReader
from pocket48.pocket48_handler import Pocket48Handler
from qq.qqhandler import QQHandler

from utils import global_config, util

pocket48_handler = None


def onInit(bot):
    # 初始化时被调用
    # 注意 : 此时 bot 尚未启动，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    DEBUG('%s.onInit', __name__)


def onQrcode(bot, pngPath, pngContent):
    # 获取到二维码时被调用
    # 注意 : 此时 bot 尚未启动，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    # pngPath : 二维码图片路径
    # pngContent : 二维码图片内容
    DEBUG('%s.onQrcode: %s (%d bytes)', __name__, pngPath, len(pngContent))


def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # contact : QContact 对象，消息的发送者
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
    # DEBUG('member: %s', str(getattr(member, 'uin')))
    # DEBUG('content: %s', content)
    # DEBUG('contact: %s', contact.ctype)
    global pocket48_handler

    if contact.ctype == 'group':
        if '@ME' in content:  # 在群中@机器人
            strs = content.split('[@ME]')[1].strip()
            if strs :
                id = contact.uin
                bot.SendTo(contact, pocket48_handler.get_tuling_ai(id, strs))
            else:
                bot.SendTo(contact, util.random_str(global_config.AT_AUTO_REPLY))
        elif content.startswith('-'):  # 以'-'开头才能触发自动回复
            if content == '-version':
                bot.SendTo(contact, 'QQbot-' + bot.conf.version)
            elif content == '-票务' or content == '-公演':
                pocket48_handler.get_current_ticket_info_msg(global_config.TICKET_INFO)
            elif content == '-屏蔽全部消息' or content == '-屏蔽所有消息':
                if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                    global_config.DEACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
                    global_config.ACTIVE_MEMBER_ROOM_ID_LIST = []
                    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '已屏蔽全部房间消息')

                else:
                    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '当前已屏蔽全部房间消息，请不要重复输入命令')
            elif content == '-开启全部消息' or content == '-开启全部消息':
                if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                    global_config.ACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
                    global_config.DEACTIVE_MEMBER_ROOM_ID_LIST = []
                    pocket48_handler.init_msg_queues(global_config.ACTIVE_MEMBER_ROOM_ID_LIST)
                    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '已开启全部房间消息')
                else:
                    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '当前已开启全部房间消息，请不要重复输入命令')
            elif content == '-关闭':
                bot.SendTo(contact, 'QQ机器人已关闭')
                bot.Stop()
            elif '-屏蔽' in content and '消息' in content:
                if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                    name = util.get_order_name(content)
                    # 命令是否包含成员名字
                    if util.is_name_in_member_list(name):
                        # 屏蔽逻辑
                        pocket48_handler.deactive_member_by_name(name)
                    else:
                        QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '屏蔽失败, 无法识别该成员,请确保命令输入正确')
                else:
                     QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '当前已屏蔽全部房间消息,无法再进行屏蔽')
            elif '-开启' in content and '消息' in content:
                if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                    name = util.get_order_name(content)
                    # 命令是否包含成员名字
                    if util.is_name_in_member_list(name):
                        # 开启逻辑
                        pocket48_handler.active_member_by_name(name)
                    else:
                        QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '开启失败, 无法识别该成员,请确保命令输入正确')
                else:
                    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, '当前已开启全部房间消息，无法再进行开启')
            elif content == '-直播':
                r = pocket48_handler.get_member_live_msg()
                pocket48_handler.parse_member_live_now(r, global_config.LIVING_MEMBER_ID_LIST)
            elif content == '-小黑屋':
                msg = util.get_black_room_list()
                QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)
            elif content == '-小白屋':
                msg = util.get_white_room_list()
                QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)
            elif content == '-使用说明':
                msg = '''
机器人使用说明:
一、命令类型（输入一次即可, 没回复可能是机器人没开启 或者 机器人卡住了）:
    (1)'-票务':  查看尚未公演的票务信息.
    (2)'-直播':  查看所有正在直播的直播间.
    (3)'-使用说明':  机器人使用说明.
    (4)'-屏蔽全部(所有)消息':  屏蔽全部成员房间消息.
    (5)'-开启全部(所有)消息':  开启全部成员房间消息.
    (6)'-屏蔽' + 成员名字 + '消息':  屏蔽某个成员房间消息.
    (7)'-开启' + 成员名字 + '消息':  开启某个成员房间消息.
    (8)'-小黑屋':  查看被屏蔽房间消息的成员.
    (9)'-小白屋':  查看已开启房间消息的成员
    其余命令均无法识别
二、聊天
    '@机器人' + 聊天内容:  与图灵机器人聊天 （每天上限1000次, 河内梗完善中...）'''
                QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)
            else:  # 无法识别命令
                no_such_command = ConfigReader.get_property('profile', 'no_such_command')
                bot.SendTo(contact, no_such_command)


def onInterval(bot):
    # 每隔 5 分钟被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('%s.onInterval', __name__)


def onStartupComplete(bot):
    # 启动完成时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('%s.onStartupComplete', __name__)
    global pocket48_handler
    # 实例化PocketHandler
    pocket48_handler = Pocket48Handler([], [], [], [], [])
    # 获取票务
    global_config.TICKET_INFO = pocket48_handler.get_ticket_info()
    # 登录口袋48
    username = ConfigReader.get_property('user', 'username')
    password = ConfigReader.get_property('user', 'password')
    pocket48_handler.login(username, password)

    DEBUG('读取配置文件')

    ConfigReader.read_conf()
    global_config.ACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
    global_config.LIVING_MEMBER_ID_LIST = ConfigReader.get_living_member_id_list()


    global_config.AUTO_REPLY_GROUPS = ConfigReader.get_property('qq_conf', 'auto_reply_groups').split(';')
    global_config.MEMBER_ROOM_MSG_GROUPS = ConfigReader.get_property('qq_conf', 'member_room_msg_groups').split(';')
    global_config.MEMBER_ROOM_COMMENT_GROUPS = ConfigReader.get_property('qq_conf', 'member_room_comment_groups').split(';')
    global_config.MEMBER_LIVE_GROUPS = ConfigReader.get_property('qq_conf', 'member_live_groups').split(';')
    global_config.MEMBER_ROOM_MSG_LITE_GROUPS = ConfigReader.get_property('qq_conf', 'member_room_comment_lite_groups').split(';')

    auto_reply_groups = QQHandler.list_group(global_config.AUTO_REPLY_GROUPS)
    member_room_msg_groups = QQHandler.list_group(global_config.MEMBER_ROOM_MSG_GROUPS)
    member_room_comment_msg_groups = QQHandler.list_group(global_config.MEMBER_ROOM_COMMENT_GROUPS)
    member_live_groups = QQHandler.list_group(global_config.MEMBER_LIVE_GROUPS)
    member_room_msg_lite_groups = QQHandler.list_group(global_config.MEMBER_ROOM_MSG_LITE_GROUPS)

    pocket48_handler.member_room_msg_groups = member_room_msg_groups
    pocket48_handler.member_room_comment_msg_groups = member_room_comment_msg_groups
    pocket48_handler.auto_reply_groups = auto_reply_groups
    pocket48_handler.member_live_groups = member_live_groups
    pocket48_handler.member_room_msg_lite_groups = member_room_msg_lite_groups

    global_config.JIZI_KEYWORDS = ConfigReader.get_property('profile', 'jizi_keywords').split(';')
    global_config.JIZI_LINK = ConfigReader.get_property('profile', 'jizi_link').split(';')

    global_config.WEIBO_KEYWORDS = ConfigReader.get_property('profile', 'weibo_keywords').split(';')
    global_config.GONGYAN_KEYWORDS = ConfigReader.get_property('profile', 'gongyan_keywords').split(';')
    global_config.LIVE_LINK=ConfigReader.get_property('profile', 'live_link').split(';')
    global_config.LIVE_SCHEDULE = ConfigReader.get_property('profile', 'live_schedule').split(';')

    global_config.WEIBO_LINK = ConfigReader.get_property('profile', 'weibo_link')
    global_config.SUPER_TAG = ConfigReader.get_property('profile', 'super_tag')

    global_config.MEMBER_ATTR = ConfigReader.get_property('profile', 'member_attr')
    global_config.I_LOVE = ConfigReader.get_property('profile', 'i_love').split(';')

    global_config.AT_AUTO_REPLY = ConfigReader.get_property('profile', 'at_auto_reply').split(';')
    global_config.ROOM_MSG_LITE_NOTIFY = ConfigReader.get_property('profile', 'room_msg_lite_notify').split(';')

    global_config.PERFORMANCE_NOTIFY = ConfigReader.get_property('profile', 'performance_notify')

    # 哔哩哔哩消息初始化
    bilibili_video_list = pocket48_handler.get_bilibili_video_list()
    pocket48_handler.init_bilibili_video_queues(bilibili_video_list)

    # 成员房间消息初始队列化
    pocket48_handler.init_msg_queues(global_config.ACTIVE_MEMBER_ROOM_ID_LIST)

    # 先更新配置
    update_conf(bot)


def onUpdate(bot, tinfo):
    # 某个联系人列表更新时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # tinfo : 联系人列表的代号，详见文档中关于 bot.List 的第一个参数的含义解释
    DEBUG('%s.onUpdate: %s', __name__, tinfo)


def onPlug(bot):
    # 本插件被加载时被调用，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # 提醒：如果本插件设置为启动时自动加载，则本函数将延迟到登录完成后被调用
    # bot ： QQBot 对象
    DEBUG('%s.onPlug', __name__)


def onUnplug(bot):
    # 本插件被卸载时被调用
    # bot ： QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('%s.onUnplug', __name__)


def onExit(bot, code, reason, error):
    # MainLoop（主循环）终止时被调用， Mainloop 是一个无限循环，QQBot 登录成功后便开始运
    # 行，当且仅当以下事件发生时 Mainloop 终止：
    #     1） 调用了 bot.Stop() ，此时：
    #         code = 0, reason = 'stop', error = None
    #     2） 调用了 bot.Restart() ，此时：
    #         code = 201, reason = 'restart', error = None
    #     3） 调用了 bot.FreshRestart() ，此时：
    #         code = 202, reason = 'fresh-restart', error = None
    #     4） 调用了 sys.exit(x) （ x 不等于 0,201,202,203 ），此时：
    #         code = x, reason = 'system-exit', error = None
    #     5） 登录的 cookie 已过期，此时：
    #         code = 203, reason = 'login-expire', error = None
    #     6） 发生未知错误 e （暂未出现过，出现则表明 qqbot 程序内部可能存在错误），此时：
    #         code = 1, reason = 'unknown-error', error = e
    #
    # 一般情况下：
    #     发生 1/2/3/4 时，可以安全的调用 bot.List/SendTo/GroupXXX 等接口
    #     发生 5/6 时，调用 bot.List/SendTo/GroupXXX 等接口将出错
    #
    # 一般情况下，用户插件内的代码和运行错误会被捕捉并忽略，不会引起 MainLoop 的退出
    #
    # 本函数被调用后，会执行 sys.exit(code) 退出本次进程并返回到父进程，父进程会根据
    # “ code 的数值” 以及 “是否配置为自动重启模式” 来决定是否重启 QQBot 。
    #

    DEBUG('%s.onExit: %r %r %r', __name__, code, reason, error)


def onExpire(bot):
    # 登录过期时被调用
    # 注意 : 此时登录已过期，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    DEBUG('ON-EXPIRE')


@qqbotsched(hour='4')
def restart_sche(bot):
    DEBUG('RESTART scheduled')
    bot.FreshRestart()

@qqbotsched(minute='*/5', hour='12,13', day_of_week="1")
def get_ticket_info(bot):
    '''
    每周2下午1点获取票务信息
    '''
    global pocket48_handler
    global_config.TICKET_INFO = pocket48_handler.get_ticket_info()
    DEBUG('获取票务信息')


@qqbotsched(minute='*')
def update_conf(bot):
    """
    每隔1分钟读取配置文件
    :param bot:
    :return:
    """
    global pocket48_handler

    # 初始化人数统计
    for group_number in global_config.MEMBER_ROOM_MSG_LITE_GROUPS:
        if group_number not in global_config.GROUP_MEMBER_NUM.keys():
            global_config.GROUP_MEMBER_NUM[group_number] = 0

    DEBUG('member_room_msg_groups: %s, length: %d', ','.join(global_config.MEMBER_ROOM_MSG_GROUPS), len(pocket48_handler.member_room_msg_groups))
    DEBUG('member_room_comment_groups: %s, length: %d', ','.join(global_config.MEMBER_ROOM_COMMENT_GROUPS), len(pocket48_handler.member_room_comment_msg_groups))
    DEBUG('auto_reply_groups: %s, length: %d', ','.join(global_config.AUTO_REPLY_GROUPS), len(pocket48_handler.auto_reply_groups))
    DEBUG('member_live_groups: %s, length: %d', ','.join(global_config.MEMBER_LIVE_GROUPS), len(pocket48_handler.member_live_groups))
    DEBUG('member_room_comment_lite_groups: %s, length: %d', ','.join(global_config.MEMBER_ROOM_MSG_LITE_GROUPS), len(pocket48_handler.member_room_msg_lite_groups))


    # member_name = ConfigReader.get_property('root', 'member_name')
    # if global_config.MEMBER_NAME == '' or member_name != global_config.MEMBER_NAME:
    #     INFO('监控成员变更!')
    #     global_config.ROOM_ID = ConfigReader.get_member_room_number(member_name)
    #     if global_config.ROOM_ID == '':
    #         ERROR('该成员没有开通口袋房间！')
    #     global_config.MEMBER_ID = ConfigReader.get_property('live', member_name)
    #     pocket48_handler.init_msg_queues(global_config.ROOM_ID)
    #     global_config.MEMBER_NAME = member_name
    # DEBUG('当前监控的成员是: %s, 房间ID: %s, member_id: %s', member_name, global_config.ROOM_ID, global_config.MEMBER_ID)

    


@qqbotsched(hour='*', minute='0-55/3', second='10')
def get_room_msgs(bot):
    start_t = time.time()
    global pocket48_handler
    if pocket48_handler.is_login is False:
        DEBUG('登录失败,无法监控房间消息')
        return
    full_room_id_length = len(ConfigReader.get_all_member_room_id_list())
    if  0 < len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) < full_room_id_length:
        # 获取监控房间的room列表,循环获取房间消息
        for roomId in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
            r1 = pocket48_handler.get_member_room_msg(roomId[1])
            pocket48_handler.parse_room_msg(r1)
            # 开启房间评论
            # r2 = pocket48_handler.get_member_room_comment(global_config.ROOM_ID)
            # pocket48_handler.parse_room_comment(r2)
            # DEBUG('last_msg_time: %s', pocket48_handler.last_msg_time)
        end_t = time.time()
        DEBUG('获取房间消息 执行时间: %s', end_t-start_t)
    else:
        if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) == full_room_id_length and len(pocket48_handler.member_room_msg_ids) >= pocket48_handler.init_room_msg_ids_length:
            for roomId in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
                r1 = pocket48_handler.get_member_room_msg(roomId[1])
                pocket48_handler.parse_room_msg(r1)
                # 开启房间评论
                # r2 = pocket48_handler.get_member_room_comment(global_config.ROOM_ID)
                # pocket48_handler.parse_room_comment(r2)
                # DEBUG('last_msg_time: %s', pocket48_handler.last_msg_time)
            end_t = time.time()
            DEBUG('获取房间消息 执行时间: %s', end_t-start_t)
        else:
            return


@qqbotsched(minute='*', second='40')
def get_member_lives(bot):
    global pocket48_handler
    r = pocket48_handler.get_member_live_msg()
    pocket48_handler.parse_member_live(r, global_config.LIVING_MEMBER_ID_LIST)


# @qqbotsched(minute='*')
@qqbotsched(second='50', minute='20,50', hour='13,18,19', day_of_week='0, 4, 5,6')
def notify_performance(bot):
    INFO('检查公演日程')
    global pocket48_handler
    pocket48_handler.notify_performance(global_config.TICKET_INFO)


@qqbotsched(second='20', minute='*')
def notify_group_number(bot):
    INFO('检查群内人数')
    QQHandler.update()
    for g_number in global_config.MEMBER_ROOM_MSG_LITE_GROUPS:
        number = QQHandler.get_group_number(g_number)
        DEBUG('群%s: %d人', g_number, number)
        DEBUG('global_config.GROUP_MEMBER_NUM: %d', global_config.GROUP_MEMBER_NUM[g_number])
        if 0 < global_config.GROUP_MEMBER_NUM[g_number] < number:
            INFO('有新人入群啦~')

            g_obj = QQHandler.list_group([g_number])
            QQHandler.send_to_groups(g_obj, '中泰机器人欢迎你~/好棒')
        global_config.GROUP_MEMBER_NUM[g_number] = number

# @qqbotsched(second='10', minute='54', hour='19', day_of_week='1')
# def notify_buy_ticket(bot):
#     INFO('切票提示')
#     msg = '切票提示:\n还有几分钟马上切票了哦~/可爱'
#     QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)

@qqbotsched(minute='0-55/5')
def notify_bilibii_update(bot):
    INFO('检查b站更新情况')
    global pocket48_handler
    bilibili_video_list = pocket48_handler.get_bilibili_video_list()
    pocket48_handler.parse_bilibili_video_list(bilibili_video_list)

# @qqbotsched(minute='*', second='30')
# def get_member_room_msg_lite(bot):
#     global pocket48_handler
#     pocket48_handler.get_member_room_msg_lite()

