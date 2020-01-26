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

import pagerduty_apis
import jira_apis
import webex_teams_apis
import utils
import reporting
import teams_bot

from config import WEBEX_TEAMS_AUTH, WEBEX_TEAMS_URL, WEBEX_TEAMS_ROOM, WEBEX_BOT_ID
from config import WEBHOOK_USERNAME, WEBHOOK_PASSWORD, WEBHOOK_URL
from config import DNAC_URL
from config import DNAC_ISSUE
from config import PAGERDUTY_EVENTS_URL, PAGERDUTY_INTEGRATION_KEY
from config import JIRA_URL, JIRA_API_KEY, JIRA_EMAIL, JIRA_PROJECT, JIRA_ISSUES

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
        if 'NETWORK-' in request_json['eventId']:  # this will select the Cisco DNA Center notifications
            dnac_notification = request_json

            # parse the issue details to variables
            # prepare to save to files -
            # dnac issue summary 'dnac_webhooks.log'
            # all webhooks received summary 'all_webhooks.log'

            severity = str(dnac_notification['severity'])
            category = dnac_notification['category']
            timestamp = str(datetime.datetime.fromtimestamp(int(dnac_notification['timestamp'] / 1000)).strftime(
                '%Y-%m-%d %H:%M:%S'))
            issue_name = dnac_notification['details']['Assurance Issue Name'] + ' - Notification from Cisco DNA Center, PA'
            issue_description = dnac_notification['details']['Assurance Issue Details']
            issue_status = dnac_notification['details']['Assurance Issue Status']
            dnac_issue_url = dnac_notification['ciscoDnaEventLink']
            dedup_key_value = dnac_notification['instanceId']

            # create the summary DNAC log
            new_info = {'severity': severity, 'category': category, 'timestamp': dnac_notification['timestamp']}
            new_info.update({'Assurance Issue Name': issue_name, 'Assurance Issue Details': issue_description})
            new_info.update({'Assurance Issue Status': issue_status, 'Assurance Issue URL': dnac_issue_url})

            # append, or create, the dnac_webhooks.log - Cisco DNA C summary logs
            with open('dnac_webhooks.log', 'a') as filehandle:
                filehandle.write('%s\n' % json.dumps(new_info))

            # append, or create, the all_webhooks.log - Summary all logs
            with open('all_webhooks.log', 'a') as filehandle:
                filehandle.write('%s\n' % json.dumps(new_info))

            # create Jira Issue if status is active
            # to be done - save issue number to assuranceId event, to be re-used for closing the incident

            jira_project = JIRA_PROJECT
            jira_component = '10016'  # Component id for Cisco DNA Center Notification, as created in Jira
            issue_detail = jira_apis.create_customer_issue(jira_project, jira_component, issue_name,
                                                           issue_description, severity,
                                                           JIRA_EMAIL)
            issue_number = issue_detail['key']

            # update the Jira issue with the Cisco DNA Center event url
            jira_issue_update = 'The Cisco DNA Center issue details may be accessed here ' + str(dnac_issue_url)
            jira_apis.update_issue(jira_project, jira_component, issue_number, jira_issue_update)

            # build the Jira Issue url
            jira_issue_url = JIRA_ISSUES + issue_number
            print('Created new ITSM Jira issue: ', issue_number)

            # create PagerDuty incident if status is 'active' or 'resolved'
            # no action for status ignore'
            # format message using the Common Event Format (PD-CEF)
            if issue_status == 'active' or issue_status == 'resolved':

                # Arrays to be used to translate Cisco DNA Center severity values to PagerDuty values
                severity_dict = {'1': 'critical', '2': 'error', '3': 'info'}

                # The 'ignore' action will trigger a new PagerDuty alert
                event_action_dict = {'active': 'trigger', 'resolved': 'resolve', 'ignore': 'acknowledge'}

                # create the new PagerDuty alert action
                event_action = event_action_dict[issue_status]

                # create the new PagerDuty alert severity
                sev = severity_dict[severity]

                summary = 'Jira Issue Number: ' + issue_number + ', ' + issue_name
                source = 'Cisco DNA Center Notification'
                component = issue_description
                group = 'Network'

                # convert time from epoch to iso 8601
                time_iso = datetime.datetime.fromtimestamp(int(dnac_notification['timestamp'] / 1000)).isoformat()

                # create PagerDuty links, list, sample format [{'href': 'https://example.com/', 'text': 'Link text'}]
                pagerduty_links = [{'href': jira_issue_url, 'text': ('ITSM Jira Issue Number ' + issue_number + ' Details')},
                                   {'href': dnac_issue_url, 'text': 'Cisco DNA Center Issue Details'}]

                pagerduty_dedup_key = pagerduty_apis.trigger_incident(summary, source, event_action, dedup_key_value,
                                                                      component, sev, time_iso, group, pagerduty_links)

            # construct the Webex Teams message
            # add url's for Jira Incident # and Cisco DNA Center Issue

            teams_message = '<p><strong>Cisco DNA Center Notification</strong>'
            teams_message += '<br/>Severity:       ' + severity
            teams_message += '<br/>Category:       ' + category
            teams_message += '<br/>Timestamp:      ' + str(timestamp)
            teams_message += '<br/>Issue Name:     ' + issue_name
            teams_message += '<br/>Issue Description:  ' + issue_description
            teams_message += '<br/>Issue Status:   ' + issue_status

            # add url for Jira incident issue
            teams_message += '<br/>ITSM: Jira Issue Number: ' + issue_number + ' [Details](' + jira_issue_url + ')'

            # add url for the Cisco DNAC issue
            teams_message += '<br/>Cisco DNA Center Issue ' + ' [Details](' + dnac_issue_url + ')'

            # post message in teams space
            print('New DNAC Webex Teams_Message\n', str(teams_message))
            webex_teams_apis.post_room_markdown_message(WEBEX_TEAMS_ROOM, teams_message)

            print('Webex Teams notification message posted')
        return 'Notification Received', 201
    else:
        return 'POST Method not supported', 404


@app.route('/teams', methods=['POST'])  # create a route for /Teams, method POST, to receive webhooks from teams
def teams_webhook():
    if request.method == 'POST':
        print('Teams Webhook Received')
        webhook_json = request.json

        # print the received notification
        print('Payload: ')
        print(webhook_json)

        # save as a file, create new file if not existing, append to existing file, full details of each notification
        with open('all_teams_detailed.log', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(webhook_json))

        # send the message to the bot function
        status = teams_bot.message_handler(webhook_json)
        return 'Webhook Received', 201
    else:
        return 'POST Method not supported', 404


@app.route('/ios')  # create a page for the ios automation
@basic_auth.required
def ios():
    return 'IOS decorator tested OK', 200


@app.route('/ios/today')  # create a page for ios automation/today
@basic_auth.required
def today():
    count = reporting.today()
    teams_answer = 'Today we had ' + str(count) + ' notifications'
    return teams_answer, 200


if __name__ == '__main__':
    app.run(debug=True)
