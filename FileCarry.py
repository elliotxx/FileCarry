# coding=gbk
#
# 服务端功能：
#       接受数据
#       套接字IP地址设置为模糊地址0.0.0.0，接受所有请求
#
# 客户端功能：
#       发送数据
#       套接字IP地址设置为发送对象的IP地址
#
# + 使用pack、unpack打包文件
# + 加入传入参数的功能
# + 分块传输/接收文件

import os
import sys
import time
import socket
import ConfigParser
import struct

class FileCarry:
    def __init__(self):
        # 读取配置文件
        cf = ConfigParser.ConfigParser()
        try:
            #cf.read(os.path.join(sys.path[0],'config.ini'))
            #cf.read(os.path.join(os.path.split(os.path.realpath(__file__))[0],'config.ini'))
            cf.read('./config.ini')
        except Exception,e:
            print '配置文件读取失败！\n',e
            exit(1)
            
        self.clientIP = cf.get('IP','client')                # 客户端IP地址设置
        self.serverIP = cf.get('IP','server')                # 服务端IP地址设置
        self.port = cf.getint('PORT','port')            # 传输端口
        self.recvPath = cf.get('PATH','recv')       # 接收文件的目录
        self.BUFSIZE = cf.getint('OTHER','bufsize')       # 接受的最大数据量
        self.format = cf.get('OTHER','packformat')      # pack 和unpack的格式化字符串
        self.maxlisten = cf.getint('OTHER','maxlisten')     # 最大连接数

        # 初始化套接字
        self.recvSock = None
        self.sendSock = None

        # 初始化编码格式大小
        self.FILEINFO_SIZE = struct.calcsize(self.format)        # 编码格式大小


    def showConfig(self):
        # 打印当前配置
        print '[配置]'
        print '客户端IP地址设置：',self.clientIP
        print '服务端IP地址设置：',self.serverIP
        print '传输端口：',self.port
        print '接收文件目录：',self.recvPath
        print '最大数据量：',self.BUFSIZE
        print 'pack/unpack格式化字符串：',self.format
        print '最大连接数：',self.maxlisten

        
    def recvServer(self):
        # 服务端程序
        # 监听是否有文件发送请求。如果有，接受文件
        self.recvSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)       # 设置发送端socket套接字
        self.recvSock.bind((self.serverIP,self.port))      # 绑定ip地址和监听端口
        self.recvSock.listen(self.maxlisten)                           # 设置最大连接数量

        while True:     # 开始循环接受客户端连接
            print '接收服务运行中……'
            try:
                connection, address=self.recvSock.accept()       # 接受客户端的连接请求
            except Exception,e:
                print '接受到客户端[%s]请求，但是连接创建失败\n' % (address[0]),e
                connection.send('[服务端]:连接请求失败')
                continue 
            else:
                # 接受到请求，开始接受数据
                print '接受到客户端[%s]请求，已建立连接' % (address[0])
                connection.send('[服务端]:已建立连接')

            # 接受数据
            print '开始接收数据……'
            try:
                fhead = connection.recv(self.FILEINFO_SIZE)         # 接受文件信息
            except Exception,e:
                print '文件信息接受失败'
                connection.send('[服务端]:文件信息接受失败')
                continue
            else:
                filepath,filesize = struct.unpack(self.format,fhead)     # 解包，得到文件名和文件大小
                filename = filepath.split("\\")[-1].strip('\00').strip()      # 提取文件名
                recvFullPath = os.path.join(self.recvPath,filename)     # 保存路径
                restsize = filesize         # 设置剩余传输量
            try:
                connection.settimeout(30)           # 设置套接字操作超时时间
                print '[%s] ===> \n[%s]' % (address[0]+':\\'+filepath.strip('\00'),recvFullPath)

##                # 处理空文件
##                if filesize==0:
##                    buf = '\00'
##                else:
##                    buf=connection.recv(self.BUFSIZE)    # 接收的最大数据量为1M
                
                # 将数据写入文件
                f = open(recvFullPath,'wb')
                while True:
                    if restsize <= 0: break
                    if restsize > self.BUFSIZE:
                        buf=connection.recv(self.BUFSIZE)
                    else:
                        buf=connection.recv(restsize)
                    if not buf: break
                    f.write(buf)
                    restsize = restsize-len(buf)
                f.close()
                
                print '数据接收完毕'
                connection.send('[服务端]:数据接收完毕')
                
            except socket.timeout:
                print 'socket timeout'
                
            except Exception,e:
                print '接收数据过程出现异常\n',e

            connection.close()      # 关闭连接
            print '本次连接已关闭\n'
            

    def send(self,filename):
        # 客户端程序
        # 发送文件，建立请求
        if not os.path.exists(filename):
            print '发送文件不存在'
            exit(1)
            
        self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)   # 创建发送端socket套接字
            
        try:
            print '正在尝试与服务端[%s]建立连接……' % (self.clientIP)
            self.sendSock.connect((self.clientIP,self.port))               # 绑定ip地址和监听端口
            time.sleep(2)           # 等待连接服务端
        except Exception,e:
            print 'ERROR : 与服务端的连接出错\n',e
            exit(1)
            
        data = self.sendSock.recv(self.BUFSIZE)     # 接收服务端返回的指令
        print data

        print '正在发送文件[%s]……' % (filename)


        fhead = struct.pack(self.format , filename , os.stat(filename).st_size)     # 文件信息打包
        self.sendSock.sendall(fhead)    # 发送文件信息
        
        # 发送文件
        f = open(filename,'rb')
        while True:
            data = f.read(self.BUFSIZE)
            if not data:break
            self.sendSock.send(data)
        f.close()


        while True:     # 将服务端缓冲内容全部输出
            try:
                data = self.sendSock.recv(self.BUFSIZE)
                if data:
                    print data
                else:
                    break
            except:     # 服务端已经关闭连接
                break
        
        self.sendSock.close()
        print '连接关闭\n'

    def mulSend(self):
        # 多重发送，发送文件数为至少一个
        if len(sys.argv) == 1:
            print '只有一个参数，不需要多重发送'
            return
        elif len(sys.argv) >= 2:
            # 两个及两个以上参数，自动转换成客户端发送模式，发送到ini中定义的服务端ip地址
            for i in range(1,len(sys.argv)):
                self.send(sys.argv[i])
        

    def __del__(self):
        # 析构函数
        if self.recvSock:       
            self.recvSock.close()       # 关闭服务端套接字
        if self.sendSock:
            self.sendSock.close()         # 关闭客户端套接字


if __name__=='__main__':
    fc = FileCarry()
    if len(sys.argv) == 1:
        fc.showConfig()
    elif len(sys.argv) >= 2:
        # 两个及两个以上参数，自动转换成客户端发送模式，发送到ini中定义的服务端ip地址
        fc.mulSend()
        os.system('pause')

