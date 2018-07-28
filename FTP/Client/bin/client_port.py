#Downtiser
import socket
from Client.core import client_main
'''用户端口'''
print("-----Downtiser's FTP System-----")
while True:
    user_choice = input('输入q以退出本FTP系统，或输入其他任意值以继续>>>')
    if user_choice == 'q':
        exit('成功退出!')
    while True:
        try:
            host_ip = input('请输入服务器IP地址>>>').strip()
            port = int(input('请输入端口号>>>').strip())
            clint = client_main.ClientFTP()
            clint.connect(host_ip, port)
            clint.interact()
        except (socket.gaierror, ConnectionRefusedError) as e:
            print('无法连接到服务器！请检查您输入的地址与端口号是否正确! ERROR %s'%e)
            break
        except Exception as e:
            print('未知错误 ERROR %s'%e)

