# -*- coding: utf-8 -*-
import time
import random
import re
import urllib
import hashlib
import requests
import json
import sys
from utils import global_config

reload(sys)
sys.setdefaultencoding('utf-8')

member_list = [
    # Team G
    {
    'pin_yin':'chenke',
    'name':'陈珂',
    'nicknames': '你陈大哥'
    },
    {
    'pin_yin':'chenyuqi',
    'name':'陈雨琪',
    'nicknames': '团子'
    },
    {
    'pin_yin':'gaoyuanjing',
    'name':'高源婧',
    'nicknames': '大盘鸡;小狐狸;大魔王'
    },
    {
    'pin_yin':'linjiapei',
    'name':'林嘉佩',
    'nicknames': '塔塔'
    },
    {
    'pin_yin':'liqinjie',
    'name':'李沁洁',
    'nicknames': '色管;kiko'
    },
    {
    'pin_yin':'xieleilei',
    'name':'谢蕾蕾',
    'nicknames': '谢蠢蠢;谢小埋'
    },
    {
    'pin_yin':'yangqingying',
    'name':'阳青颖',
    'nicknames': '辣条'
    },
    {
    'pin_yin':'zengaijia',
    'name':'曾艾佳',
    'nicknames': '艾佳'
    },
    {
    'pin_yin':'zhangkaiqi',
    'name':'张凯祺',
    'nicknames': '彪彪;彪sir'
    },
    {
    'pin_yin':'luohanyue',
    'name':'罗寒月',
    'nicknames': '罗老师'
    },
    {
    'pin_yin':'zhangqiongyu',
    'name':'张琼予',
    'nicknames': '小腮帮;soso'
    },
    {
    'pin_yin':'huanglirong',
    'name':'黄黎蓉',
    'nicknames': '莲蓉蛋'
    },
    {
    'pin_yin':'chenjiaying',
    'name':'陈佳莹',
    'nicknames': '小家伙'
    },
    {
    'pin_yin':'chenjunhong',
    'name':'陈俊宏',
    'nicknames': '夜喵'
    },
    {
    'pin_yin':'chengyixin',
    'name':'程一心',
    'nicknames': '大猩猩'
    },
    {
    'pin_yin':'fangxiaoyu',
    'name':'方晓瑜',
    'nicknames': '小鱼'
    },
    {
    'pin_yin':'liangke',
    'name':'梁可',
    'nicknames': '可可'
    },
    {
    'pin_yin':'zhuyixin',
    'name':'朱怡欣',
    'nicknames': 'ggb'
    },

    # Team NIII
    {
    'pin_yin':'chenhuijing',
    'name':'陈慧婧',
    'nicknames': '陈老板'
    },
    {
    'pin_yin':'chennanxi',
    'name':'陈楠茜',
    'nicknames': '北哥'
    },
    {
    'pin_yin':'chenxinyu',
    'name':'陈欣妤',
    'nicknames': '金鱼'
    },
    {
    'pin_yin':'fengjiaxi',
    'name':'冯嘉希',
    'nicknames': '巴扎嘿;冯噶嘿'
    },
    {
    'pin_yin':'hongjingwen',
    'name':'洪静雯',
    'nicknames': '奶盖'
    },
    {
    'pin_yin':'liulifei',
    'name':'刘力菲',
    'nicknames': '藤藤菜;菲菲'
    },
    {
    'pin_yin':'liuqianqian',
    'name':'刘倩倩',
    'nicknames': '677'
    },
    {
    'pin_yin':'lujing',
    'name':'卢静',
    'nicknames': '闹闹;吉娃娃'
    },
    {
    'pin_yin':'sunxing',
    'name':'孙馨',
    'nicknames': '小老虎'
    },
    {
    'pin_yin':'tanglijia',
    'name':'唐莉佳',
    'nicknames': '学姐;liga'
    },
    {
    'pin_yin':'xianshennan',
    'name':'冼燊楠',
    'nicknames': '兔子'
    },
    {
    'pin_yin':'xiaowenling',
    'name':'肖文铃',
    'nicknames': '小铃铛'
    },
    {
    'pin_yin':'xiongxinyao',
    'name':'熊心瑶',
    'nicknames': '苞谷'
    },
    {
    'pin_yin':'zhengdanni',
    'name':'郑丹妮',
    'nicknames': '蒸蛋;皮皮蛋'
    },
    {
    'pin_yin':'zuojiaxin',
    'name':'左嘉欣',
    'nicknames': '扎心'
    },
    {
    'pin_yin':'zuojingyuan',
    'name':'左婧媛',
    'nicknames': '左左;金毛'
    },
    {
    'pin_yin':'liyihong',
    'name':'李伊虹',
    'nicknames': '橙妹'
    },
    {
    'pin_yin':'gaoxueyi',
    'name':'高雪逸',
    'nicknames': '小高'
    },
    {
    'pin_yin':'tangshiyi',
    'name':'唐诗怡',
    'nicknames': '糖宝'
    },
    {
    'pin_yin':'xieailin',
    'name':'谢艾琳',
    'nicknames': '420'
    },
    {
    'pin_yin':'zhengyue',
    'name':'郑悦',
    'nicknames': '悦悦'
    },
    # Team Z
    {
    'pin_yin':'chenguijun',
    'name':'陈桂君',
    'nicknames': '村花;君桂妹'
    },
    {
    'pin_yin':'chenziying',
    'name':'陈梓荧',
    'nicknames': 'pica'
    },
    {
    'pin_yin':'dailing',
    'name':'代玲',
    'nicknames': '呆呆'
    },
    {
    'pin_yin':'duqiulin',
    'name':'杜秋霖',
    'nicknames': '小蚯蚓'
    },
    {
    'pin_yin':'liujiayi',
    'name':'刘嘉怡',
    'nicknames': '七妹'
    },
    {
    'pin_yin':'longyirui',
    'name':'龙亦瑞',
    'nicknames': '短腿柯基;龙哥哥'
    },
    {
    'pin_yin':'nongyanping',
    'name':'农燕萍',
    'nicknames': '小奶瓶'
    },
    {
    'pin_yin':'wangcuifei',
    'name':'王翠菲',
    'nicknames': '吧宠;小加菲'
    },
    {
    'pin_yin':'wangjiongyi',
    'name':'王炯义',
    'nicknames': '二哈'
    },
    {
    'pin_yin':'wangsiyue',
    'name':'王偲越',
    'nicknames': '小四月'
    },
    {
    'pin_yin':'wangzixin',
    'name':'王秭歆',
    'nicknames': '来自B16星球的;小王子'
    },
    {
    'pin_yin':'yangkelu',
    'name':'杨可璐',
    'nicknames': '羊驼'
    },
    {
    'pin_yin':'yangyuanyuan',
    'name':'杨媛媛',
    'nicknames': '杨导'
    },
    {
    'pin_yin':'yushanshan',
    'name':'于珊珊',
    'nicknames': '33'
    },
    {
    'pin_yin':'zhaoxinyu',
    'name':'赵欣雨',
    'nicknames': 'candy'
    },
    {
    'pin_yin':'laijunyi',
    'name':'赖俊亦',
    'nicknames': '小赖'
    },
    {
    'pin_yin':'zhangqiuyi',
    'name':'张秋怡',
    'nicknames': '秋衣'
    },
    {
    'pin_yin':'liangwanlin',
    'name':'梁婉琳',
    'nicknames': '晚晚'
    },
    {
    'pin_yin':'biruishan',
    'name':'毕瑞珊',
    'nicknames': '老毕'
    },
    {
    'pin_yin':'hemengyao',
    'name':'何梦瑶',
    'nicknames': '摇一摇'
    },
    {
    'pin_yin':'yuzhiyuan',
    'name':'余芷媛',
    'nicknames': '三否'
    },

    # 预备生
    {
    'pin_yin':'chengziyu',
    'name':'程子钰',
    'nicknames': '程子钰'
    },
    {
    'pin_yin':'denghuien',
    'name':'邓惠恩',
    'nicknames': '邓惠恩'
    },
    {
    'pin_yin':'fubingbing',
    'name':'符冰冰',
    'nicknames': '符冰冰'
    },
    {
    'pin_yin':'huangchuyin',
    'name':'黄楚茵',
    'nicknames': '奶黄包'
    },
    {
    'pin_yin':'luokejia',
    'name':'罗可嘉',
    'nicknames': '罗可嘉'
    },
    {
    'pin_yin':'linzhi',
    'name':'林芝',
    'nicknames': '林芝'
    },
    {
    'pin_yin':'wangmuyuan',
    'name':'汪慕远',
    'nicknames': '汪慕远'
    },
    {
    'pin_yin':'wuyufei',
    'name':'吴羽霏',
    'nicknames': '吴羽霏'
    },
    {
    'pin_yin':'yexiaomeng',
    'name':'叶晓梦',
    'nicknames': '叶晓梦'
    },
    {
    'pin_yin':'lichenxi',
    'name':'李晨曦',
    'nicknames': '李晨曦'
    },
    {
    'pin_yin':'shuxiang',
    'name':'舒湘',
    'nicknames': '舒湘'
    },
    {
    'pin_yin':'wangmengyuan',
    'name':'王梦媛',
    'nicknames': '大姐头'
    },
    {
    'pin_yin':'xujiayin',
    'name':'徐佳音',
    'nicknames': '徐佳音'
    },
    {
    'pin_yin':'xiaowenjing',
    'name':'肖文静',
    'nicknames': '肖文静'
    },
    {
    'pin_yin':'zhangziying',
    'name':'张紫颖',
    'nicknames': '张紫颖'
    }

]

def get_black_room_list():
    msg = ''
    if len(global_config.DEACTIVE_MEMBER_ROOM_ID_LIST) > 0:
        for item in global_config.DEACTIVE_MEMBER_ROOM_ID_LIST:
            pin_yin = item[0]
            for name_obj in member_list:
                if pin_yin == name_obj['pin_yin']:
                    msg += '%s\n' % (name_obj['name'])
                    break
        msg = '当前小黑屋:\n%s' % (msg)
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
                    msg += '%s\n' % (name_obj['name'])
                    break
        msg = '当前小白屋:\n%s' % (msg)
    else:
        msg = '没有成员在小白屋~'
    return msg

def get_order_name(order):
    line = order.decode('utf8')
    ptn = re.compile(u'-[\u4e00-\u9fa5]{2}(.*?)消息')
    res = ptn.search(line)
    if res:
        return res.group(1)
    else:
        return


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
    print md5_string
    sign = hashlib.md5(md5_string).hexdigest()[5:21]
    print sign
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
 
