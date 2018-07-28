#Downtiser
import logging,os
from Sever.conf import SETTINGS
'''日志记录模块，待完善'''
log_type = {
    'debug':logging.debug,
    'info':logging.info,
    'warning':logging.warning,
    'error':logging.error,
    'critical':logging.critical
}

# log_level = {
#     'DEBUG':logging.DEBUG,
#     'INFO':logging.INFO,
#     'WARNING':logging.WARNING,
#     'ERROR':logging.ERROR,
#     'CRITICAL':logging.CRITICAL
# }
sever_log_path = SETTINGS.Data_base_info['DB_path'] + '/sever_log/My_sever_log.log'
def sever_logger(message,level):
    logging.basicConfig(filename=sever_log_path, level=logging.DEBUG, format='%(asctime)s %(levelno)s %(levelname)s %(message)s')
    log_type[level](message)


def private_logger(log_path,message,level):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s %(levelno)s %(levelname)s %(message)s')
    log_type[level](message)

path = SETTINGS.Storage_base_info['Storage_path']+'\\downtiser@home\\log\\my_log.log'

private_logger('E:\pycharmProjects\FTP\Sever\storage\downtiser@home\log\My_log.log','123',level='info')