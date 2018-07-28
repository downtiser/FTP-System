#Downtiser
from Sever.core import sever_main
from Sever.conf import SETTINGS

'''服务器端启动接口'''
Host, Port = SETTINGS.sever_host_info['address'], SETTINGS.sever_host_info['port']
sever = sever_main.socketserver.ThreadingTCPServer((Host, Port),sever_main.My_TCP_handler)
print('服务器已启动!')
sever.serve_forever()