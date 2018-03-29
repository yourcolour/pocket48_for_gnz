# -*- coding: utf-8 -*-
# 修改配置文件
import time
from urllib.request import urlretrieve
import socket
socket.setdefaulttimeout(30)
import subprocess
import os
import requests
import getpass

def do_load_aac_media(download_url, aac_floder_path, time_stamp):
    aac_abs_path = '%s/%s.acc' % (aac_floder_path, time_stamp)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.3.2.1000 Chrome/30.0.1599.101 Safari/537.36"}
        pre_content_length = 0
        # 循环接收视频数据
        while True:
            # 若文件已经存在，则断点续传，设置接收来需接收数据的位置
            if os.path.exists(aac_abs_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(aac_abs_path)
            res = requests.get(download_url, stream=True, headers=headers)

            content_length = int(res.headers['content-length'])
            # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
            if content_length < pre_content_length or (
                    os.path.exists(aac_abs_path) and os.path.getsize(aac_abs_path) == content_length):
                break
            pre_content_length = content_length

            # 写入收到的视频数据
            with open(aac_abs_path, 'ab') as file:
                file.write(res.content)
                file.flush()
                print('receive data，file size : %d   total size:%d' % (os.path.getsize(aac_abs_path), content_length))
    except Exception as e:
        print(e)

def encode_acc_to_silk(aac_floder_path, raw_floder_path, silk_floder_path, silk_encoder_path, time_stamp):
    # aac转raw  raw转silk
    aac_abs_name = '%s/%s.acc' % (aac_floder_path, time_stamp)
    raw_abs_name = '%s/%s.raw' % (raw_floder_path, time_stamp)
    silk_abs_name = '%s/%s.silk' % (silk_floder_path, time_stamp)

    cmd1 = 'ffmpeg -i %s -f s16le -ar 44100 -ac 1 %s' % (aac_abs_name, raw_abs_name)

    p = subprocess.call(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    cmd2 = '%s/encoder %s %s -tencent' % (silk_encoder_path, raw_abs_name, silk_abs_name)
    p2 = subprocess.call(cmd2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def sound_downloda(download_url):
    # 先把文件下载到tmp-record文件夹, aac-->raw-->silk
    time_stamp = time.time()
    user_path = '/Users/%s' % getpass.getuser()
    pwd = os.getcwd()
    aac_floder_path = '%s/tmp-record/record-acc' % pwd
    raw_floder_path = '%s/tmp-record/record-raw' % pwd
    silk_floder_path = '%s/coolq/data/record' % user_path
    silk_encoder_path = '%s/silk-v3-decoder/silk' % pwd
    do_load_aac_media(download_url, aac_floder_path, time_stamp)
    encode_acc_to_silk(aac_floder_path, raw_floder_path, silk_floder_path, silk_encoder_path, time_stamp)
    return '%s.silk' % (time_stamp)

def image_download(download_url, path):
    time_stamp = ''
    try:
        time_stamp = time.time()
        urlretrieve(download_url,'%s/%s.jpg' % (path, time_stamp))
    except socket.timeout:
        count = 1
        while count <= 2:
            try:
                time_stamp = time.time()
                urlretrieve(download_url,'%s/%s.jpg' % (path, time_stamp))                                            
                break
            except socket.timeout:
                err_info = 'Reloading for %d time'%count if count == 1 else 'Reloading for %d times'%count
                print(err_info)
                count += 1
        if count > 2:
            print("downloading picture fialed!")
    return '%s.jpg' % time_stamp

if __name__ == '__main__':
    url = 'https://nos.netease.com/nim/NDA5MzEwOA==/bmltYV8xMzAyNTcyMDRfMTUyMDg2ODkxNzA3MV9mN2QxYzY3Ny0zNTYyLTRkMDEtODlmZS1mMzc0MDBhZmQ2MTg='
    name = sound_downloda(url)
    print (name)
