# -*- coding:utf-8 -*-

import requests
import json

import time
from qq.qqhandler import QQHandler
from qqbot.utf8logger import INFO, ERROR, DEBUG
from utils.download import Download

from utils import global_config, util

import Queue

import urllib, urllib2
import ssl

import sys

reload(sys)
sys.setdefaultencoding('utf8')
requests.packages.urllib3.disable_warnings()


class Member:
    def __init__(self, name, member_id, room_id):
        self.name = name
        self.member_id = member_id
        self.room_id = room_id


class Pocket48Handler:

    def __init__(self, auto_reply_groups, member_room_msg_groups, member_room_comment_msg_groups,
                 member_live_groups, member_room_msg_lite_groups):
        self.session = requests.session()
        self.token = '0'
        self.is_login = False
        self.VERSION = '5.0.0'
        self.init_room_msg_ids_length = 0

        self.last_msg_time = -1
        self.auto_reply_groups = auto_reply_groups
        self.member_room_msg_groups = member_room_msg_groups
        self.member_room_comment_msg_groups = member_room_comment_msg_groups
        self.member_live_groups = member_live_groups
        self.member_room_msg_lite_groups = member_room_msg_lite_groups

        self.member_room_msg_ids = []
        self.member_room_comment_ids = []
        self.member_live_ids = []
        # bilibili
        self.bilibili_video_ids = []

        # 成员房间未读消息数量
        self.unread_msg_amount = 0
        # 成员房间其他成员的未读消息数量
        self.unread_other_member_msg_amount = 0

        self.other_members_names = []
        self.last_other_member_msg_time = -1

        # self.live_urls = Queue.Queue(20)
        # self.download = Download(self.live_urls)
        # self.download.setDaemon(True)
        # self.download.start()

    def login(self, username, password):
        """
        登录
        :param username:
        :param password:
        :return:
        """
        if self.is_login is True:
            ERROR('已经登录！')
            return
        if username is None or password is None:
            ERROR('用户名或密码为空')
            return

        login_url = 'https://puser.48.cn/usersystem/api/user/v1/login/phone'
        params = {
            'latitude': '0',
            'longitude': '0',
            'password': str(password),
            'account': str(username),
        }
        res = {}
        try:
            res = self.session.post(login_url, json=params, headers=self.login_header_args(), verify=False).json()
        except Exception as e:
            ERROR('登录异常!')
            ERROR(e)
        # 登录成功
        if res['status'] == 200:
            self.token = res['content']['token']
            self.is_login = True
            INFO('登录成功, 用户名: %s', username)
            INFO('TOKEN: %s', self.token)
            return True
        else:
            ERROR('登录失败')
        return False

    def logout(self):
        """
        登出
        :return:
        """
        self.is_login = False
        self.token = '0'

    def get_member_live_msg(self, limit=30):
        """
        获取所有直播间信息
        :return:
        """
        # 登录失败 不访问需要鉴权的接口
        if not self.is_login:
            ERROR('尚未登录')
        url = 'https://plive.48.cn/livesystem/api/live/v1/memberLivePage'
        params = {
            "giftUpdTime": 1503766100000,
            "groupId": 0,  # SNH48 Group所有人
            "lastTime": 0,
            "limit": limit,
            "memberId": 0,
            "type": 0
        }
        try:
            r = self.session.post(url, data=json.dumps(params), headers=self.live_header_args(), verify=False)
        except Exception as e:
            ERROR('获取成员直播失败')
            ERROR(e)
        return r.text

    def get_member_room_msg(self, room_id, limit=5):
        """
        获取成员房间消息
        :param limit:
        :param room_id: 房间id
        :return:
        """
        if not self.is_login:
            ERROR('尚未登录')
            return False
        # url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/chat'
        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/mainpage'
        params = {
            "roomId": room_id, "lastTime": 0, "limit": limit, "chatType": 0
        }
        try:
            r = self.session.post(url, data=json.dumps(params), headers=self.juju_header_args(), verify=False)
        except Exception as e:
            ERROR('获取成员消息失败')
            ERROR(e)
        return r.text

    def get_ticket_info(self):
        """
        获取票务信息
        """
        url = 'http://www.gnz48.com/ticket/ticketsinfo.php?act=recent'
        try:
            r = requests.post(url, data={})
        except Exception as e:
            ERROR('获取票务')
            ERROR(e)
        f = r.json()
        all_ticket_info_list = f
        now = time.time()
        useful_ticket_info = []
        for item in all_ticket_info_list:

            perform_time = int(item['pretime'])
            if perform_time - now > 0:
                useful_ticket_info.append(item)
        return useful_ticket_info

    def init_msg_queues(self, room_ids):
        """
        初始化房间消息队列 避免每次一开启 就发送n多消息
        :param room_ids:
        :return:
        """
        if len(room_ids) > 0:
            try:
                self.member_room_msg_ids = []
                self.member_room_comment_ids = []
                self.member_live_ids = []
                

                self.unread_msg_amount = 0

                for room_id in room_ids:

                    r1 = self.get_member_room_msg(room_id[1])
                    # r2 = self.get_member_room_comment(room_id)

                    r1_json = json.loads(r1)
                    # r2_json = json.loads(r2)
                    for r in r1_json['content']['data']:
                        msg_id = r['msgidClient']
                        self.member_room_msg_ids.append(msg_id)
                self.init_room_msg_ids_length = len(self.member_room_msg_ids)

                # for r in r2_json['content']['data']:
                #     msg_id = r['msgidClient']
                #     self.member_room_comment_ids.append(msg_id)

                DEBUG('成员消息队列: %s', len(self.member_room_msg_ids))
                # DEBUG('房间评论队列: %s', len(self.member_room_comment_ids))
                DEBUG('房间未读消息数量: %d', self.unread_msg_amount)
            except Exception as e:
                ERROR('初始化房间消息队列失败')
                ERROR(e)
        else:
            return

    def init_bilibili_video_queues(self, bilibili_video_list):
        """
        初始化b站投稿队列 避免每次一开启 就发送n多消息
        :param room_ids:
        :return:
        """
        try:
            self.bilibili_video_ids = []

            for bilibili_video in bilibili_video_list:
                video_id = bilibili_video['aid']
                self.bilibili_video_ids.append(video_id)

            DEBUG('b站视频消息队列: %s', len(self.bilibili_video_ids))
        except Exception as e:
            ERROR('初始化b站视频消息队列失败')
            ERROR(e)

    def get_member_room_msg_lite(self):
        """
        发送成员房间消息（简易版，只提醒在房间里出现）
        :return:
        """
        time_now = time.time()
        msg = ''

        if self.unread_other_member_msg_amount > 0 and len(self.member_room_msg_lite_groups) > 0:
            if self.last_other_member_msg_time < 0 or time_now - self.last_other_member_msg_time >= 10 * 60:
                DEBUG('其他成员出现在房间中')
                member_name = ', '.join(self.other_members_names)
                QQHandler.send_to_groups(self.member_room_msg_lite_groups, '%s来你们灰的房间里串门啦~' % member_name)
                self.unread_other_member_msg_amount = 0
            self.last_other_member_msg_time = time_now
        if self.unread_msg_amount > 0 and len(self.member_room_msg_lite_groups) > 0:
            # 距离上一次提醒时间超过10分钟且有未读消息
            if self.last_msg_time < 0 or time_now - self.last_msg_time >= 10 * 60:
                DEBUG('向大群发送简易版提醒')
                msg = util.random_str(global_config.ROOM_MSG_LITE_NOTIFY)
                QQHandler.send_to_groups(self.member_room_msg_lite_groups, msg)
                INFO(msg)
                self.unread_msg_amount = 0
            else:
                DEBUG('不向大群发送简易版提醒')
            self.last_msg_time = time_now
        else:
            INFO('最近10分钟内没有未读消息')

    def parse_room_msg(self, response):
        """
        对成员消息进行处理
        :param response:
        :return:
        """
        DEBUG('parse room msg response: %s', response)
        rsp_json = json.loads(response)
        msgs = {}
        try:
            msgs = rsp_json['content']['data']
        except Exception as e:
            ERROR('房间消息异常')
            ERROR(e)
            return

        message = ''
        for msg in msgs:
            extInfo = json.loads(msg['extInfo'])
            msg_id = msg['msgidClient']  # 消息id

            if msg_id in self.member_room_msg_ids:
                continue

            if extInfo['senderRole'] != 1:  # 其他成员的消息
                self.unread_other_member_msg_amount += 1
                member_name = extInfo['senderName']
                if member_name == '你们的小可爱':
                    member_name = 'YBY'
                if member_name not in self.other_members_names:
                    self.other_members_names.append(member_name)
            else:
                self.unread_msg_amount += 1

            DEBUG('成员消息')
            self.member_room_msg_ids.append(msg_id)
            message_object = extInfo['messageObject']

            DEBUG('extInfo.keys():' + ','.join(extInfo.keys()))
            if msg['msgType'] == 0:  # 文字消息
                if message_object == 'text':  # 普通消息
                    DEBUG('普通消息')
                    name = extInfo['senderName']
                    default_name = '成员'
                    nickname = util.get_member_nickname(name, default_name)
                    message = ('【%s消息】[%s]-%s: %s\n' % (nickname, msg['msgTimeStr'], extInfo['senderName'], extInfo['text'])) + message
                elif message_object == 'faipaiText':  # 翻牌消息
                    DEBUG('翻牌')
                    member_msg = extInfo['messageText']
                    fanpai_msg = extInfo['faipaiContent']
                    name = extInfo['senderName']
                    nickname = util.get_member_nickname(name)
                    message = ('【%s翻牌】[%s]-%s: %s\n【被翻牌】%s\n' % (
                    nickname, msg['msgTimeStr'], extInfo['senderName'], member_msg, fanpai_msg)) + message
                # TODO: 直播可以直接在房间里监控
                elif message_object == 'diantai':  # 电台直播
                    DEBUG('电台直播')
                    reference_content = extInfo['referenceContent']
                    live_id = extInfo['referenceObjectId']
                elif message_object == 'live':  # 露脸直播
                    DEBUG('露脸直播')
                    reference_content = extInfo['referenceContent']
                    live_id = extInfo['referenceObjectId']
            elif msg['msgType'] == 1:  # 图片消息
                bodys = json.loads(msg['bodys'])
                DEBUG('图片')
                if 'url' in bodys.keys():
                    url = bodys['url']
                    message = ('【图片】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url)) + message
            elif msg['msgType'] == 2:  # 语音消息
                DEBUG('语音消息')
                bodys = json.loads(msg['bodys'])
                if 'url' in bodys.keys():
                    url = bodys['url']
                    message = ('【语音】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url)) + message
            elif msg['msgType'] == 3:  # 小视频
                DEBUG('房间小视频')
                bodys = json.loads(msg['bodys'])
                if 'url' in bodys.keys():
                    url = bodys['url']
                    message = ('【小视频】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url)) + message

        if message and len(self.member_room_msg_groups) > 0:
            QQHandler.send_to_groups(self.member_room_msg_groups, message)
            # self.get_member_room_msg_lite()
            INFO('message: %s', message)
        DEBUG('成员消息队列: %s', len(self.member_room_msg_ids))

    def parse_room_comment(self, response):
        """
        对房间评论进行处理
        :param response:
        :return:
        """
        rsp_json = json.loads(response)
        msgs = rsp_json['content']['data']
        # DEBUG('parse room comment reponse: %s', response)
        message = ''
        for msg in msgs:
            extInfo = json.loads(msg['extInfo'])
            platform = extInfo['platform']
            msg_id = msg['msgidClient']
            message_object = extInfo['messageObject']

            if msg_id in self.member_room_comment_ids:
                continue
            self.member_room_comment_ids.append(msg_id)
            if extInfo['contentType'] == 1:  # 普通评论
                DEBUG('房间评论')
                message = ('【房间评论】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], extInfo['text'])) + message
            elif extInfo['contentType'] == 3:  # 房间礼物
                DEBUG('礼物')
            else:
                DEBUG('其他类型评论')

        INFO('message: %s', message)
        DEBUG('length of comment groups: %d', len(self.member_room_comment_msg_groups))
        if message and len(self.member_room_comment_msg_groups) > 0:
            QQHandler.send_to_groups(self.member_room_comment_msg_groups, message)
        DEBUG('房间评论队列: %s', len(self.member_room_comment_ids))

    def get_member_room_comment(self, room_id, limit=20):
        """
        获取成员房间的粉丝评论
        :param limit:
        :param room_id: 房间id
        :return:
        """

        if not self.is_login:
            ERROR('尚未登录')
            return False
        # url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/comment'
        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/boardpage'
        params = {
            "roomId": room_id, "lastTime": 0, "limit": limit, "isFirst": "true"
        }
        # 收到响应
        try:
            r = self.session.post(url, data=json.dumps(params), headers=self.juju_header_args(), verify=False)
        except Exception as e:
            ERROR('获取房间评论失败')
            ERROR(e)
        return r.text

    def parse_member_live(self, response, living_member_id_list):
        """
        对直播列表进行处理，找到正在直播的指定成员
        :param member_id:
        :param response:
        :return:
        """
        try:
            rsp_json = json.loads(response)
        except Exception as e:
            ERROR('获取直播接口不报错，但拿不到数据')
            ERROR(e)
            return
        # 当前没有人在直播
        if 'liveList' not in rsp_json['content'].keys():
            # print 'no live'
            DEBUG('当前没有人在直播')
            return
        live_list = rsp_json['content']["liveList"]
        DEBUG('当前正在直播的人数: %d', len(live_list))
        # print '当前正在直播的人数: %d' % len(live_list)
        msg = ''
        # DEBUG('直播ID列表: %s', ','.join(self.member_live_ids))
        for live in live_list:
            live_id = live['liveId']
            # DEBUG(live.keys())
            # print '直播人: %s' % live['memberId']
            # DEBUG('直播人(response): %s, 类型: %s', live['memberId'], type(live['memberId']))
            # DEBUG('member_id(参数): %s, 类型: %s', member_id, type(member_id))
            DEBUG('memberId %s is in live: %s, live_id: %s', live['memberId'], live['title'], live_id)
            DEBUG('stream path: %s', live['streamPath'])
            # DEBUG('member_live_ids list: %s', ','.join(self.member_live_ids))
            # DEBUG('live_id is in member_live_ids: %s', str(live_id in self.member_live_ids))
            
            for member_id in living_member_id_list:
                if live['memberId'] == int(member_id) and live_id not in self.member_live_ids:
                    DEBUG('[被监控成员正在直播]member_id: %s, live_id: %', member_id, live_id)
                    start_time = util.convert_timestamp_to_timestr(live['startTime'])
                    stream_path = live['streamPath']  # 流地址
                    name = live['title'].encode("utf-8").split('的')[0]
                    sub_title = live['subTitle']  # 直播名称
                    live_type = live['liveType']
                    # url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' % live_id
                    if live_type == 1:  # 露脸直播
                        msg += '%s开露脸直播了: %s\n开始时间: %s\n' % (name, sub_title, start_time)
                    elif live_type == 2:  # 电台直播
                        msg += '%s开电台直播了: %s\n开始时间: %s\n' % (name, sub_title, start_time)
                    self.member_live_ids.append(live_id)

                    # 录制直播
                    # name = '%s_%s' % (member_id, live['startTime'])
                    # # self.download.setName(name)
                    # self.live_urls.put(name)
                    # self.live_urls.put(stream_path)

        DEBUG(msg)
        if msg and len(self.member_live_groups) > 0:
            QQHandler.send_to_groups(self.member_live_groups, msg)

    def parse_member_live_now(self, response, living_member_id_list):
        """
        对直播列表进行处理，找到正在直播的指定成员
        :param member_id:
        :param response:
        :return:
        """
        rsp_json = json.loads(response)
        # 当前没有人在直播
        if 'liveList' not in rsp_json['content'].keys():
            # print 'no live'
            DEBUG('当前没有人在直播')
            QQHandler.send_to_groups(self.member_live_groups, '当前没有人在直播~')
            return
        live_list = rsp_json['content']["liveList"]
        DEBUG('当前正在直播的人数: %d', len(live_list))
        # print '当前正在直播的人数: %d' % len(live_list)
        msg = ''
        # DEBUG('直播ID列表: %s', ','.join(self.member_live_ids))
        for live in live_list:
            live_id = live['liveId']
            # DEBUG(live.keys())
            # print '直播人: %s' % live['memberId']
            # DEBUG('直播人(response): %s, 类型: %s', live['memberId'], type(live['memberId']))
            # DEBUG('member_id(参数): %s, 类型: %s', member_id, type(member_id))
            DEBUG('memberId %s is in live: %s, live_id: %s', live['memberId'], live['title'], live_id)
            DEBUG('stream path: %s', live['streamPath'])
            # DEBUG('member_live_ids list: %s', ','.join(self.member_live_ids))
            # DEBUG('live_id is in member_live_ids: %s', str(live_id in self.member_live_ids))
            
            for member_id in living_member_id_list:
                if live['memberId'] == int(member_id):
                    DEBUG('[被监控成员正在直播]member_id: %s, live_id: %', member_id, live_id)
                    start_time = util.convert_timestamp_to_timestr(live['startTime'])
                    stream_path = live['streamPath']  # 流地址
                    name = live['title'].encode("utf-8").split('的')[0]
                    sub_title = live['subTitle']  # 直播名称
                    live_type = live['liveType']
                    # url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' % live_id
                    if live_type == 1:  # 露脸直播
                        msg += '%s露脸直播: %s\n开始时间: %s\n' % (name, sub_title, start_time)
                    elif live_type == 2:  # 电台直播
                        msg += '%s电台直播: %s\n开始时间: %s\n' % (name, sub_title, start_time)

                    # 录制直播
                    # name = '%s_%s' % (member_id, live['startTime'])
                    # # self.download.setName(name)
                    # self.live_urls.put(name)
                    # self.live_urls.put(stream_path)

        DEBUG(msg)
        if msg and len(self.member_live_groups) > 0:
            msg = '当前直播:\n' + msg
            QQHandler.send_to_groups(self.member_live_groups, msg)
        else:
            QQHandler.send_to_groups(self.member_live_groups, '当前没有人在直播~')

    def login_header_args(self):
        """
        构造登录请求头信息
        :return:
        """
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': '865873033980602',
            'token': '0',
            'version': self.VERSION,
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '75',
            'Host': 'puser.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache'
        }
        return header

    def live_header_args(self):
        """
        构造直播请求头信息
        :return:
        """
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': '865873033980602',
            'token': self.token,
            'version': self.VERSION,
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '87',
            'Host': 'plive.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache'
        }
        return header

    def juju_header_args(self):
        """
        构造聚聚房间请求头信息
        :return:
        """
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': '865873033980602',
            'token': self.token,
            'version': self.VERSION,
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '55',
            'Host': 'pjuju.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache'
        }
        return header

    def notify_performance(self, schedules):
        '''
        直播提醒
        '''
        notify_str = ''
        if len(schedules) > 0:
            for s in schedules:
                perform_time = int(s['pretime'])
                diff = perform_time - time.time()
                if 0 < diff <= 15 * 60:
                    live_link = self.live_url_bilibili_or_migu(s)
                    live_msg = '直播传送门: %s' % live_link
                    notify_str += '%s\n %s\n 时间:%s\n %s\n' % (
                    global_config.PERFORMANCE_NOTIFY, s['title'], s['addtime'], live_msg)
            INFO('notify str: %s', notify_str)
            if notify_str:
                QQHandler.send_to_groups(self.member_room_msg_groups, notify_str)
        else:
            QQHandler.send_to_groups(self.member_room_msg_groups, '近期没有票务')

    def live_url_bilibili_or_migu(self, schedule):
        '''
        判断公演直播地址是咪咕还是b站
        '''
        url = ''
        special = schedule['special']
        title = schedule['title']
        if '咪咕' in special:
            if 'Z队' in title:
                url = 'http://music.migu.cn/v2/live/462'
            elif 'G队' in title:
                ulr = 'http://music.migu.cn/v2/live/490'
            elif 'NIII队' in title:
                url = '地址暂时不知道'
            elif '预备生' in title:
                url = '地址暂时不知道'
            url = '（咪咕）' + url
            return url
        else:
            url = global_config.LIVE_LINK[0]
            return url

    def get_current_ticket_info_msg(self, schedules):
        '''
        自动回复票务信息
        最近公演：msg
        '''
        schedules.reverse()
        msg = '票务:\n'
        now = time.time()
        for s in schedules:
            msg += '%s\n时间:%s\n特殊说明:%s\n' % (s['title'], s['addtime'], s['special'])
        QQHandler.send_to_groups(self.auto_reply_groups, msg)

    def get_tuling_ai(self, id, info):
        api_key = '750ee100645a4707bf1bb55efc4032ed'
        url = 'http://www.tuling123.com/openapi/api'
        post_data = {
            'key': api_key,
            'info': info,
            'userid': id
        }
        json_obj = json.dumps(post_data)
        request = urllib2.Request(url, json_obj)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            msg = ''
            text = ''
            if (content):
                res_obj = json.loads(content)
                type_code = res_obj['code']
                text = res_obj['text']
                if type_code == 100000:
                    INFO('图灵文字类')
                    msg = text
                elif type_code == 200000:
                    INFO('图灵链接类')
                    msg = '%s\n%s' % (text, res_obj['url'])
                elif type_code == 302000:
                    INFO('图灵新闻类')
                    news_list = res_obj['list']
                    for news in news_list:
                        news_msg = '%s\n%s\n\n' % (news['article'], news['detailurl'])
                        msg += news_msg
                    msg += text
                elif type_code == 308000:
                    INFO('图灵菜谱类')
                    food_list = res_obj['list']
                    for food in food_list:
                        food_msg = '%s\n%s\n\n' % (food['name'], food['detailurl'])
                        msg += food_msg
                else:
                    msg = text
                return msg
        except Exception as e:
            ERROR('请求图灵机器人接口发生错误')
            print e
            return '图灵机器人接口出错啦'

    def get_bilibili_video_list(self):
        url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=27363163&pagesize=10&tid=0&page=1&keyword=&order=pubdate'
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            if (content):
                res_obj = json.loads(content)
                return res_obj['data']['vlist']
        except Exception as e:
            ERROR('请求b站接口出错')
            print e
            return

    def parse_bilibili_video_list(self, bilibili_video_list):
        msg = ''
        for bilibili_video in bilibili_video_list:
            video_id = bilibili_video['aid']
            if video_id not in self.bilibili_video_ids:
                timeStamp = bilibili_video['created']
                localTime = time.localtime(timeStamp) 
                strTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
                address = 'https://www.bilibili.com/video/av%s' % (video_id)
                msg += '%s\n投稿时间:%s\n传送门:%s\n' % (bilibili_video['title'], strTime, address)
                self.bilibili_video_ids.append(video_id)
        DEBUG(msg)
        if msg and len(self.member_room_msg_groups) > 0:
            msg = 'b站官方账号更新:\n' + msg
            QQHandler.send_to_groups(self.member_room_msg_groups, msg)

    def deactive_member_by_name(self, name):
        pin_yin = util.get_member_pinyin(name)
        msg = ''
        stop_loop = False
        for index, item in enumerate(global_config.ACTIVE_MEMBER_ROOM_ID_LIST):
            if pin_yin == item[0]:
                pop = global_config.ACTIVE_MEMBER_ROOM_ID_LIST.pop(index)
                global_config.DEACTIVE_MEMBER_ROOM_ID_LIST.append(pop)
                msg = '已屏蔽%s房间消息' % (name)
                QQHandler.send_to_groups(self.member_room_msg_groups, msg)
                break
            else:
                if stop_loop is True:
                    break
                for item in global_config.DEACTIVE_MEMBER_ROOM_ID_LIST:
                    if pin_yin == item[0]:
                        msg = '%s已在小黑屋内' % (name)
                        QQHandler.send_to_groups(self.member_room_msg_groups, msg)
                        stop_loop = True
                        break
        if msg == '':
            msg = '%s不在监控范围内' % (name)
            QQHandler.send_to_groups(self.member_room_msg_groups, msg)


    def active_member_by_name(self, name):
        pin_yin = util.get_member_pinyin(name)
        msg = ''
        stop_loop = False
        for index, deactive_item in enumerate(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST):
            if pin_yin == deactive_item[0]:
                pop = global_config.DEACTIVE_MEMBER_ROOM_ID_LIST.pop(index)
                # 先请求这个id的消息 放进消息列表里面
                r1 = self.get_member_room_msg(pop[1])
                r1_json = json.loads(r1)
                for r in r1_json['content']['data']:
                    msg_id = r['msgidClient']
                    self.member_room_msg_ids.append(msg_id)

                global_config.ACTIVE_MEMBER_ROOM_ID_LIST.append(pop)
                msg = '已开启%s房间消息' % (name)
                QQHandler.send_to_groups(self.member_room_msg_groups, msg)
                break
            else:
                if stop_loop is True:
                    break
                for active_item in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
                    if pin_yin == active_item[0]:
                        msg = '%s已在小白屋内' % (name)
                        QQHandler.send_to_groups(self.member_room_msg_groups, msg)
                        stop_loop = True
                        break
        if msg == '':
            msg = '%s不在监控范围内' % (name)
            QQHandler.send_to_groups(self.member_room_msg_groups, msg)



if __name__ == '__main__':
    handler = Pocket48Handler([], [], [], [], [])

    # handler.notify_performance()

    handler.login('*', '*')

    # response = handler.get_member_live_msg()
    # handler.parse_member_live(response, 528331)

    r = handler.get_member_room_msg(5780791)
    print r
    handler.parse_room_msg(r)
    r2 = handler.get_member_room_comment(5780791)
    print r2
    handler.parse_room_comment(r2)
    # print handler.convert_timestamp_to_timestr(1504970619679)
