# coding=gbk
#
# ����˹��ܣ�
#       ��������
#       �׽���IP��ַ����Ϊģ����ַ0.0.0.0��������������
#
# �ͻ��˹��ܣ�
#       ��������
#       �׽���IP��ַ����Ϊ���Ͷ����IP��ַ
#
# + ʹ��pack��unpack����ļ�
# + ���봫������Ĺ���
# + �ֿ鴫��/�����ļ�

import os
import sys
import time
import socket
import ConfigParser
import struct

class FileCarry:
    def __init__(self):
        # ��ȡ�����ļ�
        cf = ConfigParser.ConfigParser()
        try:
            #cf.read(os.path.join(sys.path[0],'config.ini'))
            #cf.read(os.path.join(os.path.split(os.path.realpath(__file__))[0],'config.ini'))
            cf.read('./config.ini')
        except Exception,e:
            print '�����ļ���ȡʧ�ܣ�\n',e
            exit(1)
            
        self.clientIP = cf.get('IP','client')                # �ͻ���IP��ַ����
        self.serverIP = cf.get('IP','server')                # �����IP��ַ����
        self.port = cf.getint('PORT','port')            # ����˿�
        self.recvPath = cf.get('PATH','recv')       # �����ļ���Ŀ¼
        self.BUFSIZE = cf.getint('OTHER','bufsize')       # ���ܵ����������
        self.format = cf.get('OTHER','packformat')      # pack ��unpack�ĸ�ʽ���ַ���
        self.maxlisten = cf.getint('OTHER','maxlisten')     # ���������

        # ��ʼ���׽���
        self.recvSock = None
        self.sendSock = None

        # ��ʼ�������ʽ��С
        self.FILEINFO_SIZE = struct.calcsize(self.format)        # �����ʽ��С


    def showConfig(self):
        # ��ӡ��ǰ����
        print '[����]'
        print '�ͻ���IP��ַ���ã�',self.clientIP
        print '�����IP��ַ���ã�',self.serverIP
        print '����˿ڣ�',self.port
        print '�����ļ�Ŀ¼��',self.recvPath
        print '�����������',self.BUFSIZE
        print 'pack/unpack��ʽ���ַ�����',self.format
        print '�����������',self.maxlisten

        
    def recvServer(self):
        # ����˳���
        # �����Ƿ����ļ�������������У������ļ�
        self.recvSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)       # ���÷��Ͷ�socket�׽���
        self.recvSock.bind((self.serverIP,self.port))      # ��ip��ַ�ͼ����˿�
        self.recvSock.listen(self.maxlisten)                           # ���������������

        while True:     # ��ʼѭ�����ܿͻ�������
            print '���շ��������С���'
            try:
                connection, address=self.recvSock.accept()       # ���ܿͻ��˵���������
            except Exception,e:
                print '���ܵ��ͻ���[%s]���󣬵������Ӵ���ʧ��\n' % (address[0]),e
                connection.send('[�����]:��������ʧ��')
                continue 
            else:
                # ���ܵ����󣬿�ʼ��������
                print '���ܵ��ͻ���[%s]�����ѽ�������' % (address[0])
                connection.send('[�����]:�ѽ�������')

            # ��������
            print '��ʼ�������ݡ���'
            try:
                fhead = connection.recv(self.FILEINFO_SIZE)         # �����ļ���Ϣ
            except Exception,e:
                print '�ļ���Ϣ����ʧ��'
                connection.send('[�����]:�ļ���Ϣ����ʧ��')
                continue
            else:
                filepath,filesize = struct.unpack(self.format,fhead)     # ������õ��ļ������ļ���С
                filename = filepath.split("\\")[-1].strip('\00').strip()      # ��ȡ�ļ���
                recvFullPath = os.path.join(self.recvPath,filename)     # ����·��
                restsize = filesize         # ����ʣ�ഫ����
            try:
                connection.settimeout(30)           # �����׽��ֲ�����ʱʱ��
                print '[%s] ===> \n[%s]' % (address[0]+':\\'+filepath.strip('\00'),recvFullPath)

##                # ������ļ�
##                if filesize==0:
##                    buf = '\00'
##                else:
##                    buf=connection.recv(self.BUFSIZE)    # ���յ����������Ϊ1M
                
                # ������д���ļ�
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
                
                print '���ݽ������'
                connection.send('[�����]:���ݽ������')
                
            except socket.timeout:
                print 'socket timeout'
                
            except Exception,e:
                print '�������ݹ��̳����쳣\n',e

            connection.close()      # �ر�����
            print '���������ѹر�\n'
            

    def send(self,filename):
        # �ͻ��˳���
        # �����ļ�����������
        if not os.path.exists(filename):
            print '�����ļ�������'
            exit(1)
            
        self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)   # �������Ͷ�socket�׽���
            
        try:
            print '���ڳ���������[%s]�������ӡ���' % (self.clientIP)
            self.sendSock.connect((self.clientIP,self.port))               # ��ip��ַ�ͼ����˿�
            time.sleep(2)           # �ȴ����ӷ����
        except Exception,e:
            print 'ERROR : �����˵����ӳ���\n',e
            exit(1)
            
        data = self.sendSock.recv(self.BUFSIZE)     # ���շ���˷��ص�ָ��
        print data

        print '���ڷ����ļ�[%s]����' % (filename)


        fhead = struct.pack(self.format , filename , os.stat(filename).st_size)     # �ļ���Ϣ���
        self.sendSock.sendall(fhead)    # �����ļ���Ϣ
        
        # �����ļ�
        f = open(filename,'rb')
        while True:
            data = f.read(self.BUFSIZE)
            if not data:break
            self.sendSock.send(data)
        f.close()


        while True:     # ������˻�������ȫ�����
            try:
                data = self.sendSock.recv(self.BUFSIZE)
                if data:
                    print data
                else:
                    break
            except:     # ������Ѿ��ر�����
                break
        
        self.sendSock.close()
        print '���ӹر�\n'

    def mulSend(self):
        # ���ط��ͣ������ļ���Ϊ����һ��
        if len(sys.argv) == 1:
            print 'ֻ��һ������������Ҫ���ط���'
            return
        elif len(sys.argv) >= 2:
            # �������������ϲ������Զ�ת���ɿͻ��˷���ģʽ�����͵�ini�ж���ķ����ip��ַ
            for i in range(1,len(sys.argv)):
                self.send(sys.argv[i])
        

    def __del__(self):
        # ��������
        if self.recvSock:       
            self.recvSock.close()       # �رշ�����׽���
        if self.sendSock:
            self.sendSock.close()         # �رտͻ����׽���


if __name__=='__main__':
    fc = FileCarry()
    if len(sys.argv) == 1:
        fc.showConfig()
    elif len(sys.argv) >= 2:
        # �������������ϲ������Զ�ת���ɿͻ��˷���ģʽ�����͵�ini�ж���ķ����ip��ַ
        fc.mulSend()
        os.system('pause')

