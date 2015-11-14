__author__ = 'ashish'

import requests
import json
import datetime
from datetime import date
import traceback
from config import *


def api_request(obd_dict, ivr_log):
    try:
        # contacts = "9892629112,9819712705,7208262412"
        start_date = str(date.today())
        end_date = start_date
        start_time = "00:00"
        temp_time = datetime.datetime.now() + datetime.timedelta(minutes=20)
        end_time = "23:59"

        retry_list = obd_dict.get('retry', {})

        script = obd_dict['script_name']

        campaign_name = obd_dict.get('camp_name', "api_obd")

        username = obd_dict['api_username']
        password = obd_dict['api_password']

        camp_type = obd_dict.get('trans_type', "trans")

        # is_international = obd_dict.get('is_international', False)

        contacts = obd_dict['contacts']
        post_data = {"contacts": contacts, "start_date": start_date, "camp_name": campaign_name,
                     "retry": json.dumps(retry_list), "end_date": end_date,
                     "api_username": username, "api_password": password, "script_name": script,
                     "start_time": start_time,
                     "end_time": end_time,
                     "trans_type": camp_type, "camp_subscription": "FB"}

        ivr_log.debug(post_data)

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        r = requests.post(aawaz_api_url, post_data, headers=headers)
        ivr_log.info(r)
        return r
    except Exception as e:
        print str(e)
        ivr_log.error("Exception Caught :" + str(e))
        traceback.print_exc()


        # obd_dict =  {'end_date': '2014-12-17', 'start_time': '11:00', 'api_username': 'nowahala',
        # 'api_password': 'viva123', 'script_name': 'Nigeria_VOIP', 'retry': '{}', 'contacts': '+919819712705',
        # 'camp_name': 'api_obd', 'end_time': '11:55', 'trans_type': 'trans', 'start_date': '2014-12-16', "is_international": 'True'}
        # api_request(obd_dict)