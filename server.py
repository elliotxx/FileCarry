#coding=gbk
#
# 服务端
#   接收文件服务
#

from FileCarry import * 

fc = FileCarry()
fc.recvServer()     # 开启接收文件服务


del fc
