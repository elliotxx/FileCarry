#coding=gbk
#
# �ͻ���
#   �����ļ�
#

from FileCarry import *
import sys
import os

fc = FileCarry()
if len(sys.argv)==1:
    print '[ERROR] : �����뷢�Ͷ���'
else:
    fc.mulSend()

os.system('pause')

del fc

