#Downtiser
import os,sys,json
from Sever.conf import SETTINGS
'''数据库连接模块'''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = SETTINGS.Data_base_info['DB_path']
file_path = SETTINGS.Storage_base_info['Storage_path']

def get_path(file):
    '''
    The function is used to get the specific file's path
    in database
    :param file:
    :return:
    '''
    return data_path+'/%s'%file

def dump_info(path, info):
    '''
    To dump specific information to specific
    file path.
    :param path:
    :param info:
    :return:
    '''

    f =open(path,'w')
    f.write(json.dumps(info))
    f.close()

def get_dir_path(file):
    '''
    To get the specific user's home directory path
    :param file:
    :return:
    '''
    return file_path+'\\%s@home'%file
