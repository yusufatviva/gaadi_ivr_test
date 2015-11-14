_author__ = 'vipul'
import pymysql
from pymongo import MongoClient
import redis
import datetime
from ivr_package.logClass import Log
import os

config_logpath = '/var/log/python_ivr_logs'

sounds_path = '/home/aawaz/sounds/'

myLog = Log()
setup_name = os.environ.get('LOCATION', "PUNE")
# print setup_name
mq_server = ""
mongo_server = ""
dump_mongo_server = ""
aawaz_mongo_host = ""
mysql_server = ""
redis_server = ""
mongo_fb = ""
node_call_log_url = ""
ivr_api_url = ""
print setup_name
if setup_name == "PUNE":
    node_call_log_url = "http://10.0.5.110:8001/aawaz/api/call_info_ivr"
    ivr_api_url = "http://10.0.5.106/aawaz/api/ivr_dtmf"
    fb_url = "http://10.0.5.106/aawaz/api/"
    aawaz_api_url="http://aawazapi.vivaconnect.in/campaign_api"
    mq_server = '10.0.5.101'
    mongo_server = '10.0.5.113'
    mongo_fb = "10.0.5.113"
    dump_mongo_server = '10.0.5.109'
    aawaz_mongo_host = ['punefs102:27017', 'punefs103:27017', 'punedb2:27017']
    mysql_server = '10.0.5.106'
    redis_server = '10.0.5.106'
elif setup_name == "MUMBAI":
    node_call_log_url = "http://10.0.1.207:8001/aawaz/api/call_info_ivr"
    ivr_api_url = "http://10.0.0.215:8001/aawaz/api/ivr_dtmf"
    aawaz_api_url="http://10.0.0.215:8000/campaign_api"
    mq_server = '10.0.1.208'
    mongo_server = '10.0.1.207'
    mongo_fb = '10.0.1.207'
    dump_mongo_server = '10.0.0.215'
    mysql_server = '10.0.1.208'
    redis_server = '10.0.0.215'


def mongo(hostname=mongo_fb, port=27017, db='new_aawaz'):
    mongo_connection = MongoClient(hostname, port)
    mongo_database = mongo_connection[db]
    return mongo_database

#
# def redis_connect(hostname=redis_server, port=6379, db=0):
#     r = redis.StrictRedis(hostname, port, db)
#     return r


def mysql_conn(mysql_server=mysql_server, mysql_port=3306, mysql_user='root', mysql_password='Jh90Ckb.c.Tp6',
               mysql_db_name='aawaz'):
    db_connection = pymysql.connect(host=mysql_server, port=mysql_port, user=mysql_user,
                                    passwd=mysql_password, db=mysql_db_name,
                                    cursorclass=pymysql.cursors.DictCursor)
    db_connection.autocommit(1)
    return db_connection


# def mongo_live(hostname=mongo_server, port=27017, db='new_aawaz'):
#     mongo_database = None
#     try:
#         mongo_connection = MongoClient(hostname, replicaSet="aawaz", readPreference='secondaryPreferred')
#         mongo_database = mongo_connection[db]
#     except Exception as e:
#         pass
#     finally:
#         return mongo_database


def logging(log_file_name):
    strdate = datetime.datetime.now()
    log_path = os.path.join(config_logpath, str(strdate.year), str(strdate.month), str(strdate.day))
    if not (os.path.exists(log_path)):
        os.makedirs(log_path)

    loger_name = log_file_name + str(strdate.day) + '_' + str(strdate.month) + '_' + str(strdate.year)
    log = myLog.get_logger(loger_name)
    myLog.setup_logger(loger_name, log_path + '/' + str(log_file_name) + '.log')

    myLog.set_level(loger_name, 1)
    myLog.set_level(loger_name, 2)
    return log
