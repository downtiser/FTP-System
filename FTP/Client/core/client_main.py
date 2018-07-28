#Downtiser
import socket
import os,json,hashlib
from Client.conf import SETTINGS
'''和服务端错误代码相匹配的错误信息字典'''
Error_dict = {
    '101':'磁盘空间不足！',
    '201':'权限不足!',
    '104':'账户不存在!',
    '207':'密码错误!',
    '309':'目录不存在!',
    '507':'不合法的分隔符!',
    '404':'文件不存在!'

}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class ClientFTP(object):
    '''
    The main class to instantiate a client port object
    '''
    def __init__(self):
        self.client = socket.socket()

        self.storage_path = SETTINGS.local_storage_info['storage_path']
    def authenticate(self):
        '''
        The authenticate function is used to authenticate a user's validity through
        the inputted account_id and password
        :return:
        '''
        account_id = input('请输入您的用户名>>>').strip()
        password = input('请输入您的密码>>>').strip()
        self.info = {
            'account_id': account_id,
            'password': password
        }
        self.client.send(json.dumps(self.info).encode('utf-8'))
        self.auth = self.client.recv(1024).decode()
        if self.auth in Error_dict:
            print('ERROR %s>>>%s'%(self.auth, Error_dict[self.auth]))
            return False
        else:
            return True

    def connect(self, ip, port):
        '''
        Try to connect the sever_host through the ip address and port id
        :param ip:
        :param port:
        :return:
        '''
        self.client.connect((ip, port))

    def help(self,*args):
        '''
        The help function is used to
        :param args:
        :return:
        '''
        print('----命令列表----')
        print('ls 查看当前目录下的文件')
        print('pwd 查看当前所在目录 ')
        print('upload 文件名 上传文件')
        print('download 文件名 下载文件')
        print('cd /../ 进入指定目录')


    def ls(self,*args):
        '''
        The ls function is used to send a ls command to sever host and try to
        get the list contains file and directory of current directory
        :param args:
        :return:
        '''
        cmd_split = args[0].split()
        if len(cmd_split) == 1:
            cmd_dict = {
                'command':cmd_split[0]
            }
            self.client.send(json.dumps(cmd_dict).encode('utf-8'))
            list_size = int(self.client.recv(1024).decode())
            self.client.send(b'1')
            received_size = 0
            received_list = b''
            while received_size < list_size:
                data = self.client.recv(8192)
                received_list += data
                received_size += len(data)
            else:
                dir_list = json.loads(received_list.decode())
                for i, item in enumerate(dir_list):
                    print(i+1,item)
        else:
            print('无效的命令！')
            self.help()

    def pwd(self,*args):
        '''
        The pwd function is used to send a pwd command to sever host and try to
        get current directory name from sever
        :param args:
        :return:
        '''
        cmd_split = args[0].split()
        if len(cmd_split) == 1:
            cmd_dict = {
                'command':cmd_split[0]
            }
            self.client.send(json.dumps(cmd_dict).encode('utf-8'))
            current_path = self.client.recv(1024).decode()
            print(current_path)
        else:
            print('无效的命令!')
            self.help()

    def upload(self,*args):
        '''
        The upload function is used to upload local file to your own storage in
        sever host.
        :param args:
        :return:
        '''
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            if os.path.isfile(cmd_split[1]):
                filename = cmd_split[1]
                filesize = os.stat(filename).st_size
                file_dict = {
                    'command':cmd_split[0],
                    'filename':filename,
                    'filesize':filesize
                }
                self.client.send(json.dumps(file_dict).encode('utf-8'))
                sever_respond = self.client.recv(1024).decode()
                if sever_respond in Error_dict:
                    print('ERROR %s>>>%s'%(sever_respond, Error_dict[sever_respond]))
                else:
                    print('文件上传中......')
                    f = open(filename, 'rb')
                    for line in f:
                        self.client.send(line)
                    f.close()
                    print('文件上传成功！')
            else:
                print('文件不存在！')

    def download(self,*args):
        '''
        The download function is used to download file in your own storage
        from the sever host.
        :param args:
        :return:
        '''
        cmd_split = args[0].split()
        if len(cmd_split) >1:
            filename = cmd_split[1]
            cmd_dict = {
                'command':cmd_split[0],
                'filename':filename
            }
            self.client.send(json.dumps(cmd_dict).encode('utf-8'))
            sever_respond = self.client.recv(1024).decode()
            if sever_respond in Error_dict:
                print('ERROR %s>>>%s' % (sever_respond, Error_dict[sever_respond]))
            else:
                self.client.send(b'1')
                filesize = int(self.client.recv(1024).decode())
                self.client.send(b'1')
                file_path = self.storage_path + '/%s'%filename
                if os.path.isfile(file_path):
                    file_path = self.storage_path+'/_new%s'%filename

                f = open(file_path, 'wb')
                client_md5 = hashlib.md5()
                received_size = 0
                n = 10
                print('文件下载中.....')
                while received_size < filesize:
                    if filesize - received_size > 8192:
                        size = 8192
                    else:
                        size = filesize - received_size
                    data = self.client.recv(size)
                    received_size += len(data)
                    client_md5.update(data)
                    f.write(data)
                    if int((received_size / filesize) * 100) / n > 1:
                        print('##', end='')
                        n += 10
                else:
                    self.client.send('客户端已成功接受文件'.encode('utf-8'))
                    print('文件已接收完成！')
                    f.close()
                    sever_md5 = self.client.recv(1024).decode()
                    print('源文件MD5>>>%s  本地文件MD5>>>%s'%(sever_md5, client_md5.hexdigest()))

        else:
            print('无效的命令!')
            self.help()



    def cd(self,*args):
        '''
        The cd function is used to send cd command to the sever host and try
        to enter the specific directory
        :param args:
        :return:
        '''
        cmd_spilt = args[0].split()
        if len(cmd_spilt) > 1:
            dir_path = cmd_spilt[1]
            cmd = cmd_spilt[0]
            cmd_dic = {
                'command':cmd,
                'dir_path':dir_path
            }
            self.client.send(json.dumps(cmd_dic).encode('utf-8'))
            sever_respond = self.client.recv(1024).decode()
            if sever_respond in Error_dict:
                print('ERROR %s>>>%s' % (sever_respond, Error_dict[sever_respond]))
            else:
                print(sever_respond)

    def interact(self):
        '''
        The main interact function for a client object to interact with the
        sever host
        '''
        while True:
            if self.authenticate():
                while True:
                    command = input('请输入命令>>>')

                    if not command:

                        continue
                    cmd = command.split()[0]
                    if hasattr(self, cmd):
                        func = getattr(self, cmd)
                        func(command)
                    else:
                        print('无效的命令！')
                        self.help()
                        continue



