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
import reporting

from flask import Flask, request, abort, send_from_directory
from flask_basicauth import BasicAuth

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

import webex_teams_apis
import utils
import reporting
import teams_bot

from config import WEBEX_TEAMS_AUTH, WEBEX_TEAMS_URL, WEBEX_TEAMS_ROOM, WEBEX_BOT_ID
from config import WEBHOOK_USERNAME, WEBHOOK_PASSWORD, WEBHOOK_URL
from config import DNAC_URL


os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)


@app.route('/')  # create a page for testing the flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/detailed_logs', methods=['GET'])  # create a return detailed logs file
@basic_auth.required
def detailed_logs():
    print('File all_webhooks_detailed.log requested, transfer started')
    return send_from_directory('', 'all_webhooks_detailed.log', as_attachment=True)


@app.route('/webhook', methods=['POST'])  # create a route for /webhook, method POST
@basic_auth.required
def webhook():
    if request.method == 'POST':
        print('Cisco DNA Center Webhook Received')
        request_json = request.json

        # print the received notification
        print('Payload: ')
        print(request_json)

        # save as a file, create new file if not existing, append to existing file
        # full details of each notification to file 'all_webhooks_detailed.log'

        with open('all_webhooks_detailed.log', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(request_json))
        dnac_notification = request_json

        # parse the issue details to variables
        # prepare to save to files:
        #  - dnac issue summary 'dnac_webhooks.log'
        #  - all webhooks received summary 'all_webhooks.log'

        severity = str(dnac_notification['severity'])
        category = dnac_notification['category']

        # convert timestamp from epoch time to Cisco DNA Center timezone time
        timestamp = str(datetime.datetime.fromtimestamp(int(dnac_notification['timestamp'] / 1000)).strftime(
            '%Y-%m-%d %H:%M:%S'))

        issue_name = dnac_notification['details']['Assurance Issue Name'] + ' - Notification from Cisco DNA Center, PA'
        issue_description = dnac_notification['details']['Assurance Issue Details']
        issue_status = dnac_notification['details']['Assurance Issue Status']
        dnac_issue_url = dnac_notification['ciscoDnaEventLink']

        # create the summary Cisco DNA Center log
        new_info = {'severity': severity, 'category': category, 'timestamp': dnac_notification['timestamp']}
        new_info.update({'Assurance Issue Name': issue_name, 'Assurance Issue Details': issue_description})
        new_info.update({'Assurance Issue Status': issue_status, 'Assurance Issue URL': dnac_issue_url})

        # append, or create, the dnac_webhooks.log - Cisco DNA C summary logs
        with open('dnac_webhooks.log', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(new_info))

        # append, or create, the all_webhooks.log - Summary all logs
        with open('all_webhooks.log', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(new_info))

        # construct the Webex Teams message

        # use this section for Webex Teams Markdown messages
        '''
        teams_message = '<p><strong>Cisco DNA Center Notification</strong>'
        teams_message += '<br/>Severity:       ' + severity
        teams_message += '<br/>Category:       ' + category
        teams_message += '<br/>Timestamp:      ' + str(timestamp)
        teams_message += '<br/>Issue Name:     ' + issue_name
        teams_message += '<br/>Issue Description:  ' + issue_description
        teams_message += '<br/>Issue Status:   ' + issue_status

        # add url for the Cisco DNAC issue
        teams_message += '<br/>Cisco DNA Center Issue ' + ' [Details](' + dnac_issue_url + ')'

        # post message in teams space
        print('New DNAC Webex Teams_Message\n', str(teams_message))
        webex_teams_apis.post_room_markdown_message(WEBEX_TEAMS_ROOM, teams_message)

        print('Webex Teams notification message posted')
        '''

        # use this section for Webex Teams Adaptive Cards messages

        # create the cards payload
        space_id = webex_teams_apis.get_room_id(WEBEX_TEAMS_ROOM)

        card_message = {
            "roomId": space_id,
            "markdown": "Cisco DNA Center Notification",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Cisco DNA Center Notification",
                                "weight": "bolder",
                                "size": "large"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Severity:",
                                        "value": severity
                                    },
                                    {
                                        "title": "Category:",
                                        "value": category
                                    },
                                    {
                                        "title": "Timestamp:",
                                        "value": str(timestamp)
                                    },
                                    {
                                        "title": "Issue Name:",
                                        "value": issue_name
                                    },
                                    {
                                        "title": "Issue Description:",
                                        "value": issue_description
                                    },
                                    {
                                        "title": "Issue Status:",
                                        "value": issue_status
                                    }
                                ]
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.openURL",
                                "title": "Cisco DNA Center Issue Details",
                                "url": dnac_issue_url
                            }
                        ]
                    }
                }
            ]
        }
        # post message in teams space
        print('New DNAC Webex Teams_Message\n', str(card_message))

        webex_teams_apis.post_room_card_message(WEBEX_TEAMS_ROOM, card_message)
        print('Webex Teams notification message posted')

        return 'Notification Received', 201
    else:
        return 'POST Method not supported', 404


if __name__ == '__main__':
    app.run(debug=True)
