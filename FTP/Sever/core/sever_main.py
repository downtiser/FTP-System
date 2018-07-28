#Downtiser
import socketserver
import json
import os,hashlib
from Sever.core import data_handler
from Sever.log import logger
'''服务器端主逻辑模块'''

'''错误代码参照表'''
Error_dict = {
    '101':'磁盘空间不足！',
    '201':'权限不足!',
    '104':'账户不存在!',
    '207':'密码错误!',
    '309':'目录不存在!',
    '507':'不合法的分隔符',
    '404':'文件不存在'

}

class My_TCP_handler(socketserver.BaseRequestHandler):
    '''
    The man class to create a sever object with relevant method
    to interact with clients
    '''
    def ls(self,*args):
        '''
        The ls function is used to return the list contains the file in
        current directory to client
        :param args:
        :return:
        '''
        dir_list = os.listdir(self.dir_path)
        list_b_obj = json.dumps(dir_list).encode('utf-8')
        list_size = len(list_b_obj)
        self.request.send(str(list_size).encode('utf-8'))
        self.request.recv(1024)
        self.request.send(list_b_obj)

    def pwd(self,*args):
        '''
        The pwd function is used to return the name of current directory
        to client
        :param args:
        :return:
        '''
        m = self.dir_path.rfind('\\')
        current_path = self.dir_path[m+1:]
        self.request.send(current_path.encode('utf-8'))
    def upload(self,*args):
        '''
        The function is used to receive and store the file which is uploaded
        by client in current directory
        :param args:
        :return:
        '''
        cmd_dict = args[0]
        filename = cmd_dict['filename']
        filesize = cmd_dict['filesize']
        if filesize > self.private_info_dict['disc_space']:
            self.request.send(b'101')
            space = int(self.private_info_dict['disc_space']/(1024**2))
            logger.sever_logger('用户[%s]上传文件失败，存储空间不足，存储空间剩余[%s]MB'%(self.private_info_dict['account_id'], space),level='error')
            logger.private_logger(self.log_path, '上传文件失败，存储空间不足，存储空间剩余[%s]MB'%space,level='error')
        else:
            file_path = self.dir_path + '/%s'%filename
            if os.path.isfile(file_path):
                new_path = self.dir_path + '/new_%s'%filename
                f = open(new_path,'wb')
            else:
                f = open(file_path,'wb')
            self.request.send(b'1')
            received_size = 0
            n = 10
            print('文件上传中.....')
            while received_size < filesize:
                if filesize - received_size > 8192:
                    size = 8192
                else:
                    size = filesize - received_size
                data = self.request.recv(size)
                received_size += len(data)
                f.write(data)
                if int((received_size / filesize) * 100) / n >1:
                    print('##',end='')
                    n +=10
            else:
                print('\n文件[%s]已上传完成!'%filename)
                f.close()
                self.private_info_dict['disc_space'] -= filesize
                space = int(self.private_info_dict['disc_space']/(1024**2))
                data_handler.dump_info(self.path, self.private_info_dict)
                logger.sever_logger('用户[%s]成功上传文件[%s]'%(self.private_info_dict['account_id'], filename), level='info')
                print(self.log_path)

                logger.private_logger(self.log_path,'成功上传文件[%s] 剩余存储空间[%s]MB'%(filename, space), level='info')

    def download(self,*args):
        '''
        The function is used to send specific file to client if it
        exist.
        :param args:
        :return:
        '''
        cmd_dict = args[0]
        filename = cmd_dict['filename']
        file_path = self.dir_path+'/%s'%filename
        if os.path.isfile(file_path):
            self.request.send(b'1')
            self.request.recv(1024)
            f = open(file_path,'rb')
            filesize = os.stat(file_path).st_size
            m = hashlib.md5()
            self.request.send(str(filesize).encode('utf-8'))
            self.request.recv(1024)
            for line in f:
                self.request.send(line)
                m.update(line)
            ack = self.request.recv(1024)
            print(ack.decode())
            self.request.send(m.hexdigest().encode('utf-8'))
            logger.sever_logger('用户[%s]成功下载文件[%s]'%(self.private_info_dict['account_id'], filename), level='info')
            logger.private_logger(self.log_path, '成功下载文件[%s]'%filename, level='info')
            f.close()
        else:
            self.request.send(b'404')
            logger.sever_logger('USER:Unknown ERROR ID 404:%s' % Error_dict['404'], level='error')
    def cd(self,*args):
        '''
        The function is used to enter and return the specific
        directory
        :param args:
        :return:
        '''
        client_path = args[0]['dir_path']
        if client_path == '..':
            if self.dir_path == self.BASE_DIR:
                self.request.send(b'201')
            else:
                m = self.dir_path.find('/')
                n = self.dir_path.rfind('/')
                self.dir_path = self.dir_path[0:n]
                client_path = self.dir_path[m:n]
                path = '[downtiser@home %s]' % client_path
                self.request.send(path.encode('utf-8'))

        else:
            if '\\' in client_path:
                self.request.send(b'507')
            else:
                temp_dir_path = self.dir_path + '/%s'%client_path
                temp_dir_path = temp_dir_path.replace('//', '/')

                if os.path.isdir(temp_dir_path):
                    self.dir_path = self.dir_path + '/%s' % client_path
                    self.dir_path = self.dir_path.replace('//', '/')
                    path = '[downtiser@home %s]'%client_path
                    self.request.send(path.encode('utf-8'))

                else:
                    self.request.send(b'309')



    def handle(self):
        '''
        The main interact function to interact with client
        :return:
        '''
        print('客户端已连接!')
        while True:
            try:
                client_info = self.request.recv(1024)
                client_info_dict = json.loads(client_info.decode())
                account_id = client_info_dict['account_id']
                password = client_info_dict['password']
                self.path = data_handler.get_path('%s.json'%account_id)
                if os.path.isfile(self.path):
                    private_info_file = open(self.path, 'r')
                    self.private_info_dict = json.loads(private_info_file.read())
                    if self.private_info_dict['password'] == password:
                        self.request.send(b'1')
                        self.dir_path = data_handler.get_dir_path(account_id)
                        self.BASE_DIR = data_handler.get_dir_path(account_id)
                        self.log_path = self.BASE_DIR+'\\log\\My_log.log'
                        while True:
                            data = self.request.recv(1024)
                            cmd_dict = json.loads(data.decode())
                            command = cmd_dict['command']

                            if hasattr(self,command):
                                func = getattr(self,command)
                                func(cmd_dict)
                    else:
                        self.request.send(b'207')
                        logger.sever_logger('USER:Unknown ERROR ID 207:%s'%(Error_dict['207']), level='error')
                else:
                    self.request.send(b'104')
                    logger.sever_logger('USER:Unknown ERROR ID 104:%s' % Error_dict['104'], level='error')
            except ConnectionResetError as e:
                print('客户端强制断开！ERROR:%s' % e)
                logger.sever_logger('CRITICAL: 客户端强制断开!', level='critical')
                break






