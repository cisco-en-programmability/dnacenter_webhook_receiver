#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2020 Cisco and/or its affiliates.

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
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import urllib3
import json
import os
import time


from flask import Flask, request, abort, send_from_directory
from flask_basicauth import BasicAuth

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings


os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

from config import WEBHOOK_URL, WEBHOOK_USERNAME, WEBHOOK_PASSWORD


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)


@app.route('/')  # create a page for testing the flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/webhook', methods=['POST'])  # create a route for /webhook, method POST
@basic_auth.required
def webhook():
    if request.method == 'POST':
        print('Webhook Received')
        request_json = request.json

        # print the received notification
        print('Payload: ')
        print(request_json)

        # save as a file, create new file if not existing, append to existing file
        # full details of each notification to file 'all_webhooks_detailed.json'

        with open('all_webhooks_detailed.json', 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(request_json))

        # steps required by the notification
        notification = request_json

        return 'Webhook notification received', 202
    else:
        return 'POST Method not supported', 405


if __name__ == '__main__':
    app.run(debug=True)
