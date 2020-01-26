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
import ncclient
import xml
import xml.dom.minidom
import json
import lxml.etree as et
import xmltodict
import time
from ncclient.operations import RPCError
import netconf_restconf
import dnac_apis
import utils

from ncclient import manager

from config import DNAC_URL, DNAC_USER, DNAC_PASS

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

"""
This script will:
- ask user to enter interface number
- validate the interface is in the range 1/0/2-5
- disable interface
- wait 15 seconds
- enable interface
- re-sync the PDX-M switch
"""

host_ip = '10.93.141.1'
hostname = 'PDX-M'
username = 'cisco'
password = 'cisco'

dnac_auth = HTTPBasicAuth(DNAC_USER, DNAC_PASS)

while True:
    interface_number = int(input('Enter the interface number (range 2-5): '))
    if 2 <= interface_number <= 5:
        disable_message = 'Interface GigabitEthernet1/0/' + str(interface_number) + ' disable request: '
        disable_message += netconf_restconf.netconf_oper_admin_interface('GigabitEthernet1/0/' + str(interface_number), 'false', host_ip, 830, username, password)
        print('\n', disable_message)

        # wait for event to be created
        utils.time_sleep(15)

        enable_message = 'Interface GigabitEthernet1/0/' + str(interface_number) + ' enable request: '
        enable_message += netconf_restconf.netconf_oper_admin_interface('GigabitEthernet1/0/' + str(interface_number), 'true', host_ip, 830, username, password)
        print('\n\n', enable_message)

        # start the Cisco DNA Center device re-sync
        dnac_token = dnac_apis.get_dnac_jwt_token(dnac_auth)

        sync_status = dnac_apis.sync_device(hostname, dnac_token)
        print('\nDevice sync started: ', sync_status)

        break

