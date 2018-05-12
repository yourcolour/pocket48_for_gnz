import json
from utils.config_reader import ConfigReader
from utils import global_config
import sys
import os
import socket
from utils.scheduler import scheduler

# 读取口袋48的配置
global_config.MEMBER_JSON = json.load(open('data/member.json', encoding='utf8'))['members']
global_config.ROOM_ID_JSON = json.load(open('data/jujuroom.json', encoding='utf8'))['room_ids']
global_config.POCKET48_VERSION = ConfigReader.get_property('root', 'version')
global_config.IMEI = ConfigReader.get_property('root', 'imei')

using_pro = ConfigReader.get_property('root', 'using_coolq_pro')
if using_pro == 'yes':
    global_config.USING_COOLQ_PRO = True


if __name__ == '__main__':
    import pocket48_plugin
    from pocket48_plugin import bot
    import statistic_plugin
    # import weibo_plugin
    # import modian_plugin

    # 动态获取本机ip
    def get_host_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip
    host = get_host_ip()

    # 每天12点重启爬虫
    @scheduler.scheduled_job('cron', second='0', minute='0', hour='0', day_of_week='*')
    def restart_program():
      python = sys.executable
      os.execl(python, python, * sys.argv)

    scheduler.start()
    print ('启动定时任务')
    port = ConfigReader.get_property('root', 'port')
    bot.run(host=host, port=port)
