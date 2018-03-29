# -*- coding: utf-8 -*-
# 修改配置文件
import socket
import configparser
from selenium import webdriver
import subprocess
import time
import getpass
from utils.config_reader import ConfigReader

user_path = '/Users/%s' % getpass.getuser()

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip
    
def run_docker_login_coolq():

    # 付费版
    coolq_url = 'http://dlsec.cqp.me/cqp-xiaoi'

    # 免费版
    # coolq_url = 'http://dlsec.cqp.me/cqa-tuling'
    
    port = ConfigReader.get_property('root', 'port')

    host = get_host_ip()
    
    post_url = 'http://%s:%s' % (host, port)

    bot_qq = ConfigReader.get_property('qq_conf', 'qq')

    cmd = 'docker run -ti --rm --name cqhttp-test -v %s/coolq:/home/user/coolq -p 9000:9000 -p 5700:5700 -e COOLQ_ACCOUNT=%s -e COOLQ_URL=%s -e CQHTTP_POST_URL=%s -e CQHTTP_SERVE_DATA_FILES=yes richardchien/cqhttp:latest' % (user_path, bot_qq, coolq_url, post_url)

    # 运行docker
    print ('运行docker')
    p = subprocess.Popen(cmd, shell=True)

    time.sleep(5)

    login()

def login():
        print ('开始登陆...')
        connect_password = 'MAX8char'
        browser = webdriver.Chrome()
        browser.maximize_window()
        browser.implicitly_wait(10)
        browser.set_page_load_timeout(30)
        browser.get('http://127.0.0.1:9000')
        browser.find_element_by_id('noVNC_connect_button').click()
        browser.find_element_by_id('noVNC_password_input').send_keys(connect_password)
        browser.find_element_by_id('noVNC_password_button').click()
        browser.quit()

def auto_login():
    run_docker_login_coolq()

if __name__ == "__main__": 
    auto_login()