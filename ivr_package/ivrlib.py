import json

_author__ = 'Ashish'

from ESL import *
import requests
import traceback
from ivr_package import obd_call, voice360_call
import urllib
from config import *




class IvrLib:
    def __init__(self, esl_conn, ivr_log):
        self.esl_con = esl_conn
        self.info = self.esl_con.getInfo()
        self.uuid = self.info.getHeader('unique-id')
        self.ivr_log = ivr_log
        self.script_name = self.info.getHeader("variable_script_name")
        self.call_direction = self.info.getHeader("Call-Direction")
        self.esl_con.sendRecv("myevents")
        if self.call_direction == "outbound":
            self.request_id = self.get_request_id(str(self.uuid))
            self.user_id = self.get_user_id(self.uuid)
        else:
            self.request_id = ""
            self.user_id = ""


    def getVar(self, ch_var):
        """

        :param self.esl_con:
        :param ch_var:
        :return:
        """
        uuid = self.uuid
        try:
            assert isinstance(self.esl_con, ESLconnection)

            param = uuid + ' ' + ch_var
            api_res = self.esl_con.api('uuid_getvar', str(param))
            if api_res is None or api_res == '':
                result = ''
            else:
                result = api_res.getBody()
            self.ivr_log.info(str(param) + '-' + 'getvar ' + str(result))
            return result
        except Exception, e:
            self.ivr_log.exception(uuid + '-' + 'error while GetVar :-' + str(e))
            return None

    def setVar(self, ch_var, ch_value):
        """

        :param self.esl_con:
        :param ch_var:
        :param ch_value:
        :return:
        """
        uuid = self.uuid
        try:
            assert isinstance(self.esl_con, ESLconnection)

            self.ivr_log.info(uuid + '-' + 'setvar ' + ch_var + ' ' + ch_value)
            self.esl_con.api('uuid_setvar', uuid + ' ' + ch_var + ' ' + ch_value)
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while setVar:-' + str(e))
            traceback.print_exc()

    def playback(self, soundfile, start_position=0):
        """

        :param self.esl_con:
        :param soundfile:
        :return:
        """
        uuid = self.uuid
        try:
            assert isinstance(self.esl_con, ESLconnection)

            self.ivr_log.info(uuid + '-' + 'playback ' + soundfile + ' ' + str(start_position))
            self.esl_con.execute('playback', str(soundfile) + '@@' + str(start_position), uuid)
            self.ivr_log.debug(uuid + '-' + 'playback ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while playback:-' + str(e))
            traceback.print_exc()

    def play_and_get_digit(self, allvar, dtmf_var=None, dtmf_level=0, dtmf_tag=[]):
        """

        :param self.esl_con:
        :param allvar:
        :return:
        """
        uuid = self.uuid
        try:

            if not dtmf_var:
                cmd_list = allvar.split(" ")
                dtmf_var = cmd_list[7]

            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.info(uuid + '-' + 'play_and_get_digits ' + str(allvar))
            self.esl_con.execute('play_and_get_digits', str(allvar))
            dtmf_val = self.getVar(dtmf_var)
            now = datetime.datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            request_id = self.get_request_id(str(self.uuid))
            user_id = self.user_id
            destination_no = self.getVar("caller_id_number")
            if not request_id:
                request_id = ""
            if not user_id:
                user_id = ""
            dtmf_info = {
                "call_uuid": self.uuid,
                "destination_no": destination_no,
                "user_id": user_id,
                "script_name": self.script_name,
                "dtmf_level": dtmf_level,
                "dtmf_tag": dtmf_tag,
                "dtmf": str(dtmf_val),
                "dtmf_timestamp": current_time,
                "request_id": request_id,
                "call_direction": self.call_direction

            }
            self.save_dtmf(dtmf_info)

            return dtmf_val

        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while play_and_get_digit :- ' + str(e))
            traceback.print_exc()

    def answer(self):
        """

        :param self.esl_con:
        :return:
        """
        uuid = self.uuid
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.debug(uuid + '-' + 'answer')
            self.esl_con.execute('answer')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while answering :-' + str(e))
            traceback.print_exc()

    def bridge(self, endpoints):
        """

        :param self.esl_con:
        :param endpoints:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.info(uuid + '-' + 'bridge ' + str(endpoints))
            self.esl_con.execute('bridge', endpoints)
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while bridge:-' + str(e))
            traceback.print_exc()

    def endless_playback(self, soundfile):
        """

        :param self.esl_con:
        :param soundfile:
        :return:
        """
        uuid = self.uuid
        try:
            assert isinstance(self.esl_con, ESLconnection)
            self.ivr_log.info(uuid + '-' + 'endless_playback ' + soundfile)
            self.esl_con.execute('endless_playback', soundfile, uuid)
            self.ivr_log.debug(uuid + '-' + 'endless playback ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while endless_playback:-' + str(e))
            traceback.print_exc()

            # def hangup(self, hangup_cause):
            # """
            #
            # :param self.esl_con:
            # :param hangup_cause:

    # :return:
    # """
    # try:
    # assert isinstance(self.esl_con, ESLconnection)
    # uuid = self.uuid
    # self.ivr_log.info(uuid + '-' + 'hangup cause ' + hangup_cause)
    # self.esl_con.execute('hangup', hangup_cause, uuid)
    # self.ivr_log.debug(uuid + '-' + 'hangup ends')
    # except Exception, e:
    # self.ivr_log.error(uuid + '-' + 'error while hangup:-' + str(e))
    # traceback.print_exc()

    def hangup(self, hangup_cause):
        """

        :param self.esl_con:
        :param hangup_cause:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.info(uuid + '-' + 'hangup cause ' + hangup_cause)
            self.execute('hangup', hangup_cause, uuid, wait=False)
            self.ivr_log.debug(uuid + '-' + 'hangup ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while hangup:-' + str(e))
            traceback.print_exc()

    def wait_for_answer(self):
        """
        :param self.esl_con:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.debug(uuid + '-' + 'waiting for answer')
            self.esl_con.execute('wait_for_answer')
            self.ivr_log.debug(uuid + '-' + 'waiting for answer ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while wait_for_answer:-' + str(e))
            traceback.print_exc()

    def set_audio_level(self, data):
        """

        :param self.esl_con:
        :param data:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.info(uuid + '-' + 'set audio level for with data' + data)
            self.esl_con.execute('set_audio_level', data)
            self.ivr_log.debug(uuid + '-' + 'set audio level ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while set_audio_level:-' + str(e))
            traceback.print_exc()

    def speak(self, engine, voice, text):
        """

        :param self.esl_con:
        :param engine:
        :param voice:
        :param text:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            cmd = engine + "|" + voice + "|" + text
            self.ivr_log.info(uuid + '-' + 'speak with text' + text)
            self.esl_con.execute('set_audio_level', cmd)
            self.ivr_log.debug(uuid + '-' + 'set audio level ends')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while set_audio_level:-' + str(e))
            traceback.print_exc()

    def record(self, path, time_limit, silence_thresh=200, silence_seconds=3):
        """

        :param self.esl_con:
        :param path:
        :param time_limit: seconds
        :param silence_thresh: silence level
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            cmd = "%s %s %s %s" % (path, time_limit, silence_thresh, silence_seconds)
            self.ivr_log.debug(uuid + '-' + 'record')
            self.esl_con.execute('record', cmd)
            self.ivr_log.debug(uuid + '-' + 'record ends')
        except Exception:
            self.ivr_log.exception(uuid + '-' + 'error while record')

    def park(self):
        """

        :param self.esl_con:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.debug(uuid + '-' + 'park')
            self.esl_con.execute('park')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while record:-' + str(e))
            traceback.print_exc()

    def pre_answer(self):
        """

        :param self.esl_con:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            self.ivr_log.debug(uuid + '-' + 'pre_answer')
            self.esl_con.execute('pre_answer')
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while pre_answer:-' + str(e))
            traceback.print_exc()

    def sched_hangup(self, sch_time, cause):
        """

        :param self.esl_con:
        :param sch_time:
        :param cause:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid

            self.ivr_log.debug(uuid + '-' + 'sched_hangup')
            self.esl_con.execute('sched_hangup', "+" + sch_time + " " + cause)
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while sched_hangup:-' + str(e))
            traceback.print_exc()

    def unset(self, data):
        """

        :param self.esl_con:
        :param data:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid

            self.ivr_log.info(uuid + '-' + "unset " + data)
            self.esl_con.execute('unset', data)
            self.ivr_log.debug(uuid + '-' + "unset end")
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while unset:-' + str(e))
            traceback.print_exc()

    def sched_broadcast(self, time, path, leg):
        """

        :param self.esl_con:
        :param time:
        :param path:
        :param leg:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid
            cmd = path + " " + leg
            self.ivr_log.info(uuid + '-' + "sched_broadcast " + leg)

            self.esl_conn.execute('unset', "+" + time + " " + cmd)
            self.ivr_log.debug(uuid + '-' + "sched_broadcast end")
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while sched_broadcast:-' + str(e))
            traceback.print_exc()

    def sleep(self, time):
        """

        :param time:
        :return:
        """
        try:
            assert isinstance(self.esl_con, ESLconnection)
            uuid = self.uuid

            self.ivr_log.info(uuid + '-' + "sleep " + str(time))

            self.esl_con.execute('sleep', time)
            self.ivr_log.debug(uuid + '-' + "sleep ends")
        except Exception, e:
            self.ivr_log.error(uuid + '-' + 'error while sleep:-' + str(e))
            traceback.print_exc()

    def url_request(self, url, payload, req_type="get", headers={'content-type': 'application/json'}):
        """

        :param url: Eg: /abc/def.com
        :param payload: Eg: {"Username":"abc","Password":"pqr", "Message": "Hello", "MobileNo": "9877767656"}// Payload differs from 1 url to another
        :return:
        """
        uuid = self.uuid
        try:

            self.ivr_log.info(uuid + '-' + str(url) + str(payload))
            r = None
            if req_type == "get":
                r = requests.get(url, params=payload)
            else:
                r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
            if r == '' or r is None:
                self.ivr_log.info(uuid + '-' + 'Response is blank or None')
                result = ''
            else:
                self.ivr_log.info(uuid + '-' + str(r.text))
                result = str(r.text)

            return result
        except Exception as e:
            self.ivr_log.error(uuid + '-' + "error while url_request :" + str(e))
            traceback.print_exc()

    def aawaz_obd(self, obd_dict):
        """
        :param obd_dict:
         Eg: {"username":"abc","password":"pqr", "camp_name": "test", "script": "demo.wav",
        "camp_type":"trans", retry_list:{1:5,2:10}, contacts:[987667898,89798687587,7896977908] }
        :return:
        """
        uuid = self.uuid
        try:

            assert obd_dict['script_name'] is not None, "Script name is not present"

            assert obd_dict['api_username'] is not None, "Username is not present"

            assert obd_dict['api_password'] is not None, "Password is not present"

            assert obd_dict['contacts'] is not None, "Contacts are not present"

            self.ivr_log.info(uuid + '-' + str(obd_dict))

            r = obd_call.api_request(obd_dict, self.ivr_log)
            if r == '' or r is None:
                self.ivr_log.info(uuid + '-' + 'Response is blank or None')
                result = ''
            else:
                self.ivr_log.info(uuid + '-' + str(r.text))
                result = str(r.text)

            return result
        except Exception as e:
            self.ivr_log.error(uuid + '-' + "error while aawaz_obd :" + str(e))
            traceback.print_exc()

    def voice360_obd(self, obd_dict):
        """
        :param obd_dict:Eg: {"username": "abc", "password": "pqr", "camp_name": "voice_camp",
                     "destination": "098878677676", "script_id": 1, "retry": 0, "interval": 0}
        :return:
        """
        uuid = self.uuid
        try:

            assert obd_dict['script_id'] is not None, "Script name is not present"

            assert obd_dict['username'] is not None, "Username is not present"

            assert obd_dict['password'] is not None, "Password is not present"

            assert obd_dict['destination'] is not None, "Destinations are not present"

            self.ivr_log.info(uuid + '-' + str(obd_dict))

            r = voice360_call.api_request(obd_dict, self.ivr_log)
            if r == '' or r is None:
                self.ivr_log.info(uuid + '-' + 'Response is blank or None')
                result = ''
            else:
                self.ivr_log.info(uuid + '-' + str(r.text))
                result = str(r.text)

            return result
        except Exception as e:
            self.ivr_log.error(uuid + '-' + "error while voice_obd :" + str(e))
            traceback.print_exc()

    def send_sms(self, sms_dict):
        """
        :param sms_dict: Eg: {'UserName': 'intl_viva', 'password': '933278', "MobileNo": contacts, "SenderID": "test",
                            ,"Message": "Thank your for calling"}
        :return:
        """
        uuid = self.uuid
        try:
            # assert sms_dict['UserName'] is not None, "Username is not present"
            # assert sms_dict['password'] is not None, "Password is not present"
            # assert sms_dict['MobileNo'] is not None, "MobileNo is not present"
            # assert sms_dict['SenderID'] is not None, "SenderID is not present"
            # assert sms_dict['Message'] is not None, "Message is not present"

            is_international = sms_dict.get('is_international', None)
            if is_international:
                url = "http://ihapi.smsapi.org/SendSMS.aspx"
                self.ivr_log.info(uuid + '-' + str(url) + ' ' + str(sms_dict))
            else:
                url = "http://hapi.smsapi.org/SendSMS.aspx"
                self.ivr_log.info(uuid + '-' + str(url) + ' ' + str(sms_dict))

            sms_dict = urllib.urlencode(sms_dict)

            r = requests.get(url, params=sms_dict)
            if r == '' or r is None:
                self.ivr_log.info(uuid + '-' + 'Response is blank or None')
                result = ''
            else:
                self.ivr_log.info(uuid + '-' + str(r.text))
                result = str(r.text)

            return result
        except Exception as e:
            self.ivr_log.error(uuid + '-' + "error while send_sms :" + str(e))
            traceback.print_exc()

    def save_dtmf(self, dtmf_dict):
        uuid = self.uuid
        self.ivr_log.debug(uuid + " : dtmf api request started")
        request_res = self.url_request(ivr_api_url, dtmf_dict, req_type="post")
        self.ivr_log.debug(uuid + " : dtmf api request ended with result : " + str(request_res))
        # mysql_connection = mysql_conn()
        # cursor = mysql_connection.cursor()
        # try:
        #
        # self.ivr_log.info(uuid + '-' + str(dtmf_dict))
        # mongo_database = mongo()
        # result = mongo_database.ivr_dtmf_info.insert(dtmf_dict)
        # self.ivr_log.info(uuid + '-' + str(result))
        # call_uuid = dtmf_dict.get("call_uuid", "")
        # user_id = dtmf_dict.get("user_id", "")
        # dtmf_level = dtmf_dict.get("dtmf_level", "")
        # destination = dtmf_dict.get("destination_no", "")
        # dtmf = dtmf_dict.get("dtmf", 0)
        # dtmf_tag = dtmf_dict.get("dtmf_tag", "")
        # request_id = dtmf_dict.get("request_id", "")
        # script_name = dtmf_dict.get("script_name", "")
        # call_direction = dtmf_dict.get("call_direction", "")
        #     tag_str = ""
        #     tag_len = len(dtmf_tag)
        #     counter = 0
        #     for tag in dtmf_tag:
        #         counter += 1
        #         tag_str += str(tag)
        #         if tag_len > counter:
        #             tag_str += ","
        #
        #     query = "INSERT INTO aawaz.ivr_dtmf_master (call_uuid,user_id,destination,script_name,call_direction,dtmf_level,dtmf,dtmf_tag,request_id) VALUES('" + str(
        #         call_uuid) + "','" + str(user_id) + "','" + str(
        #         destination) + "','" + str(script_name) + "','" + str(call_direction) + "'," + str(
        #         dtmf_level) + ",'" + str(
        #         dtmf) + "','" + str(tag_str) + "','" + str(request_id) + "');"
        #     # print query
        #     cursor.execute(query)
        #     if result is not None:
        #         return True
        #     else:
        #         return False
        # except Exception as e:
        #     self.ivr_log.error(uuid + '-' + "error while save_dtmf :" + str(e))
        #     traceback.print_exc()
        # finally:
        #     pass
        #     cursor.close()
        #     mysql_connection.close()


    def print_headers(self):
        uuid = self.uuid
        try:

            getInfo = self.esl_con.getInfo()
            header = getInfo.firstHeader()
            self.ivr_log.info(uuid + '-' + str(header) + ": " + getInfo.getHeader(header))
            while header:
                header = getInfo.nextHeader()
                self.ivr_log.info(uuid + '-' + str(header) + ": " + getInfo.getHeader(header))
        except Exception as e:
            self.ivr_log.error(uuid + '-' + "error while print_headers :" + str(e))
            traceback.print_exc()


    def get_request_id(self, call_uuid):
        try:
            request_id = None
            self.ivr_log.info("call_uuid: " + str(call_uuid))
            myRedis = redis_connect()

            uuid_key = "call_uuid:" + str(call_uuid)
            request_id = myRedis.hmget(uuid_key, 'request_id')
            if request_id is None:
                mongo_database = mongo_live()
                camp_data = mongo_database.call_destination.find_one({"call_uuid": str(call_uuid)}, {"camp_uuid": 1})
                camp_uuid = camp_data["camp_uuid"]
                camp_key = "aawaz:camp:" + str(camp_uuid)
                request_id = myRedis.hmget(camp_key, 'request_id')
                user_id = myRedis.hmget(camp_key, 'user_id')
                if request_id is None:
                    camp_data = mongo_database.campaign_master.find_one({"camp_uuid": str(camp_uuid)},
                                                                        {"request_id": 1})
                    request_id = camp_data["request_id"]
                else:
                    request_id = request_id[0]
            else:
                request_id = request_id[0]
            self.ivr_log.info("request_id: " + str(request_id))
            return request_id
        except Exception as e:
            self.ivr_log.error(call_uuid + '-' + "error while get_request_id :" + str(e))
            traceback.print_exc()
            return None


    def get_user_id(self, call_uuid):
        try:
            user_id = None
            self.ivr_log.info("call_uuid: " + str(call_uuid))
            myRedis = redis_connect()

            uuid_key = "call_uuid:" + str(call_uuid)
            user_id = myRedis.hmget(uuid_key, 'user_id')
            if user_id is None:
                mongo_database = mongo_live()
                camp_data = mongo_database.call_destination.find_one({"call_uuid": str(call_uuid)}, {"camp_uuid": 1})
                camp_uuid = camp_data["camp_uuid"]
                camp_key = "aawaz:camp:" + str(camp_uuid)
                user_id = myRedis.hmget(camp_key, 'user_id')
                if user_id is None:
                    camp_data = mongo_database.call_destination.find_one({"camp_uuid": str(camp_uuid)}, {"user_id": 1})
                    user_id = camp_data["user_id"]
            self.ivr_log.info("user_id: " + str(user_id))
            return user_id[0]
        except Exception as e:
            self.ivr_log.error(call_uuid + '-' + "error while get_user_id :" + str(e))
            traceback.print_exc()
            return None


    def execute(self, *args, **kwargs):
        self.esl_con.execute(*args)
        if kwargs.pop("wait", True):
            self.wait_for_event('CHANNEL_EXECUTE_COMPLETE')


    def wait_for_event(self, event):
        while self.esl_con.connected():
            e = self.esl_con.recvEvent()
            name = e.getHeader("Event-Name")
            if name == 'CHANNEL_HANGUP':
                raise Exception("The call was disconnected.")
            elif name == event:
                break
