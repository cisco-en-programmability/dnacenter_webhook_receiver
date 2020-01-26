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
from datetime import datetime


def today():
    """
    This function will search for all the notifications matching the current date
    :return: number of notifications
    """
    with open('all_webhooks.log', 'r') as filehandle:
        file_lines = filehandle.readlines()
        count = 0
        for line in file_lines:
            line_json = json.loads(line)
            epoch_time = line_json['timestamp']
            timestamp = str(datetime.fromtimestamp(epoch_time / 1000).strftime('%Y-%m-%d'))
            if timestamp == str(datetime.today().date()):
                count += 1
    return count


def yesterday():
    """
    This function will search for all the notifications matching yesterday
    :return: number of notifications
    """
    with open('all_webhooks.log', 'r') as filehandle:
        file_lines = filehandle.readlines()
        count = 0
        for line in file_lines:
            line_json = json.loads(line)
            epoch_time = line_json['timestamp']
            timestamp = str(datetime.fromtimestamp((epoch_time + 86400000) / 1000).strftime('%Y-%m-%d'))  # add the number of msec in a day
            if timestamp == str(datetime.today().date()):
                count += 1
    return count


def last_seven_days():
    """
    This function will search for all the notifications matching last 7 days
    :return: number of notifications
    """
    with open('all_webhooks.log', 'r') as filehandle:
        file_lines = filehandle.readlines()
        count = 0
        for line in file_lines:
            line_json = json.loads(line)
            epoch_time = line_json['timestamp']
            timestamp = str(datetime.fromtimestamp((epoch_time + 7*86400000) / 1000).strftime(
                '%Y-%m-%d'))  # add the number of msec in a day
            if timestamp >= str(datetime.today().date()):
                count += 1
    return count
