# -*- coding:utf-8 -*-

import requests
import json
from pyquery import PyQuery as pq
import time
from log.my_logger import logger as my_logger
from qq.qqhandler import QQHandler
from utils import global_config, util
import urllib.request
import ssl
import os
import sqlite3
import sys
from utils.downloads import sound_downloda, image_download
requests.packages.urllib3.disable_warnings()


class Pocket48Handler:

    def __init__(self, auto_reply_groups, member_room_msg_groups, member_live_groups):
        self.session = requests.session()
        self.token = '0'
        self.is_login = False
        self.can_talk = True
        self.can_pull_message = True
        self.init_room_msg_ids_length = 0

        self.last_msg_time = -1
        self.auto_reply_groups = auto_reply_groups
        self.member_room_msg_groups = member_room_msg_groups
        self.member_live_groups = member_live_groups

        self.member_room_msg_ids = []
        self.member_live_ids = []
        # bilibili
        self.bilibili_video_ids = []
        self.user_id_member_info_list = []

        # 成员房间未读消息数量
        self.unread_msg_amount = 0
        # 成员房间其他成员的未读消息数量
        self.unread_other_member_msg_amount = 0

        self.other_members_names = []
        self.last_other_member_msg_time = -1

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'statistic', 'statistics.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_message (
                    message_id   VARCHAR,
                    type         INTEGER,
                    user_id      INTEGER,
                    user_name    VARCHAR,
                    message_time DATETIME,
                    content      VARCHAR,
                    fans_comment VARCHAR
                );
                """)
        cursor.close()

    def login(self, username, password):
        """
        登录
        :param username:
        :param password:
        :return:
        """
        if self.is_login is True:
            my_logger.error('已经登录！')
            return
        if username is None or password is None:
            my_logger.error('用户名或密码为空')
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
            my_logger.error('登录异常!')
            my_logger.error(e)
        # 登录成功
        if res['status'] == 200:
            self.token = res['content']['token']
            self.is_login = True
            my_logger.info('登录成功, 用户名: %s', username)
            my_logger.info('TOKEN: %s', self.token)
            return True
        else:
            my_logger.error('登录失败')
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
            my_logger.error('尚未登录')
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
            my_logger.error('获取成员直播失败')
            my_logger.error(e)
        return r.text

    def get_member_room_msg(self, room_id, limit=15):
        """
        获取成员房间消息
        :param limit:
        :param room_id: 房间id
        :return:
        """
        if not self.is_login:
            my_logger.error('尚未登录')
            return False
        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/mainpage'
        params = {
            "roomId": room_id, "lastTime": 0, "limit": limit, "chatType": 0
        }
        try:
            r = self.session.post(url, data=json.dumps(params), headers=self.juju_header_args(), verify=False)
        except Exception as e:
            my_logger.error('获取成员消息失败')
            my_logger.error(e)
        return r.text

    def get_ticket_info(self):
        """
        获取票务信息
        """
        url = 'http://www.gnz48.com/ticket/ticketsinfo.php?act=recent'
        try:
            r = requests.post(url, data={})
        except Exception as e:
            my_logger.error('获取票务')
            my_logger.error(e)
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

                self.unread_msg_amount = 0

                for room_id in room_ids:

                    r1 = self.get_member_room_msg(room_id[1])

                    r1_json = json.loads(r1)
                    for r in r1_json['content']['data']:
                        msg_id = r['msgidClient']
                        self.member_room_msg_ids.append(msg_id)
                self.init_room_msg_ids_length = len(self.member_room_msg_ids)


                my_logger.debug('成员消息队列: {}'.format(len(self.member_room_msg_ids)))
                my_logger.debug('房间未读消息数量: {}'.format(self.unread_msg_amount))
            except Exception as e:
                my_logger.error('初始化房间消息队列失败')
                my_logger.error(e)
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

            my_logger.debug('b站视频消息队列: {}'.format(len(self.bilibili_video_ids)))
        except Exception as e:
            my_logger.error('初始化b站视频消息队列失败')
            my_logger.error(e)

    def parse_room_msg(self, response, source_room_name, immediate=False):
        """
        对成员消息进行处理
        :param response:
        :return:
        """
        # my_logger.debug('parse room msg response: %s', response)
        rsp_json = json.loads(response)
        msgs = {}
        try:
            msgs = rsp_json['content']['data']
            msgs_reverse = list(reversed(msgs))
            cursor = self.conn.cursor()
        except Exception as e:
            my_logger.error('房间消息异常')
            my_logger.error(e)
            return

        message = ''
        try:
            for msg in msgs_reverse:
                extInfo = json.loads(msg['extInfo'])
                msg_id = msg['msgidClient']  # 消息id

                # 是否直接拉取消息
                if immediate == False:
                    # 如果msg_id已在列表里，就进行下一次循环，后面代码不执行
                    if msg_id in self.member_room_msg_ids:
                        continue
                    self.member_room_msg_ids.append(msg_id)

                if extInfo['senderRole'] != 1:  # 其他成员的消息
                    self.unread_other_member_msg_amount += 1
                    member_name = extInfo['senderName']
                    if member_name not in self.other_members_names:
                        self.other_members_names.append(member_name)
                else:
                    self.unread_msg_amount += 1

                my_logger.debug('成员消息')
                message_object = extInfo['messageObject']

                my_logger.debug('extInfo.keys():' + ','.join(extInfo.keys()))
                if msg['msgType'] == 0:  # 文字消息
                    if message_object == 'text':  # 普通消息
                        my_logger.debug('普通消息')
                        name = extInfo['senderName']
                        default_name = '成员'
                        nickname = util.get_member_nickname(name, default_name)
                        message = message + ('【%s消息】[%s]-%s: %s\n' % (nickname, msg['msgTimeStr'], extInfo['senderName'], extInfo['text']))
                        cursor.execute("""
                                INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content) VALUES
                                (?, ?, ?, ?, ?, ?)
                            """, (msg_id, 100, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], extInfo['text']))
                    elif message_object == 'faipaiText':  # 翻牌消息
                        my_logger.debug('普通翻牌')
                        member_msg = extInfo['messageText']
                        fanpai_msg = extInfo['faipaiContent']
                        name = extInfo['senderName']
                        nickname = util.get_member_nickname(name)
                        message = message + ('【被翻牌】%s\n【%s翻牌】[%s]-%s: %s\n\n' % (
                        fanpai_msg, nickname, msg['msgTimeStr'], extInfo['senderName'], member_msg))
                        cursor.execute("""
                                            INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content, fans_comment) VALUES
                                            (?, ?, ?, ?, ?, ?, ?)
                                    """, (msg_id, 101, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], member_msg, fanpai_msg))
                    # TODO: 直播可以直接在房间里监控
                    elif message_object == 'diantai':  # 电台直播
                        my_logger.debug('电台直播')
                        reference_content = extInfo['referenceContent']
                        live_id = extInfo['referenceObjectId']
                    elif message_object == 'live':  # 露脸直播
                        my_logger.debug('露脸直播')
                        reference_content = extInfo['referenceContent']
                        live_id = extInfo['referenceObjectId']
                    elif message_object == 'idolFlip':
                        my_logger.debug('付费翻牌功能')
                        user_name = extInfo['idolFlipUserName']
                        title = extInfo['idolFlipTitle']
                        content = extInfo['idolFlipContent']

                        question_id = extInfo['idolFlipQuestionId']
                        answer_id = extInfo['idolFlipAnswerId']
                        source = extInfo['idolFlipSource']
                        answer = self.parse_idol_flip(question_id, answer_id, source)
                        message = message + ('【问】%s: %s\n\n【答】%s: %s\n【翻牌时间】: %s\n\n' % (
                            user_name, content, extInfo['senderName'], answer, msg['msgTimeStr']))
                        cursor.execute("""
                            INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content, fans_comment) VALUES
                            (?, ?, ?, ?, ?, ?, ?)
                            """, (msg_id, 105, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], answer, user_name + ': ' + content))
                elif msg['msgType'] == 1:  # 图片消息
                    bodys = json.loads(msg['bodys'])
                    my_logger.debug('图片')
                    if 'url' in bodys.keys():
                        url = bodys['url']
                        if global_config.USING_COOLQ_PRO is True:
                            file_name = image_download(url, '/Users/yourcolour/coolq/data/image')
                            message = message + ('【图片】[%s]-%s: \n[CQ:image,file=%s]\n' % (msg['msgTimeStr'], extInfo['senderName'], file_name))
                        else:
                            message = message + ('【图片】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url))
                        cursor.execute("""
                               INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content) VALUES
                                                                (?, ?, ?, ?, ?, ?)
                            """, (msg_id, 200, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], url))
                elif msg['msgType'] == 2:  # 语音消息
                    my_logger.debug('语音消息')
                    bodys = json.loads(msg['bodys'])
                    if 'url' in bodys.keys():
                        url = bodys['url']
                        if global_config.USING_COOLQ_PRO is True:
                            file_name = sound_downloda(url)
                            notic_message = ('【%s语音】[%s]: \n' % (extInfo['senderName'], msg['msgTimeStr']))
                            QQHandler.send_to_groups(self.member_room_msg_groups, notic_message)
                            sound_message = ('[CQ:record,file=%s]' % file_name)
                            QQHandler.send_to_groups(self.member_room_msg_groups, sound_message)
                        else:
                            message = message + ('【语音】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url))
                        cursor.execute("""
                                INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content) VALUES
                                                           (?, ?, ?, ?, ?, ?)
                             """, (msg_id, 201, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], url))
                elif msg['msgType'] == 3:  # 小视频
                    my_logger.debug('房间小视频')
                    bodys = json.loads(msg['bodys'])
                    if 'url' in bodys.keys():
                        url = bodys['url']
                        message = message + ('【小视频】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], url))
                        cursor.execute("""
                             INSERT INTO 'room_message' (message_id, type, user_id, user_name, message_time, content) VALUES
                                            (?, ?, ?, ?, ?, ?)
                            """, (msg_id, 202, extInfo['senderId'], extInfo['senderName'], msg['msgTimeStr'], url))

            if message and len(self.member_room_msg_groups) > 0:
                message = message + ('【消息来源】: %s房间' % (source_room_name))
                QQHandler.send_to_groups(self.member_room_msg_groups, message)
                # self.get_member_room_msg_lite()
                my_logger.info('message: {}'.format(message))
            my_logger.debug('成员消息队列: {}'.format(len(self.member_room_msg_ids)))
        except Exception as e:
            my_logger.error(e)
        finally:
            pass
            self.conn.commit()
            cursor.close()

    def parse_idol_flip(self, question_id, answer_id, source):
        url = 'https://ppayqa.48.cn/idolanswersystem/api/idolanswer/v1/question_answer/detail'
        params = {
            "questionId": question_id, "answerId": answer_id, "idolFlipSource": source
        }

        res = self.session.post(url, data=json.dumps(params), headers=self.idol_flip_header_args()).json()
        return res['content']['answer']

    def get_member_room_comment(self, room_id, limit=20):
        """
        获取成员房间的粉丝评论
        :param limit:
        :param room_id: 房间id
        :return:
        """

        if not self.is_login:
            my_logger.error('尚未登录')
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
            my_logger.error('获取房间评论失败')
            my_logger.error(e)
        return r.text

    def parse_member_live(self, response, living_member_id_list, init=False):
        """
        对直播列表进行处理，找到正在直播的指定成员
        :param member_id:
        :param response:
        :return:
        """
        try:
            rsp_json = json.loads(response)
        except Exception as e:
            my_logger.error('获取直播接口不报错，但拿不到数据')
            my_logger.error(e)
            return
        # 当前没有人在直播
        if 'liveList' not in rsp_json['content'].keys():
            # print 'no live'
            my_logger.debug('当前没有人在直播')
            return
        live_list = rsp_json['content']["liveList"]
        my_logger.debug('当前正在直播的人数: {}'.format(len(live_list)))
        # print '当前正在直播的人数: %d' % len(live_list)
        msg = ''
        # my_logger.debug('直播ID列表: %s', ','.join(self.member_live_ids))
        for live in live_list:
            live_id = live['liveId']
            # my_logger.debug(live.keys())
            # print '直播人: %s' % live['memberId']
            # my_logger.debug('直播人(response): %s, 类型: %s', live['memberId'], type(live['memberId']))
            # my_logger.debug('member_id(参数): %s, 类型: %s', member_id, type(member_id))
            my_logger.debug('memberId {} is in live: {}, live_id: {}'.format(live['memberId'], live['title'], live_id))
            my_logger.debug('stream path: {}'.format(live['streamPath']))
            # my_logger.debug('member_live_ids list: %s', ','.join(self.member_live_ids))
            # my_logger.debug('live_id is in member_live_ids: %s', str(live_id in self.member_live_ids))
            
            for member_id in living_member_id_list:
                if live['memberId'] == int(member_id) and live_id not in self.member_live_ids:
                    my_logger.debug('[被监控成员正在直播]member_id: {}, live_id: {}'.format(member_id, live_id))
                    start_time = util.convert_timestamp_to_timestr(live['startTime'])
                    stream_path = live['streamPath']  # 流地址
                    name = live['title'].split('的')[0]
                    sub_title = live['subTitle']  # 直播名称
                    live_type = live['liveType']
                    url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' % live_id
                    if live_type == 1:  # 露脸直播
                        msg += '%s开露脸直播: %s\n开始时间: %s\n直播地址流: %s\n\n' % (name, sub_title, start_time, stream_path)
                    elif live_type == 2:  # 电台直播
                        msg += '%s开电台直播: %s\n开始时间: %s\n直播地址流: %s\n\n' % (name, sub_title, start_time, stream_path)
                    self.member_live_ids.append(live_id)

                    # 录制直播
                    # name = '%s_%s' % (member_id, live['startTime'])
                    # # self.download.setName(name)
                    # self.live_urls.put(name)
                    # self.live_urls.put(stream_path)

        my_logger.debug(msg)
        if msg and len(self.member_live_groups) > 0 and init is False:
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
            my_logger.debug('当前没有人在直播')
            QQHandler.send_to_groups_by_order(self.member_live_groups, '当前没有人在直播~')
            return
        live_list = rsp_json['content']["liveList"]
        my_logger.debug('当前正在直播的人数: {}'.format(len(live_list)))
        # print '当前正在直播的人数: %d' % len(live_list)
        msg = ''
        # my_logger.debug('直播ID列表: %s', ','.join(self.member_live_ids))
        for live in live_list:
            live_id = live['liveId']
            # my_logger.debug(live.keys())
            # print '直播人: %s' % live['memberId']
            # my_logger.debug('直播人(response): %s, 类型: %s', live['memberId'], type(live['memberId']))
            # my_logger.debug('member_id(参数): %s, 类型: %s', member_id, type(member_id))
            my_logger.debug('memberId {} is in live: {}, live_id: {}'.format(live['memberId'], live['title'], live_id))
            my_logger.debug('stream path: {}'.format(live['streamPath']))
            # my_logger.debug('member_live_ids list: %s', ','.join(self.member_live_ids))
            # my_logger.debug('live_id is in member_live_ids: %s', str(live_id in self.member_live_ids))
            
            for member_id in living_member_id_list:
                if live['memberId'] == int(member_id):
                    my_logger.debug('[被监控成员正在直播]member_id: {}, live_id: {}'.format(member_id, live_id))
                    start_time = util.convert_timestamp_to_timestr(live['startTime'])
                    stream_path = live['streamPath']  # 流地址
                    name = live['title'].split('的')[0]
                    sub_title = live['subTitle']  # 直播名称
                    live_type = live['liveType']
                    url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' % live_id
                    if live_type == 1:  # 露脸直播
                        msg += '%s露脸直播: %s\n开始时间: %s\n直播地址流: %s\n\n' % (name, sub_title, start_time, stream_path)
                    elif live_type == 2:  # 电台直播
                        msg += '%s电台直播: %s\n开始时间: %s\n直播地址流: %s\n\n' % (name, sub_title, start_time, stream_path)

                    # 录制直播
                    # name = '%s_%s' % (member_id, live['startTime'])
                    # # self.download.setName(name)
                    # self.live_urls.put(name)
                    # self.live_urls.put(stream_path)

        my_logger.debug(msg)
        if msg and len(self.member_live_groups) > 0:
            msg = '当前直播:\n' + msg
            QQHandler.send_to_groups_by_order(self.member_live_groups, msg)
        else:
            QQHandler.send_to_groups_by_order(self.member_live_groups, '当前没有人在直播~')

    def idol_flip_header_args(self):
        """
        构造收费翻牌请求头信息
        :return:
        """
        my_logger.debug('token: %s', self.token)
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': global_config.IMEI,
            'token': self.token,
            'version': global_config.POCKET48_VERSION,
            'Content-Type': 'application/json;charset=utf-8',
            'Host': 'ppayqa.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        return header

    def login_header_args(self):
        """
        构造登录请求头信息
        :return:
        """
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': global_config.IMEI,
            'token': '0',
            'version': global_config.POCKET48_VERSION,
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
            'IMEI': global_config.IMEI,
            'token': self.token,
            'version': global_config.POCKET48_VERSION,
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
            'IMEI': global_config.IMEI,
            'token': self.token,
            'version': global_config.POCKET48_VERSION,
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
        for s in schedules:
            perform_time = int(s['pretime'])
            diff = perform_time - time.time()
            if 0 < diff <= 15 * 60:
                live_link = self.live_url_bilibili_or_migu(s)
                live_msg = '直播传送门: %s' % live_link
                notify_str += '%s\n %s\n 时间:%s\n %s\n' % (
                global_config.PERFORMANCE_NOTIFY, s['title'], s['addtime'], live_msg)
        my_logger.info('notify str: {}'.format(notify_str))
        if notify_str:
                QQHandler.send_to_groups(self.member_room_msg_groups, notify_str)

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
                url = 'http://music.migu.cn/v2/live/490'
            elif 'NIII队' in title:
                url = '地址暂时不知道'
            elif '预备生' in title:
                url = '地址暂时不知道'
            url = '（咪咕）' + url
            return url
        else:
            url = global_config.LIVE_LINK
            return url

    def get_current_ticket_info_msg(self, schedules):
        '''
        自动回复票务信息
        最近公演：msg
        '''
        schedules_copy = schedules[:]
        schedules_copy.reverse()
        msg = '票务:\n'
        now = time.time()
        for s in schedules_copy:
            msg += '%s\n时间:%s\n\n' % (s['special'], s['addtime'])
        QQHandler.send_to_groups(self.auto_reply_groups, msg)

    def get_tuling_ai(self, id, info):
        api_key = '750ee100645a4707bf1bb55efc4032ed'
        url = 'http://www.tuling123.com/openapi/api'
        post_data = {
            'key': api_key,
            'info': info,
            'userid': id
        }
        try:
            content = requests.post(url, post_data)
            msg = ''
            text = ''
            if (content):
                res_obj = content.json()
                type_code = res_obj['code']
                text = res_obj['text']
                if type_code == 100000:
                    msg = text
                elif type_code == 200000:
                    msg = '%s\n%s' % (text, res_obj['url'])
                elif type_code == 302000:
                    news_list = res_obj['list']
                    for news in news_list:
                        news_msg = '%s\n%s\n\n' % (news['article'], news['detailurl'])
                        msg += news_msg
                    msg += text
                elif type_code == 308000:
                    food_list = res_obj['list']
                    for food in food_list:
                        food_msg = '%s\n%s\n\n' % (food['name'], food['detailurl'])
                        msg += food_msg
                else:
                    msg = text
                return msg
        except Exception as e:
            my_logger.error('请求图灵机器人接口发生错误')
            print (e)
            return '图灵机器人接口出错啦'

    def get_bilibili_video_list(self):
        url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=27363163&pagesize=10&tid=0&page=1&keyword=&order=pubdate'
        request = urllib.request.Request(url)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        try:
            response = urllib.request.urlopen(request)
            content = response.read()
            if (content):
                res_obj = json.loads(content)
                return res_obj['data']['vlist']
        except Exception as e:
            my_logger.error('请求b站接口出错')
            print (e)
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
        my_logger.debug(msg)
        if msg and len(self.member_room_msg_groups) > 0:
            msg = 'b站官方账号更新:\n' + msg
            QQHandler.send_to_groups(self.member_room_msg_groups, msg)

    def deactive_member_by_name(self, name):
        pin_yin = util.get_member_pinyin(name)
        msg = ''
        stop_loop = False
        if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) > 0:
            for index, item in enumerate(global_config.ACTIVE_MEMBER_ROOM_ID_LIST):
                if pin_yin == item[0]:
                    pop = global_config.ACTIVE_MEMBER_ROOM_ID_LIST.pop(index)
                    global_config.DEACTIVE_MEMBER_ROOM_ID_LIST.append(pop)
                    msg = '已屏蔽%s房间' % (name)
                    QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                    break
                else:
                    if stop_loop is True:
                        break
                    for item in global_config.DEACTIVE_MEMBER_ROOM_ID_LIST:
                        if pin_yin == item[0]:
                            msg = '%s已在小黑屋内,无需再屏蔽' % (name)
                            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                            stop_loop = True
                            break
        else:
            for item in global_config.DEACTIVE_MEMBER_ROOM_ID_LIST:
                if pin_yin == item[0]:
                    msg = '%s已在小黑屋内,无需再屏蔽' % (name)
                    QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                    break
        if msg == '':
            msg = '%s房间不在监控范围内' % (name)
            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)


    def active_member_by_name(self, name):
        pin_yin = util.get_member_pinyin(name)
        msg = ''
        stop_loop = False
        if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
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
                    msg = '已开启%s房间' % (name)
                    QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                    break
                else:
                    if stop_loop is True:
                        break
                    for active_item in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
                        if pin_yin == active_item[0]:
                            msg = '%s已在小白屋内,无需再开启' % (name)
                            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                            stop_loop = True
                            break
        else:
            for active_item in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
                if pin_yin == active_item[0]:
                    msg = '%s已在小白屋内,无需再开启' % (name)
                    QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)
                    break
        if msg == '':
            msg = '%s房间不在监控范围内' % (name)
            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, msg)

    # def get_lucky_members_info(self):
    #     url = 'http://h5.snh48.com/resource/jsonp/members.php?gid=30&callback=get_members_success'
    #     request = urllib.request.Request(url)
    #     request.add_header('Content-Type', 'application/json; charset=UTF-8')
    #     try:
    #         response = urllib.request.urlopen(request)
    #         content = response.read()
    #         if (content):
    #             res_str = util.parse_jsonp(content)
    #             res_obj = json.loads(res_str)
    #             items = res_obj['rows']
    #             return items
                
    #     except Exception as e:
    #         my_logger.error('请求接口出错')
    #         print (e)
    #         return

    def today_lucky_member(self, user_id):
        msg = ''
        obj = None
        if len(self.user_id_member_info_list) > 0:
            for item in self.user_id_member_info_list:
                if item['user_id'] == user_id:
                    obj = item
                    break
        if obj is None:
            member_info = util.random_str(global_config.LUCKY_MEMBERS_INFO)
            member_info['user_id'] = user_id
            member_info['fate_degree'] = util.random_int(70, 100)
            member_info['rebirth'] = 0
            obj = member_info
            self.user_id_member_info_list.append(member_info)
        if obj['catch_phase']:
            msg = '\n今日有缘成员:%s (%s)\n%s\n契合度: %s' % (obj['name'], obj['nicknames'], obj['catch_phase'], obj['fate_degree'])
        else:
            msg = '\n今日有缘成员:%s (%s)\n契合度: %s' % (obj['name'], obj['nicknames'], obj['fate_degree'])
        return msg

    def rebirth(self, user_id, limit=1):
        msg = ''
        if len(self.user_id_member_info_list) > 0:
            for index, item in enumerate(self.user_id_member_info_list):
                if item['user_id'] == user_id:
                    if item['rebirth'] < limit:
                        member_info = util.random_str(global_config.LUCKY_MEMBERS_INFO)
                        member_info['user_id'] = user_id
                        member_info['fate_degree'] = util.random_int(70, 100)
                        member_info['rebirth'] = item['rebirth'] + 1
                        self.user_id_member_info_list[index] = member_info
                        if member_info['catch_phase']:
                            msg = '恭喜你重生成功!\n重生成员: %s (%s)\n%s\n契合度: %s' % (member_info['name'], member_info['nicknames'], member_info['catch_phase'], member_info['fate_degree'])
                        else:
                            msg = '恭喜你重生成功!\n重生成员: %s (%s)\n契合度: %s' % (member_info['name'], member_info['nicknames'], member_info['fate_degree'])
                    else:
                        msg = '重生失败,你今天重生次数已达上限(每天1次)'
                    break
        if msg == '':
            msg = '重生失败,请先进行\'-今日有缘\''
        return msg

    def get_some_room_msg(self,name,num):
        pin_yin = util.get_member_pinyin(name)
        all_member_room_ids = global_config.ACTIVE_MEMBER_ROOM_ID_LIST + global_config.DEACTIVE_MEMBER_ROOM_ID_LIST
        target_room_id = ''
        for member_room_id in all_member_room_ids:
            if pin_yin == member_room_id[0]:
                target_room_id = member_room_id[1]
                break
        r = self.get_member_room_msg(target_room_id, num)
        self.parse_room_msg(r, name, True)

    def get_page(self):
        id = global_config.LAST_TICKET_INFO_ID
        url = 'https://shop.48.cn/Tickets/Item/%s' % id
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            html =str(response.read(),'utf-8')
            if (html):
                return html
        except Exception as e:
            my_logger.error('请求票务接口出错')
            print (e)
            return

    def parse_page (self, content):
        if ('广州市天河区林和西路161号中泰国际广场3F' in content):
            p = pq(content)
            detail = p('div').filter('.lb_1').children('p').text()
            detail2 = '直播\n'.join('\n'.join(detail.split('  ')).split('直播 '))
            return detail2
        else:
            return ''

    def parse_page_now (self, content):
        # id = global_config.LAST_TICKET_INFO_ID
        # url = 'https://shop.48.cn/Tickets/Item/%s' % id
        if ('广州市天河区林和西路161号中泰国际广场3F' in content):
            p = pq(content)
            detail = p('div').filter('.lb_1').children('p').text()
            detail2 = '直播\n'.join('\n'.join(detail.split('  ')).split('直播 '))
            detail2 += '票务地址:https://shop.48.cn/tickets/item/%s' % global_config.LAST_TICKET_INFO_ID
            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, detail2)
        else:
            QQHandler.send_to_groups_by_order(self.member_room_msg_groups, '尚未有最新票务')







if __name__ == '__main__':
    pass
