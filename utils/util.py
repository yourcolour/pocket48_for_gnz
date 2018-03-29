# -*- coding: utf-8 -*-
import time
import random
import re
import urllib
import hashlib
import requests
import json
import sys
import datetime
import os
from utils import global_config
from urllib.request import urlretrieve

member_list = [
    # Team G
    {
    'pin_yin':'chenke',
    'name':'陈珂',
    'nicknames': '陈王可;CK',
    'catch_phase': '多C多健康，每天都来一份~~ 活力维C！'
    },
    {
    'pin_yin':'chenyuqi',
    'name':'陈雨琪',
    'nicknames': '团子',
    'catch_phase': '一手把你抱走的~~ 暴走团子！'
    },
    {
    'pin_yin':'gaoyuanjing',
    'name':'高源婧',
    'nicknames': '大盘鸡;小狐狸;大魔王;MC Queen',
    'catch_phase': '我不管,我就是~~ 大魔王!'
    },
    {
    'pin_yin':'linjiapei',
    'name':'林嘉佩',
    'nicknames': '塔塔',
    'catch_phase': '林家小妹在哪里~~ 在这里！'
    },
    {
    'pin_yin':'liqinjie',
    'name':'李沁洁',
    'nicknames': '色管;kiko',
    'catch_phase': 'Kiko Kiko~~ 笑眯眯'
    },
    {
    'pin_yin':'xieleilei',
    'name':'谢蕾蕾',
    'nicknames': '谢蠢蠢;谢小埋',
    'catch_phase': '谢谢你，谢谢大家，还有别忘了~~ 谢谢蕾蕾！'
    },
    {
    'pin_yin':'yangqingying',
    'name':'阳青颖',
    'nicknames': '辣条',
    'catch_phase': '【唱】夏天夏天悄悄过去 ~~【唱】留下小青颖'
    },
    {
    'pin_yin':'zengaijia',
    'name':'曾艾佳',
    'nicknames': '艾佳',
    'catch_phase': '爱家爱生活，把爱~~ 带回家.'
    },
    # {
    # 'pin_yin':'zhangkaiqi',
    # 'name':'张凯祺',
    # 'nicknames': '彪彪;彪sir',
    # 'catch_phase': '你有权保持沉默，但你所讲嘅一切将会成为呈堂证供，Understand? Yes, sir!'
    # },
    {
    'pin_yin':'luohanyue',
    'name':'罗寒月',
    'nicknames': '罗老师;中泰rap王;MC King',
    'catch_phase': '寒月服不服？ 不服！'
    },
    {
    'pin_yin':'zhangqiongyu',
    'name':'张琼予',
    'nicknames': '小腮帮;soso',
    'catch_phase': '湿湿碎,麻麻地,唔该唔该~~ 冇问题'
    },
    {
    'pin_yin':'huanglirong',
    'name':'黄黎蓉',
    'nicknames': '莲蓉蛋',
    'catch_phase': '咕噜咕噜，滚来一颗~~ 莲蓉蛋'
    },
    {
    'pin_yin':'chenjiaying',
    'name':'陈佳莹',
    'nicknames': '小家伙',
    'catch_phase': '你们要守护的有亲情、友情，还有~~ 陈！佳！莹！'
    },
    {
    'pin_yin':'chenjunhong',
    'name':'陈俊宏',
    'nicknames': '夜喵',
    'catch_phase': '白喵、橘喵、大灰喵 队友：我最喜欢~~ 小夜喵'
    },
    {
    'pin_yin':'fangxiaoyu',
    'name':'方晓瑜',
    'nicknames': '小鱼',
    'catch_phase': '放长线,钓~~ 小鱼'
    },
    {
    'pin_yin':'liangke',
    'name':'梁可',
    'nicknames': '可可',
    'catch_phase': '炎热（凉爽）的夏天（秋天）需要一杯冰凉(暖暖)的~~ 可可！'
    },
    {
    'pin_yin':'zhuyixin',
    'name':'朱怡欣',
    'nicknames': 'ggb',
    'catch_phase': '在童话里做英雄的是~~ GG Bond!'
    },

    # Team NIII
    {
    'pin_yin':'chenhuijing',
    'name':'陈慧婧',
    'nicknames': '陈老板',
    'catch_phase': '开启魔镜的咒语是~~ 封！印！解！除！'
    },
    {
    'pin_yin':'chennanxi',
    'name':'陈楠茜',
    'nicknames': '北哥',
    'catch_phase': '茉莉冻奶昔，最爱~~ 陈！楠！茜！'
    },
    {
    'pin_yin':'chenxinyu',
    'name':'陈欣妤',
    'nicknames': '金鱼',
    'catch_phase': '金鱼的记忆只有7秒，而你们7秒的记忆里全部都是~~ 陈！欣！妤！'
    },
    {
    'pin_yin':'fengjiaxi',
    'name':'冯嘉希',
    'nicknames': '巴扎嘿;冯噶嘿;希仔',
    'catch_phase': '世界五彩 你选希仔！'
    },
    {
    'pin_yin':'hongjingwen',
    'name':'洪静雯',
    'nicknames': '奶盖',
    'catch_phase': '苦苦的茶记得要配上甜甜的~~ 奶！盖（Gay）！'
    },
    {
    'pin_yin':'liulifei',
    'name':'刘力菲',
    'nicknames': '藤藤菜;菲菲;中泰小仙女',
    'catch_phase': '吃了藤藤菜，就是~~ 长得帅'
    },
    {
    'pin_yin':'liuqianqian',
    'name':'刘倩倩',
    'nicknames': '677',
    'catch_phase': '6767~~ 677！'
    },
    {
    'pin_yin':'lujing',
    'name':'卢静',
    'nicknames': '闹闹',
    'catch_phase': '嘘，别闹~~ 我想静静'
    },
    {
    'pin_yin':'sunxing',
    'name':'孙馨',
    'nicknames': '小老虎',
    'catch_phase': '天王盖地虎！队友：孙馨小老虎!\n宝塔镇河妖！队友：孙馨小蛮（没有）腰！'
    },
    {
    'pin_yin':'tanglijia',
    'name':'唐莉佳',
    'nicknames': '学姐;liga',
    'catch_phase': ''
    },
    {
    'pin_yin':'xianshennan',
    'name':'冼燊楠',
    'nicknames': '兔子',
    'catch_phase': 'Jump! Jump! 跳出一只~~ Usagi!'
    },
    {
    'pin_yin':'xiaowenling',
    'name':'肖文铃',
    'nicknames': '小铃铛',
    'catch_phase': '叮叮当当~~ 小铃铛！'
    },
    {
    'pin_yin':'xiongxinyao',
    'name':'熊心瑶',
    'nicknames': '苞谷',
    'catch_phase': '你心里的遥控器~~ SwitchOn！'
    },
    {
    'pin_yin':'zhengdanni',
    'name':'郑丹妮',
    'nicknames': '蒸蛋;皮皮蛋',
    'catch_phase': '肚子饿了要吃饭，酒窝配上~~ 蒸！蛋！'
    },
    {
    'pin_yin':'zuojiaxin',
    'name':'左嘉欣',
    'nicknames': '扎心',
    'catch_phase': '加班加点也要~~ 加薪！'
    },
    {
    'pin_yin':'zuojingyuan',
    'name':'左婧媛',
    'nicknames': '左左;金毛',
    'catch_phase': '立正！向左看~~ 齐！'
    },
    # {
    # 'pin_yin':'liyihong',
    # 'name':'李伊虹',
    # 'nicknames': '橙妹',
    # 'catch_phase': '初次见面,请说~~你好'
    # },
    {
    'pin_yin':'gaoxueyi',
    'name':'高雪逸',
    'nicknames': '小高;喷嚏;果核',
    'catch_phase': '白雪皑皑，雪逸不矮'
    },
    {
    'pin_yin':'tangshiyi',
    'name':'唐诗怡',
    'nicknames': '糖宝',
    'catch_phase': '糖儿甜蜜蜜，蜜糖甜甜~~ 有诗意'
    },
    {
    'pin_yin':'xieailin',
    'name':'谢艾琳',
    'nicknames': '420',
    'catch_phase': ''
    },
    {
    'pin_yin':'zhengyue',
    'name':'郑悦',
    'nicknames': '小悦悦',
    'catch_phase': '想给你们越来越多~~ 正能量'
    },
    # Team Z
    {
    'pin_yin':'chenguijun',
    'name':'陈桂君',
    'nicknames': '阿邪;君桂妹',
    'catch_phase': 'Bling,Bling, 陈桂君，阿邪阿邪~~ 天真无邪！'
    },
    {
    'pin_yin':'chenziying',
    'name':'陈梓荧',
    'nicknames': 'pica',
    'catch_phase': 'Shiny~ Beauty! Picapica~ P!'
    },
    {
    'pin_yin':'dailing',
    'name':'代玲',
    'nicknames': '呆呆',
    'catch_phase': '呆呆地住在你心里，想要成为你的~~ Darling!'
    },
    {
    'pin_yin':'duqiulin',
    'name':'杜秋霖',
    'nicknames': '小蚯蚓',
    'catch_phase': '【唱】在树的那边，窟的里边，有一只~~ 【唱】小！蚯！蚓！'
    },
    {
    'pin_yin':'liujiayi',
    'name':'刘嘉怡',
    'nicknames': '七妹',
    'catch_phase': '欢迎来到非常~~ 6+1！'
    },
    {
    'pin_yin':'longyirui',
    'name':'龙亦瑞',
    'nicknames': '短腿柯基;龙哥哥;瑞子',
    'catch_phase': '好吃不如饺子，可爱不如~~ 瑞子！'
    },
    {
    'pin_yin':'nongyanping',
    'name':'农燕萍',
    'nicknames': '小奶瓶',
    'catch_phase': '萍水相逢遇见你，浓情蜜意~~ 小奶瓶！'
    },
    {
    'pin_yin':'wangcuifei',
    'name':'王翠菲',
    'nicknames': '吧宠;小加菲',
    'catch_phase': '我不是加菲猫，我是你们的~~ 小加菲！'
    },
    {
    'pin_yin':'wangsiyue',
    'name':'王偲越',
    'nicknames': '小四月',
    'catch_phase': '你是那人间四月天，我是你们的~~ 小！四！月！'
    },
    {
    'pin_yin':'wangzixin',
    'name':'王秭歆',
    'nicknames': '小王子',
    'catch_phase': '来自B612星球的是~~ 小王子'
    },
    {
    'pin_yin':'yangkelu',
    'name':'杨可璐',
    'nicknames': '羊驼',
    'catch_phase': ''
    },
    {
    'pin_yin':'yangyuanyuan',
    'name':'杨媛媛',
    'nicknames': '杨导;杨⭕⭕',
    'catch_phase': '圈圈⭕⭕圈圈,圈圈⭕⭕~~ 圈圈!'
    },
    {
    'pin_yin':'yushanshan',
    'name':'于珊珊',
    'nicknames': '33',
    'catch_phase': 'Yui, Yui-er, Yui-est，我是化身终极形态的~~ 珊！珊！'
    },
    # {
    # 'pin_yin':'zhaoxinyu',
    # 'name':'赵欣雨',
    # 'nicknames': 'candy',
    # 'catch_phase': '爱吃棉花糖（炸药）的小可爱就是~~ Candy！'
    # },
    {
    'pin_yin':'laijunyi',
    'name':'赖俊亦',
    'nicknames': '小赖',
    'catch_phase': '我是赖在你心里的~~ 小赖皮'
    },
    {
    'pin_yin':'zhangqiuyi',
    'name':'张秋怡',
    'nicknames': '秋衣',
    'catch_phase': '秋天到了，最不可缺少的是秋裤，你们最不可缺少的是~~ 秋衣！'
    },
    {
    'pin_yin':'liangwanlin',
    'name':'梁婉琳',
    'nicknames': '晚晚;言言子',
    'catch_phase': '森林中住着小精灵,你们的心中住着~~ 梁婉琳!'
    },
    {
    'pin_yin':'biruishan',
    'name':'毕瑞珊',
    'nicknames': '老毕;小毕',
    'catch_phase': ''
    },
    {
    'pin_yin':'hemengyao',
    'name':'何梦瑶',
    'nicknames': '摇一摇',
    'catch_phase': '梦里花落知多少,shake your body~~ 摇一摇'
    },
    {
    'pin_yin':'yuzhiyuan',
    'name':'余芷媛',
    'nicknames': '否否',
    'catch_phase': '送你一份礼物,是一个可爱的~~ 芷媛'
    },

    # 预备生
    {
    'pin_yin':'chengziyu',
    'name':'程子钰',
    'nicknames': '鱼崽',
    'catch_phase': 'Pilipala Pilipala, 天上下的是什么雨？~~ 橙子雨'
    },
    {
    'pin_yin':'denghuien',
    'name':'邓惠恩',
    'nicknames': '小凳子;酥饼',
    'catch_phase': '温暖的家里有桌子、椅子，还有~~小凳子'
    },
    {
    'pin_yin':'fubingbing',
    'name':'符冰冰',
    'nicknames': '冰冰;Bubu',
    'catch_phase': '你幸不幸福？~~ 幸福'
    },
    {
    'pin_yin':'huangchuyin',
    'name':'黄楚茵',
    'nicknames': '奶黄包;央央',
    'catch_phase': '储藏你们的声音,我就是~~黄楚茵'
    },
    {
    'pin_yin':'luokejia',
    'name':'罗可嘉',
    'nicknames': '小安',
    'catch_phase': '今天不想起床怎么办? 要呆在小安的~~被窝里~'
    },
    {
    'pin_yin':'linzhi',
    'name':'林芝',
    'nicknames': '木木西;007',
    'catch_phase': '7654321,我是你的~007'
    },
    {
    'pin_yin':'wangmuyuan',
    'name':'汪慕远',
    'nicknames': '小妖',
    'catch_phase': '妖皇大人现身, 快拨打~110'
    },
    {
    'pin_yin':'wuyufei',
    'name':'吴羽霏',
    'nicknames': '无语飞',
    'catch_phase': '啾~啾~无语飞,无语~~就会飞'
    },
    {
    'pin_yin':'yexiaomeng',
    'name':'叶晓梦',
    'nicknames': 'big梦',
    'catch_phase': '日有所思,夜有~~晓梦'
    },
    {
    'pin_yin':'lichenxi',
    'name':'李晨曦',
    'nicknames': '抖抖',
    'catch_phase': '黎明后照耀你们的是~~晨曦'
    },
    {
    'pin_yin':'shuxiang',
    'name':'舒湘',
    'nicknames': '湘湘',
    'catch_phase': '书声琅琅，书香门第'
    },
    {
    'pin_yin':'wangmengyuan',
    'name':'王梦媛',
    'nicknames': '妙蛙种子;沧子',
    'catch_phase': '每天晚上都要梦见你们的~~ 沧子'
    },
    {
    'pin_yin':'xujiayin',
    'name':'徐佳音',
    'nicknames': '喑爷',
    'catch_phase': '灵魂之音,愿如你心~'
    },
    {
    'pin_yin':'xiaowenjing',
    'name':'肖文静',
    'nicknames': '茶搽',
    'catch_phase': '无由持一碗，寄与爱茶人~'
    },
    {
    'pin_yin':'zhangziying',
    'name':'张紫颖',
    'nicknames': '颖妹;影子',
    'catch_phase': '在黑夜里默默守护你们的是~~ 影子'
    }

]
# 命令使用时间限制
def is_in_limit_time():
    now = datetime.datetime.now()
    lower_limit1 = now.replace(hour=0,minute=0,second=0,microsecond=0)
    upper_limit1 = now.replace(hour=9,minute=0,second=0,microsecond=0)
    if lower_limit1 <= now <= upper_limit1:
        return True
    else:
        return False

# 返回录音文件夹下, 某一关键字的文件名称列表        
def record_key_word_list(key_word_name, key_word_unique):
    top_dir = '/Users/yourcolour/coolq/data/record'
    random = '随机'
    key_word_list = []
    if os.path.exists(top_dir)==False:
        print ("not exists")
        return
    if os.path.isdir(top_dir)==False:
        print ("not a dir")
        return
    for dir_path,subpaths,files in os.walk(top_dir,False):
        for file in files:
            if key_word_name in file and key_word_unique in file:
                key_word_list.append(file)
            if key_word_name in file and random in file:
                key_word_list.append(file)
    return key_word_list

def record_time_interval():
    now = datetime.datetime.now()
    hour0 = now.replace(hour=0,minute=0,second=0,microsecond=0)
    hour1 = now.replace(hour=1,minute=0,second=0,microsecond=0)
    hour5 = now.replace(hour=5,minute=0,second=0,microsecond=0)
    hour8 = now.replace(hour=8,minute=0,second=0,microsecond=0)
    hour11 = now.replace(hour=11,minute=0,second=0,microsecond=0)
    hour13 = now.replace(hour=13,minute=0,second=0,microsecond=0)
    hour16 = now.replace(hour=16,minute=0,second=0,microsecond=0)
    hour19 = now.replace(hour=19,minute=0,second=0,microsecond=0)
    hour22 = now.replace(hour=22,minute=0,second=0,microsecond=0)
    hour_last = now.replace(hour=23,minute=59,second=59,microsecond=999)
    if hour1 < now <= hour5:
        return '半夜三点'
    if hour5 < now <= hour8:
        return '上午七点'
    if hour8 < now <= hour11:
        return '上午九点'
    if hour11 < now <= hour13:
        return '中午十二点'
    if hour13 < now <= hour16:
        return '下午三点'
    if hour16 < now <= hour19:
        return '下午六点'
    if hour19 < now <= hour22:
        return '晚上九点'
    if hour22 < now <= hour_last or hour0 < now <= hour1:
        return '半夜十二点'

def random_record(key_word_name):
    key_word_unique = record_time_interval()
    key_word_list = record_key_word_list(key_word_name, key_word_unique)
    return random_str(key_word_list)


def get_black_room_list():
    msg = ''
    if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
        for item in global_config.DEACTIVE_MEMBER_ROOM_ID_LIST:
            pin_yin = item[0]
            for name_obj in member_list:
                if pin_yin == name_obj['pin_yin']:
                    msg += '%s,' % (name_obj['name'])
                    break
        msg = '当前小黑屋 (共%s人):\n%s' % (len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST), msg)
    else:
        msg = '没有成员在小黑屋~'
    return msg

def get_white_room_list():
    msg = ''
    if len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST) > 0:
        for item in global_config.ACTIVE_MEMBER_ROOM_ID_LIST:
            pin_yin = item[0]
            for name_obj in member_list:
                if pin_yin == name_obj['pin_yin']:
                    msg += '%s,' % (name_obj['name'])
                    break
        msg = '当前小白屋（共%s人）:\n%s' % (len(global_config.ACTIVE_MEMBER_ROOM_ID_LIST), msg)
    else:
        msg = '没有成员在小白屋~'
    return msg

def get_order_name(order):
    ptn = re.compile(u'-[\u4e00-\u9fa5]{2}(.*?)房间')
    res = ptn.search(order)
    if res:
        return res.group(1)
    else:
        return ''
def get_msg_order_name_num(order):
    ptn = re.compile('-拉(\d+)条(.*?)消息')
    res = ptn.search(order)
    if res:
        return res.group(1), res.group(2)
    else:
        return '', ''
def is_num_in_limt(num, limit=20):
    if num:
        num = int(num)
        if num > limit:
            return False
        else:
            return True
    else:
        return False

def get_modian_flag(order):
    ptn = re.compile(u'-(.*?)集资')
    res = ptn.search(order)
    if res:
        return res.group(1)
    else:
        return ''


def convert_timestamp_to_timestr(timestamp):
    """
    将13位时间戳转换为字符串
    :param timestamp:
    :return:
    """
    timeArray = time.localtime(timestamp / 1000)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return time_str

def is_name_in_member_list(name):
    global member_list
    res = False
    for item in member_list:
        if item['name'] == name:
            res = True
            break
    return res



def convert_timestr_to_timestamp(time_str):
    """
    将时间字符串转换为时间戳
    :param time_str:
    :return:
    """
    timestamp = time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
    return timestamp


def random_str(strs):
    return random.choice(strs)

def random_int(lower_limit, upper_limit):
    return random.randint(lower_limit, upper_limit)


# 过滤HTML中的标签
# 将HTML中标签等信息去掉
# @param htmlstr HTML字符串.
def filter_tags(htmlstr):
    # 先过滤CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_br = re.compile('<br\s*?/?>')  # 处理换行
    re_h = re.compile('</?\w+[^>]*>')  # HTML标签
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释
    s = re_cdata.sub('', htmlstr)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    # 去掉多余的空行
    blank_line = re.compile('\n+')
    s = blank_line.sub('\n', s)
    s = replaceCharEntity(s)  # 替换实体
    return s


# 替换常用HTML字符实体.
# 使用正常的字符替换HTML中特殊的字符实体.
# 你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
# @param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                     'lt': '<', '60': '<',
                     'gt': '>', '62': '>',
                     'amp': '&', '38': '&',
                     'quot': '"', '34': '"',
                     }

    re_charEntity = re.compile(r'&#?(?P<name>\w+);')
    sz = re_charEntity.search(htmlstr)
    while sz:
        entity = sz.group()  # entity全称，如&gt;
        key = sz.group('name')  # 去除&;后entity,如&gt;为gt
        try:
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charEntity.sub('', htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
    return htmlstr


def replace(s, re_exp, repl_string):
    return re_exp.sub(repl_string, s)


def make_signature(post_fields):
    """
    生成调用微打赏接口所需的签名

    PHP的例子：
        $post_fields = $_POST;
        ksort($post_fields);
        $md5_string = http_build_query($post_fields);
        $sign = substr(md5($md5_string), 5, 16);

    :param post_fields: post请求的参数
    :return:
    """
    post_fields_sorted = ksort(post_fields)
    md5_string = urllib.urlencode(post_fields_sorted) + '&p=das41aq6'
    print (md5_string)
    sign = hashlib.md5(md5_string).hexdigest()[5:21]
    print (sign)
    return sign

def list_to_utf8(list):
    s = str(list).replace('u\'','\'')
    return s.decode("unicode-escape")

def ksort(d):
    return [(k, d[k]) for k in sorted(d.keys())]

def get_member_nickname(name, default_name = ''):
    nicknames = ''
    global member_list
    for item in member_list:
        if item['name'] in name:
            nicknames = item['nicknames']
            break
    if nicknames == '':
        nicknames = default_name
    nickname_list = nicknames.split(';')
    nickname = random_str(nickname_list)
    return nickname

def get_member_pinyin(name):
    pin_yin = ''
    global member_list
    for item in member_list:
        if item['name'] in name:
            pin_yin = item['pin_yin']
            break
    return pin_yin

def parse_jsonp(jsonp_str):
    jsonp_str_decode = jsonp_str.decode('utf-8')
    try:
        return re.search('^[^(]*?\((.*)\)[^)]*$', jsonp_str_decode).group(1)
    except:
        raise ValueError('Invalid JSONP')




 
