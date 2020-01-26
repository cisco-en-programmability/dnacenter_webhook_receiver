#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests
import urllib3
import sys
import json
import datetime
import os
import time

from flask import Flask, request, abort, send_from_directory
from flask_basicauth import BasicAuth

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings


import webex_teams_apis
import reporting

from config import WEBEX_TEAMS_AUTH, WEBEX_TEAMS_URL, WEBEX_TEAMS_ROOM, WEBEX_BOT_ID
from config import WEBHOOK_USERNAME, WEBHOOK_PASSWORD, WEBHOOK_URL
from config import DNAC_URL
from config import DNAC_ISSUE
from config import PAGERDUTY_EVENTS_URL, PAGERDUTY_INTEGRATION_KEY
from config import JIRA_URL, JIRA_API_KEY, JIRA_EMAIL, JIRA_PROJECT, JIRA_ISSUES

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


def message_handler(teams_message):
    """
    This function will process all the messages addressed to the bot.
    It will:
     - find the Webex Teams message id
     - read the message from teams
     - respond to the message
    :param teams_message: the initial notifications message the bot is informed there is a new message
    :return: status of the message process engine
    """
    # parse and select the message id
    message_id = teams_message['data']['id']
    message_info = webex_teams_apis.get_bot_message_by_id(message_id, WEBEX_BOT_ID)
    print('Teams message content: ' + str(message_info))
    if str.lower(message_info) in ['whatsop help', 'whatsop manage']:  # convert the message to lower case
        post_menu = '<p>I can help you with: <br/><strong>1</strong> or <strong>How many notifications today?</strong>'
        post_menu += '<br/><strong>2</strong> or <strong>How many notifications yesterday?</strong>'
        post_menu += '<br/><strong>3</strong> or <strong>How many notifications last 7 days?</strong>'
        webex_teams_apis.post_room_markdown_message(WEBEX_TEAMS_ROOM, post_menu)
    else:
        if str.lower(message_info) in ['whatsop 1', 'whatsop how many notifications today?']:
            count = reporting.today()
            teams_answer = 'Today we had ' + str(count) + ' notifications'
            print(teams_answer)
            webex_teams_apis.post_room_message(WEBEX_TEAMS_ROOM, teams_answer)
        else:
            if str.lower(message_info) in ['whatsop 2', 'whatsop how many notifications yesterday?']:
                count = reporting.yesterday()
                teams_answer = 'Yesterday we had ' + str(count) + ' notifications'
                print(teams_answer)
                webex_teams_apis.post_room_message(WEBEX_TEAMS_ROOM, teams_answer)
            else:
                if str.lower(message_info) in ['whatsop 3', 'whatsop how many notifications last 7 days?']:
                    count = reporting.last_seven_days()
                    teams_answer = 'Last seven days we had ' + str(count) + ' notifications'
                    print(teams_answer)
                    webex_teams_apis.post_room_message(WEBEX_TEAMS_ROOM, teams_answer)

