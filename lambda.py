# imports
import json
import sys
import random
import requests
import logging
from datetime import datetime


#from urllib2 import Request, urlopen, URLError, HTTPError
# Read all the environment variables
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxxxxxxxx"
SLACK_USER = "Suzan"
SLACK_CHANNEL = "lambda-slack"
# logging related code
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# byte to readable
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
    
# Lambda method
def lambda_handler(event, context):
  if event['Records'][0]['s3']['object']['size'] > 1000000000:
    logger.info("Event: " + str(event))
    message = {
        "eventTime": datetime.strptime(event['Records'][0]['eventTime'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S"),
        "eventName": event['Records'][0]['eventName'],
        "bucket": event['Records'][0]['s3']['bucket']['name'],
        "object": event['Records'][0]['s3']['object']['key'],
        "size": sizeof_fmt(event['Records'][0]['s3']['object']['size'])
    }
    logger.info(message['eventTime'])
    url = SLACK_WEBHOOK_URL
    title = (f"New Incoming Message :zap: ")
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
        "channel" : SLACK_CHANNEL,
        "blocks": [
        {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": str(title)
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*File has been uploaded* "
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Date:* % s" % str(message['eventTime'])
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Bucket:* % s" % str(message['bucket'])
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*File:* % s" % str(message['object'])
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*File Size:* % s" % message['size']
				}
			]
		}
	]
    }

    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
