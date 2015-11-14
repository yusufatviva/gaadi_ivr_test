__author__ = 'varna'

import traceback
import requests
import json
import datetime
from datetime import date


def api_request(obd_dict, ivr_log):
	try:
		# contacts = "9892629112,9819712705,7208262412"
		start_date = str(date.today())
		end_date = datetime.datetime.now() + datetime.timedelta(days=1)
		end_date = end_date.strftime("%Y-%m-%d")
		start_time = str(datetime.datetime.now().time().strftime("%H:%M"))
		temp_time = datetime.datetime.now() + datetime.timedelta(minutes=20)
		end_time = str(temp_time.time().strftime("%H:%M"))

		try:
			retry = obd_dict['retry']
		except:
			retry = 0

		try:
			interval = obd_dict['interval']
		except:
			interval = 5

		script_id = obd_dict['script_id']
		try:
			campaign_name = obd_dict['camp_name']
		except:
			campaign_name = "api_obd_voice360"
		username = obd_dict['username']
		password = obd_dict['password']

		contacts = obd_dict['destination']
		phonebook_id = obd_dict['phonebook_id']

		post_data = {"username": username, "password": password, "camp_name": campaign_name,
		             "destination": contacts, "start_date": start_date,  "end_date": end_date,
		             "start_time": start_time, "end_time": end_time,
		             "script_id": script_id, "retry": retry, "interval": interval, "phonebook_id":phonebook_id }
		ivr_log.debug(post_data)
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		r = requests.post("http://api.voice360.in/Campaignapi.asmx/setcampaign", post_data, headers=headers)
		ivr_log.debug(r)
		return r

	except Exception as e:
		ivr_log.error("Exception Caught :" + str(e))
		traceback.print_exc()
