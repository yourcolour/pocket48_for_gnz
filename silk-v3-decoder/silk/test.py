# -*- coding: utf-8 -*-
# 修改配置文件
import subprocess
native_name = '1521429387.203373.aac'
raw_name = '1521429387.203373.raw'
silk_name = '1521429387.203373.silk'

cmd1 = 'ffmpeg -i %s -f s16le -ar 44100 -ac 1 %s' % (native_name, raw_name)

p = subprocess.call(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

cmd2 = './encoder %s %s -tencent' % (raw_name, silk_name)
p2 = subprocess.call(cmd2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)