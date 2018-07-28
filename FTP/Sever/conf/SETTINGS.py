#Downtiser
import os
'''服务器主要配置文件'''


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Data_base_info = {
    'DB_path':BASE_DIR+'/data',
    'DB_name':'MY_DATABASE',
    'DB_engine':'FileStorage'
}

Storage_base_info = {
    'Storage_path':BASE_DIR+'\\storage',
    'Storage_name':'MY_STORAGE',
    'Storage_Type':'FileStorage'
}

sever_host_info = {
    'address':'localhost',
    'port':6080
}