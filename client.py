#coding=gbk
#
# 客户端
#   发送文件
#

from FileCarry import *
import sys
import os

fc = FileCarry()
if len(sys.argv)==1:
    print '[ERROR] : 请输入发送对象！'
else:
    fc.mulSend()

os.system('pause')

del fc

