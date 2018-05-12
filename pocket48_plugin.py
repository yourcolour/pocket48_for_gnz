# -*- coding: utf-8 -*-
import time

from log.my_logger import logger as my_logger
from utils.config_reader import ConfigReader
from pocket48.pocket48_handler import Pocket48Handler
from qq.qqhandler import QQHandler
from utils import global_config, util
from utils.scheduler import scheduler
import json
from cqhttp import CQHttp
# from modian_plugin import modian_handler

bot = CQHttp(api_root='http://0.0.0.0:5700/')

pocket48_handler = None

# 一.初始化
def update_conf():
    '''
    读取配置文件
    '''
    global pocket48_handler
    ConfigReader.read_conf()
    global_config.ACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
    global_config.LIVING_MEMBER_ID_LIST = ConfigReader.get_living_member_id_list()

    global_config.LAST_TICKET_INFO_ID = ConfigReader.get_property('last_ticket_info_id', 'id')
    global_config.ROBOT_QQ = ConfigReader.get_property('qq_conf', 'qq')
    global_config.AUTO_REPLY_GROUPS = ConfigReader.get_property('qq_conf', 'auto_reply_groups').split(';')
    global_config.MEMBER_ROOM_MSG_GROUPS = ConfigReader.get_property('qq_conf', 'member_room_msg_groups').split(';')
    global_config.MEMBER_LIVE_GROUPS = ConfigReader.get_property('qq_conf', 'member_live_groups').split(';')

    auto_reply_groups = global_config.AUTO_REPLY_GROUPS
    member_room_msg_groups = global_config.MEMBER_ROOM_MSG_GROUPS
    member_live_groups = global_config.MEMBER_LIVE_GROUPS

    pocket48_handler.member_room_msg_groups = member_room_msg_groups
    pocket48_handler.auto_reply_groups = auto_reply_groups
    pocket48_handler.member_live_groups = member_live_groups

    global_config.AT_AUTO_REPLY = ConfigReader.get_property('profile', 'at_auto_reply').split(';')
    global_config.LIVE_LINK=ConfigReader.get_property('profile', 'live_link')

    global_config.PERFORMANCE_NOTIFY = ConfigReader.get_property('profile', 'performance_notify')
    global_config.NO_SUCH_COMMAND = ConfigReader.get_property('profile', 'no_such_command')
    # 读取成员信息表
    # global_config.MEMBER_JSON = json.load(open('data/member.json', encoding='utf8'))

    

# 初始化
pocket48_handler = Pocket48Handler([], [], [])

#读取配置文件
update_conf()
# 获取票务
global_config.TICKET_INFO = pocket48_handler.get_ticket_info()
# 获取今日有缘资料
global_config.LUCKY_MEMBERS_INFO = util.member_list
# 登录口袋48
username = ConfigReader.get_property('user', 'username')
password = ConfigReader.get_property('user', 'password')
pocket48_handler.login(username, password)
# 哔哩哔哩消息初始化
bilibili_video_list = pocket48_handler.get_bilibili_video_list()
pocket48_handler.init_bilibili_video_queues(bilibili_video_list)
# 成员房间消息初始队列化
pocket48_handler.init_msg_queues(global_config.ACTIVE_MEMBER_ROOM_ID_LIST)
# 用于标记星期二票务
count = 0
# 二.接收群消息的反应
@bot.on_message('group')
def onQQMessage(context):
    global pocket48_handler
    group_id = str(context['group_id'])
    # if group_id in pocket48_handler.member_room_msg_groups or group_id in modian_handler.modian_notify_groups:
    if group_id in pocket48_handler.member_room_msg_groups:
        pass
    else:
        return
    content = context['message']
    user_id = context['user_id']
    my_logger.debug('user_id: {}, message: {}'.format(user_id, content))
    at_msg = '[CQ:at,qq={}]'.format(global_config.ROBOT_QQ)
    if at_msg in content:  # 在群中@机器人
        if pocket48_handler.can_talk == False:
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用聊天功能, 想开启聊天功能,请输入 -开启聊天')
            return
        strs = content.split(at_msg)[1].strip()
        if strs :
            return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, pocket48_handler.get_tuling_ai(user_id, strs), True)
        else:
            return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, util.random_str(global_config.AT_AUTO_REPLY), True)
    elif content.startswith('-'):  # 以'-'开头才能触发自动回复
        if content == '-票务' or content == '-公演':
            global_config.TICKET_INFO = pocket48_handler.get_ticket_info()
            pocket48_handler.get_current_ticket_info_msg(global_config.TICKET_INFO)
        elif content == '-屏蔽全部房间' or content == '-屏蔽所有房间':
            if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                global_config.DEACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
                global_config.ACTIVE_MEMBER_ROOM_ID_LIST = []
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '已屏蔽全部房间')

            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '当前已屏蔽全部房间，请不要重复输入命令')
        elif content == '-开启全部房间' or content == '-开启所有房间':
            if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
                global_config.ACTIVE_MEMBER_ROOM_ID_LIST = ConfigReader.get_all_member_room_id_list()
                global_config.DEACTIVE_MEMBER_ROOM_ID_LIST = []
                pocket48_handler.init_msg_queues(global_config.ACTIVE_MEMBER_ROOM_ID_LIST)
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '已开启全部房间')
            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '当前已开启全部房间，请不要重复输入命令')
        elif content == '-睡觉':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if QQHandler.send_message_permission is True:
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已睡觉')
                    QQHandler.send_message_permission = False
                else:
                    bot.send(context, '中泰机器人已睡觉,想唤醒机器人请输入 -起床')
            else:
                bot.send(context, '管理员或群主才能使用 -睡觉 命令')
        elif content == '-起床':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if QQHandler.send_message_permission is False:
                    QQHandler.send_message_permission = True
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已起床')
                else:
                    bot.send(context, '中泰机器人已起床,想机器人睡觉请输入 -睡觉')
            else:
                bot.send(context, '管理员或群主才能使用 -起床 命令')
        elif '-屏蔽' in content and '房间' in content:
            name = util.get_order_name(content)
            # 命令是否包含成员名字
            if util.is_name_in_member_list(name):
                # 屏蔽逻辑
                pocket48_handler.deactive_member_by_name(name)
            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '屏蔽失败, 无法识别该成员,请确保命令输入正确')
        elif '-开启' in content and '房间' in content:
            name = util.get_order_name(content)
            # 命令是否包含成员名字
            if util.is_name_in_member_list(name):
                # 开启逻辑
                pocket48_handler.active_member_by_name(name)
            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '开启失败, 无法识别该成员,请确保命令输入正确')
        elif content == '-直播':
            r = pocket48_handler.get_member_live_msg()
            pocket48_handler.parse_member_live_now(r, global_config.LIVING_MEMBER_ID_LIST)
        elif content == '-小黑屋':
            msg = util.get_black_room_list()
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg)
        elif content == '-小白屋':
            msg = util.get_white_room_list()
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg)
        elif '-拉' in content and '条' in content and '消息' in content:
            if pocket48_handler.can_pull_message == False:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用拉取功能, 想开启拉取功能,请输入 -开启拉取')
                return
            num, name = util.get_msg_order_name_num(content)
            if util.is_name_in_member_list(name) and util.is_num_in_limt(num):
                pocket48_handler.get_some_room_msg(name, int(num))
            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '成员名或数量有误（1~20），请确保命令输入正确')
        elif content == '-禁用聊天':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if pocket48_handler.can_talk == True:
                    pocket48_handler.can_talk = False
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用聊天功能')
                else:
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用聊天功能, 想开启聊天功能,请输入 -开启聊天')
            else:
                return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '管理员或群主才能使用 -禁用聊天 命令')
        elif content == '-开启聊天':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if pocket48_handler.can_talk == False:
                    pocket48_handler.can_talk = True
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已开启聊天功能')
                else:
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已开启聊天功能, 想禁用聊天功能,请输入 -禁用聊天')
            else:
                return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '管理员或群主才能使用 -开启聊天 命令')
        elif content == '-开启拉取':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if pocket48_handler.can_pull_message == False:
                    pocket48_handler.can_pull_message = True
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已开启手动拉取功能')
                else:
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已开启手动拉取功能, 想禁用手动拉取功能,请输入 -禁用拉取')
            else:
                return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '管理员或群主才能使用 -开启拉取 命令')
        elif content == '-禁用拉取':
            info = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])
            role = info['role']
            if role == 'owner' or role == 'admin':
                if pocket48_handler.can_pull_message == True:
                    pocket48_handler.can_pull_message = False
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用手动拉取功能')
                else:
                    QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '机器人已禁用手动拉取功能, 想开启手动拉取功能,请输入 -开启拉取')
            else:
                return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '管理员或群主才能使用 -禁用拉取 命令')
        elif content == '-今日有缘':
            msg = ''
            is_in_limit_time = util.is_in_limit_time()
            if is_in_limit_time:
                msg = pocket48_handler.today_lucky_member(user_id)
            else:
                msg = '请在指定时间内进行今日有缘测试(每天0~9点)'
            return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg, True)
        elif content == '-重生':
            msg = ''
            is_in_limit_time = util.is_in_limit_time()
            if is_in_limit_time:
                msg = pocket48_handler.rebirth(user_id)
            else:
                msg = '请在指定时间内进行重生(每天0~9点)'
            return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg, True)
        # elif '集资' in content:
        #     order_flag = util.get_modian_flag(content)
        #     target_obj = None
        #     for modian in global_config.MODIAN_ARRAY:
        #         if order_flag == modian.order_flag:
        #             target, current, pro_name = modian_handler.get_current_and_target(modian)
        #             ranking_list = modian_handler.get_modian_rankings(modian)
        #             target_obj = {}
        #             target_obj['target'] = target
        #             target_obj['current'] = current
        #             target_obj['pro_name'] = pro_name
        #             target_obj['ranking_list'] = ranking_list
        #             break
        #     if target_obj:
        #         msg = '{}:\n目标金额：{}元  当前集资：{}元\n'.format(target_obj['pro_name'], target_obj['target'], target_obj['current'])
        #         for index, rank in enumerate(target_obj['ranking_list']):
        #             msg = '{}{}、{} {}\n'.format(msg, rank['rank'], rank['nickname'], rank['backer_money'])
        #             if index >= 19:
        #                 break;
        #         QQHandler.send_to_groups_by_order(modian_handler.modian_notify_groups, msg)
        #     else:
        #         QQHandler.send_to_groups_by_order(modian_handler.modian_notify_groups, '没有监控%s集资' % (order_flag))
        # elif content == '-摩点项目':
        #     msg = '当前监控摩点项目（共%s个）:\n' % (len(global_config.MODIAN_ARRAY))
        #     for modian in global_config.MODIAN_ARRAY:
        #         msg += '%s,' % (modian.order_flag)
        #     QQHandler.send_to_groups_by_order(modian_handler.modian_notify_groups, msg)
        elif content == '-帮助' or content == '-说明':
            msg = '''
机器人使用说明:
一、命令类型 ( -命令前缀, ||同义词, /可选词, 【】变量, ""例子, *未开通命令）:
(1)"-直播":  查看所有正在直播的直播间.
(2)"-票务||公演": 查看尚未公演的票务信息.
(3)"-开启/屏蔽  所有||全部 房间":  开启/屏蔽 全部房间.
(4)"-开启/屏蔽【成员】房间":  开启/屏蔽 某成员房间.
(5)"-小白屋/小黑屋": 查看 开启/屏蔽 房间消息的成员名单.
(6)"-拉【数量】条【成员】消息": 拉取房间消息.（例:"-拉10条王炯义消息",【数量】范围:1~20, 仅限小白屋和小黑屋【成员】） 
(7)"-摩点项目":  查看监控的集资项目.（例:"-摩点项目", 机器人回复"王翠菲生诞,", 输入"-王翠菲生诞"+"集资"即可查询）
(8*)"-【摩点项目】集资":  查看某个摩点项目集资详情. （例:"-王翠菲生诞集资", 该命令6月开通）
(9)"-今日有缘":  测试今日有缘成员.(每天0~9点可进行, 每天0点重置今日有缘)
(10)"-重生":  重生今日有缘成员.（先进行"-今日有缘", 每天重生上限1次）
(11)"-钟妹/泰叔":  钟妹/泰叔 随机语音.（不同时段有一段专属语音）
(12)"-帮助||说明":  机器人使用说明.
(13)"@机器人" + 聊天内容进行聊天:  每天上限1000次,河内梗待完善.

二、命令开关类型 (仅限群主或管理员使用)
(1)"-开启/禁用 拉取": 开/关 拉取房间消息功能 （即上面的功能6）
(2)"-开启/禁用 聊天": 开/关 机器人聊天功能. (即上面的功能12)
(3)"-睡觉/起床":  机器人睡觉/起床. (睡觉会关闭机器人所有功能, 起床后其它功能才能恢复)
'''
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg)
        elif content == '-钟妹':
            image = '1.jpg'
            msg1 = ('[CQ:image,file=%s]' % image)
            sound = util.random_record('钟妹')
            msg2 = ('[CQ:record,file=%s]' % sound)
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg1)
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg2)
        elif content == '-泰叔':
            image = '2.jpg'
            msg1 = ('[CQ:image,file=%s]' % image)
            sound = util.random_record('泰叔')
            msg2 = ('[CQ:record,file=%s]' % sound)
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg1)
            QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, msg2)
        elif content == '-最新票务':
            if util.is_Tuesday():
                html = pocket48_handler.get_page()
                pocket48_handler.parse_page_now(html)
            else:
                QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, '最新票务只能在周二获取')
        else:  # 无法识别命令
            return QQHandler.send_to_groups_by_order(pocket48_handler.member_room_msg_groups, global_config.NO_SUCH_COMMAND, True)
    
@bot.on_event('group_increase')
def handle_group_increase(context):
    info = bot.get_group_member_info(group_id=context['group_id'],
                                     user_id=context['user_id'])
    recommend_member = util.random_str(util.member_list)['name']
    bot.send(context, message='[CQ:at,qq={}] 中泰机器人欢迎你~\n新人推谁? 爆照~\n{} 了解一下'.format(context['user_id'], recommend_member))


@bot.on_event('group_decrease')
def handle_group_decrease(context):
    user_id = context['user_id']
    logger.info('有人拔出了自己的电池，QQ号: %s', user_id)

# 三.定时任务
@scheduler.scheduled_job('cron', minute='*/2', second='30')
def get_room_msgs():
    start_t = time.time()
    global pocket48_handler
    if pocket48_handler.is_login is False:
        my_logger.debug('登录失败,无法监控房间消息')
        return
    full_room_id_length = len(ConfigReader.get_all_member_room_id_list())
    if  0 < len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) < full_room_id_length:
        # 获取监控房间的room列表,循环获取房间消息
        for roomId in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
            source_room_name = ''
            for member in global_config.LUCKY_MEMBERS_INFO:
                if member['pin_yin'] == roomId[0]:
                    source_room_name = member['name']
                    break
            r1 = pocket48_handler.get_member_room_msg(roomId[1])
            pocket48_handler.parse_room_msg(r1, source_room_name)
        end_t = time.time()
        my_logger.debug('获取房间消息 执行时间: {}'.format(end_t-start_t))
    else:
        if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) == full_room_id_length and len(pocket48_handler.member_room_msg_ids) >= pocket48_handler.init_room_msg_ids_length:
            for roomId in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
                source_room_name = ''
                for member in global_config.LUCKY_MEMBERS_INFO:
                    if member['pin_yin'] == roomId[0]:
                        source_room_name = member['name']
                        break
                r1 = pocket48_handler.get_member_room_msg(roomId[1])
                pocket48_handler.parse_room_msg(r1, source_room_name)
            end_t = time.time()
            my_logger.debug('获取房间消息 执行时间: {}'.format(end_t-start_t))
        else:
            return


@scheduler.scheduled_job('cron', minute='*', second='40')
def get_member_lives():
    global pocket48_handler
    r = pocket48_handler.get_member_live_msg()
    pocket48_handler.parse_member_live(r, global_config.LIVING_MEMBER_ID_LIST)

@scheduler.scheduled_job('cron', second='50', minute='20,50', hour='13,18,19', day_of_week='0, 4, 5,6')
def notify_performance():
    my_logger.info('检查公演日程')
    global pocket48_handler
    pocket48_handler.notify_performance(global_config.TICKET_INFO)

@scheduler.scheduled_job('cron', second='0', minute='50', hour='19', day_of_week='1')
def notify_buy_ticket():
    my_logger.info('切票提示')
    msg = '切票提示:\n还有10分钟马上切票了哦~/可爱'
    QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)

@scheduler.scheduled_job('cron', minute='*/5', second='50')
def notify_bilibii_update():
    my_logger.info('检查b站更新情况')
    global pocket48_handler
    bilibili_video_list = pocket48_handler.get_bilibili_video_list()
    pocket48_handler.parse_bilibili_video_list(bilibili_video_list)

@scheduler.scheduled_job('cron', second='*/30', hour='11,12,13', day_of_week='1')
def notify_latest_ticket_info():
    global count
    if count < 1:
        my_logger.info('检查周二最新票务情况')
        global pocket48_handler
        html = pocket48_handler.get_page()
        msg = pocket48_handler.parse_page(html)
        if msg:
            count += 1
            msg += '票务地址:https://shop.48.cn/tickets/item/%s' % global_config.LAST_TICKET_INFO_ID
            QQHandler.send_to_groups(pocket48_handler.member_room_msg_groups, msg)


# @scheduler.scheduled_job('cron', second='0', minute='0', hour='0', day_of_week='*')
# def reset_data():
#     global pocket48_handler
#     my_logger.info('清空今日有缘列表')
#     pocket48_handler.user_id_member_info_list = []

#     my_logger.info('清空房间消息id列表')
#     member_room_id_list = ConfigReader.get_all_member_room_id_list()
#     pocket48_handler.init_msg_queues(member_room_id_list)

#     my_logger.info('清空直播id列表')
#     pocket48_handler.member_live_ids = []
#     r = pocket48_handler.get_member_live_msg()
#     pocket48_handler.parse_member_live(r, global_config.LIVING_MEMBER_ID_LIST, True)

#     my_logger.info('清空bilibili列表')
#     bilibili_video_list = pocket48_handler.get_bilibili_video_list()
#     pocket48_handler.init_bilibili_video_queues(bilibili_video_list)


