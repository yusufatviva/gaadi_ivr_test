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

class AgentBusy(Exception):pass

def process(conn):
    connObj = ivrlib.IvrLib(conn, ivr_log)
    connObj.call_start_time = int(time.time()) #Epoch
    connObj.caller_id = connObj.getVar("caller_id_number")
    connObj.did_number = connObj.getVar("destination_number")
   try:
        get_agents(connObj)
        dial_agent(connObj)


# def get_circle_operator(connObj):

def get_agents(connObj):
    mysqlcursor.execute("SELECT vc.cp_no,vc.seq_no FROM vmn_cp vc INNER JOIN did_vmn dv ON vc.vmn_no=dv.vmn_no WHERE dv.did_no=%s ORDER BY vc.seq_no")
    a=mysqlcursor.fetchall()
    print a
    for b in a:
       print b['seq_no'],b['cp_no']
    """Print results
    a--->[{u'seq_no': 1, u'cp_no': '9022'}, {u'seq_no': 2, u'cp_no': '9323'}, {u'seq_no': 3, u'cp_no': '9820'}, {u'seq_no': 4, u'cp_no': '9819'}]
    b--->
    1 9022
    2 9323
    3 9820
    4 9819"""
    #get vmn from did (MySQL)
    #get agents m1,m2,m3 in sequence from vmn (MySQL)

def call_bridge_cre(connObj):
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
            # voice_recording_module(connObj)

    exit(1)


def dial_agent(connObj):
    ans_flag = True
    ivr_log.debug(connObj.uuid + "-  Call Bridging: " + connObj.call_center_number)
    mongodb = mongo()
    ivr_log.debug(mongodb)

    output = mongodb.user_master.find({"status":"active", "role":"agent"}).sort("update_time", 1)
    ivr_log.debug(output)
    cmd_str = "{originate_timeout=40,ignore_early_media=true,origination_caller_id_number=2242830995,reliance_call_leg=agent}"
    ivr_log.debug(cmd_str)
    for data in output:
        if connObj.hangup_cause in ['NORMAL_CLEARING', '']:
            return False
        ivr_log.debug(data)
        agent_sip_user =  str(data["sip_username"])
        print agent_sip_user
        agent_id = str(data["_id"])
        cmd_str = "{dialed_user="+str(agent_sip_user)+",originate_timeout=40,ignore_early_media=true,origination_caller_id_number=2242830995,reliance_call_leg=agent}"
        #dynamic_cmd = '%suser/%s' % (cmd_str, agent_sip_user)
        dynamic_cmd = '%ssofia/internal/%s%s' % (cmd_str, agent_sip_user, '%10.0.0.233')
        #update_id = mongodb.user_master.update({"_id":ObjectId(agent_id)},{"$set": {'update_time':datetime.datetime.now()}})
        #ivr_log.debug(update_id)
        #bridge_start(connObj, agent_sip_user)
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
    #connObj.recorded_file_path = recording_sound + connObj.uuid + "_" + connObj.caller_id + "_record_.wav"
    connObj.hangup_stage = 'CALL_RECORDING_MODULE'
    try:
        if connObj.esl_con.connected():
            connObj.playback(connObj.path_sound + connObj.language + 'Recordafterbeep.wav')
            connObj.playback("tone_stream://%(300,0,754)")  # beep
            connObj.setVar('playback_terminators', '#')
            connObj.record(connObj.recorded_file_path, 30)
    except Exception as e:
        ivr_log.debug("Exception raised e: %s" % e)
    #finally:
        #raise TotalDisconnect



def sms_module(connObj):
    single_msg = '\xe0\xa4\xb8\xe0\xa5\x8d\xe0\xa4\x9f\xe0\xa5\x87\xe0\xa4\xab\xe0\xa5\x8d\xe0\xa4\xb0\xe0\xa5\x80 \xe0\xa4\xb9\xe0\xa5\x87\xe0\xa4\xb2\xe0\xa5\x8d\xe0\xa4\xaa\xe0\xa4\xb2\xe0\xa4\xbe\xe0\xa4\x88\xe0\xa4\xa8 \xe0\xa4\xae\xe0\xa4\xa7\xe0\xa5\x8d\xe0\xa4\xaf\xe0\xa5\x87 \xe0\xa4\xae\xe0\xa5\x8b\xe0\xa4\xab\xe0\xa4\xa4 \xe0\xa4\x95\xe0\xa5\x89\xe0\xa4\xb2 \xe0\xa4\x95\xe0\xa4\xb0\xe0\xa4\xbe 18002672222'
    if connObj.kkb_content_heard:
            single_msg = '\xe0\xa4\xb8\xe0\xa5\x8d\xe0\xa4\x9f\xe0\xa5\x87\xe0\xa4\xab\xe0\xa5\x8d\xe0\xa4\xb0\xe0\xa5\x80 \xe0\xa4\xb9\xe0\xa5\x87\xe0\xa4\xb2\xe0\xa5\x8d\xe0\xa4\xaa\xe0\xa4\xb2\xe0\xa4\xbe\xe0\xa4\x88\xe0\xa4\xa8 \xe0\xa4\xae\xe0\xa4\xa7\xe0\xa5\x8d\xe0\xa4\xaf\xe0\xa5\x87 \xe0\xa4\xae\xe0\xa5\x8b\xe0\xa4\xab\xe0\xa4\xa4 \xe0\xa4\x95\xe0\xa5\x89\xe0\xa4\xb2 \xe0\xa4\x95\xe0\xa4\xb0\xe0\xa4\xbe 18002672222'
    sms_dictionary = {
            'username': 'SFMarathi_IVR',
            'password': '279556',
            "mobileno": connObj.caller_id,
            "message": single_msg,
            "cdmaheader": "SFHELP",
            "senderid" : "SFHELP",
            'coding':2,
            "is_international": False
    }
    # if connObj.kkb_content_heard:
    ivr_log.debug(sms_dictionary )
    sms_response = connObj.send_sms(sms_dictionary )
