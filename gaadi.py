__author__ = 'yusuf'

from config import *
from ivr_package import ivrlib
import os
import requests
import re
import datetime
import time


script_name = 'gaadi'
ivr_log = logging(str(script_name) + "_ivr")

class Gaadi(ivrlib.IvrLib):
    def __init__(self, session, ivr_log):
        ivrlib.IvrLib.__init__(self, session, ivr_log)
        self.call_start_time = int(time.time()) #Epoch
        self.call_forward_start_time=int(time.time())
        self.caller_id = self.getVar("caller_id_number")
        self.did_number = self.getVar("destination_number")
        self.path_sound = "/var/lib/viva/sounds/ril_petro/"
        self.recording_path = self.path_sound + 'recordings/'

class AgentBusy(Exception):pass

class TotalDisconnect(Exception):pass

def insert_caller_details(connObj):
    conn=pymysql.connect(host='localhost',port=3306,user='root',password='root',database='gaadi',
                         cursorclass=pymysql.cursors.DictCursor,autocommit=True)
    ivr_log.debug(conn)
    mysqlcursor=conn.cursor()
    cursor.execute("INSERT INTO missed_calls (caller) VALUES(%s)",(connObj.caller_id))

def get_cp_list():
    conn=pymysql.connect(host='localhost',port=3306,user='root',password='root',database='gaadi',
                         cursorclass=pymysql.cursors.DictCursor)
    ivr_log.debug(conn)
    mysqlcursor=conn.cursor()
    cursor.execute("""SELECT vc.seq_no,vc.cp_no,vc.sms_flag,vc.isactive
                    FROM vmn_cp vc INNER JOIN did_vmn dv ON vc.vmn_no=dv.vmn_no
                    WHERE dv.did_no=%s ORDER BY vc.seq_no""",(connObj.did_number))
    result=mysqlcursor.fetchall()
    ivr_log.debug("Call patch numbers from db: %s"%(result))
    return result


def process(session):
    connObj = Gaadi(session, ivr_log)
    record_url = '/mnt/reliance_apps/reliance_cc_recordings'
    cmd = '%s/%s.wav' % (record_url, connObj.uuid)
    # connObj.esl_con.execute("record_session", cmd)
    try:
        connObj.playback(connObj.path_sound + 'welcome.wav')
        connObj.cp_list=get_cp_list()
        if connObj.cp_list:
            call_bridge(connObj)
        else:
            ivr_log.debug("No call patch numbers found mapped to the did(vmn) number: %s"%(connObj.did_number))
            raise TotalDisconnect
       # except AgentBusy:
       #  playback agents busy wav file
       #  connObj.hangup_cause="AGENTS_BUSY"

    except AgentBusy:

    except TotalDisconnect:
        ivr_log.debug("TotalDisconnect raised")
        insert_caller_details(connObj)
        exit()

    finally:
        connObj.hangup("NORMAL_CLEARING")
        exit()
# def get_circle_operator(connObj):

def call_bridge(connObj):
    connObj.hangup_stage = 'CALL_BRIDGE_ATTEMPT'
    ans_flag = True
    bridge_start_time = time.time()
    while(ans_flag):
        ans_flag = dial_agent(connObj)
        ivr_log.debug("ans flag is %s" % ans_flag)
        if not ans_flag:
            break
        connObj.playback('/var/lib/viva/sounds/reliance_cc/RIL_TRANSFERCALL.wav')
        time.sleep(2)
        if bridge_start_time - time.time() > 180:
            connObj.hangup_stage = 'CALL_BRIDGE_AGENT_BUSY'
            ans_flag = False
            ivr_log.debug("All agents busy...Recording message")
            voice_recording_module(connObj)

    exit(1)


def dial_agent(connObj):
    ans_flag = True
    # ivr_log.debug(connObj.uuid + "-  Call Bridging: " + connObj.call_center_number)
    # mongodb = mongo()
    # ivr_log.debug(mongodb)
    #output = mongodb.user_master.find({"status":"active", "role":"agent"}).sort("update_time", 1)
    # ivr_log.debug(output)
    cmd_str = "{originate_timeout=40,ignore_early_media=true,origination_caller_id_number=2242830995,reliance_call_leg=agent}"
    ivr_log.debug(cmd_str)
    for cp_num in connObj.cp_list:
        if connObj.hangup_cause in ['NORMAL_CLEARING', '']:
            return False
        ivr_log.debug(cp_num)
        # agent_sip_user =  str(data["sip_username"])
        # print agent_sip_user
        # agent_id = str(data["_id"])
        cmd_str = """{dialed_user="+str(agent_sip_user)+",originate_timeout=40,ignore_early_media=true,
                    origination_caller_id_number=2242830995,reliance_call_leg=agent}"""
        #dynamic_cmd = '%suser/%s' % (cmd_str, agent_sip_user)
        dynamic_cmd = '%ssofia/internal/%s%s' % (cmd_str, agent_sip_user, '%10.0.0.233')
        #update_id = mongodb.user_master.update({"_id":ObjectId(agent_id)},{"$set": {'update_time':datetime.datetime.now()}})
        #ivr_log.debug(update_id)
        bridge_start(connObj, agent_sip_user)
        connObj.bridge(dynamic_cmd)

        ivr_log.debug('last_bridge_hangup_cause is %s' % connObj.getVar("last_bridge_hangup_cause"))
        connObj.hangup_cause = connObj.getVar("last_bridge_hangup_cause")
        #bridge_end(connObj, agent_sip_user)
        print 'hangup cause is %s' % connObj.hangup_cause
        if connObj.hangup_cause in ['NORMAL_CLEARING', '']:
            return False
    return ans_flag




def voice_recording_module(connObj):
    ivr_log.debug(":::Entered in voice_recording_module:::")
    connObj.recorded_file_path = recording_sound + connObj.uuid + "_" + connObj.caller_id + "_record_.wav"
    connObj.hangup_stage = 'CALL_RECORDING_MODULE'
    try:
        if connObj.esl_con.connected():
            connObj.playback(connObj.path_sound + connObj.language + 'Recordafterbeep.wav')
            connObj.playback("tone_stream://%(300,0,754)")  # beep
            connObj.setVar('playback_terminators', '#')
            connObj.record(connObj.recorded_file_path, 30)
    except Exception as e:
        ivr_log.debug("Exception raised e: %s" % e)
    finally:
        raise TotalDisconnect

def sms_module(connObj):
    msg = 'You have a missed call from %s'connObj.caller_id
    for cp in connObj.cp_list:
        if cp['sms_flag']==1:
            sms_dictionary = {
                    'username': '',
                    'password': '',
                    "mobileno": cp['cp_no'],
                    "message": msg,
                    "cdmaheader": "",
                    "senderid" : "",
                    "is_international": False
            }
            ivr_log.debug(sms_dictionary)
            sms_response = connObj.send_sms(sms_dictionary )
            ivr_log.debug(sms_response)


#connObj.call_start_time
#connObj.call_end_time
#connObj.call_forward_start_time
#connObj.call_forward_end_time
#connObj.call_patch_start_time
#connObj.call_patch_end_time