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
import json
import urllib3
import utils

from requests.auth import HTTPBasicAuth  # for Basic Auth
from config import WEBHOOK_URL, WEBHOOK_USERNAME, WEBHOOK_PASSWORD

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

basic_auth = HTTPBasicAuth(WEBHOOK_USERNAME, WEBHOOK_PASSWORD)

dnac_param = {
    "version": "",
    "instanceId": "ea6e28c5-b7f2-43a4-9937-def73771c5ef",
    "eventId": "NETWORK-NON-FABRIC_WIRED-1-251",
    "namespace": "ASSURANCE",
    "name": "",
    "description": "",
    "type": "NETWORK",
    "category": "ALERT",
    "domain": "Connectivity",
    "subDomain": "Non-Fabric Wired",
    "severity": 1,
    "source": "ndp",
    "timestamp": 1574457834497,
    "tags": "",
    "details": {
        "Type": "Network Device",
        "Assurance Issue Priority": "P1",
        "Assurance Issue Details": "Interface GigabitEthernet1/0/3 on the following network device is down: Local Node: PDX-M",
        "Device": "10.93.141.17",
        "Assurance Issue Name": "Interface GigabitEthernet1/0/3 is Down on Network Device 10.93.141.17",
        "Assurance Issue Category": "Connectivity",
        "Assurance Issue Status": "active"
    },
    "ciscoDnaEventLink": "https://10.93.141.35/dna/assurance/issueDetails?issueId=ea6e28c5-b7f2-43a4-9937-def73771c5ef",
    "note": "To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "tntId": "",
    "context": "",
    "tenantId": ""
}


dnac_param_resolved = {
    "version": null,
    "instanceId": "4292b3bc-a8a7-4a2e-8349-ddfae1ea8b9e",
    "eventId": "NETWORK-NON-FABRIC_WIRED-1-251",
    "namespace": null,
    "name": null,
    "description": null,
    "type": "NETWORK",
    "category": "ALERT",
    "domain": "Connectivity",
    "subDomain": "Non-Fabric Wired",
    "severity": 1,
    "source": "Cisco DNA Assurance",
    "timestamp": 1576122993751,
    "tags": null,
    "details": {
      "Type": "Network Device",
      "Assurance Issue Priority": "P1",
      "Assurance Issue Details": "Interface GigabitEthernet0/0 on the following network device is down: Local Node: PDX-CORE2",
      "Device": "10.93.141.3",
      "Assurance Issue Name": "Interface GigabitEthernet0/0 is Down on Network Device 10.93.141.3",
      "Assurance Issue Category": "Connectivity",
      "Assurance Issue Status": "resolved"
    },
    "ciscoDnaEventLink": "https://10.93.141.35/dna/assurance/issueDetails?issueId=4292b3bc-a8a7-4a2e-8349-ddfae1ea8b9e",
    "note": "To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "tntId": "",
    "context": null,
    "tenantId": ""
}


sd_wan_param = {
    "devices": [
        {
            "system-ip": "21.21.21.21"
        }
    ],
    "eventname": "interface-admin-state-change",
    "type": "interface-admin-state-change",
    "rulename": "interface-admin-state-change",
    "component": "VPN",
    "entry_time": 1574274686000,
    "statcycletime": 1574274686000,
    "message": "The interface admin-state changed to down",
    "severity": "Critical",
    "severity_number": 1,
    "uuid": "303af097-12ca-4aa2-b1e8-544094a7c96d",
    "values": [
        {
            "host-name": "vBond-Pod5",
            "system-ip": "21.21.21.21",
            "if-name": "eth0",
            "new-admin-state": "down",
            "vpn-id": "512"
        }
    ],
    "rule_name_display": "Interface_Admin_State_Change",
    "receive_time": 1574274686635,
    "values_short_display": [
        {
            "host-name": "vBond-Pod5",
            "system-ip": "21.21.21.21",
            "if-name": "eth0",
            "new-admin-state": "down"
        }
    ],
    "acknowledged": False,
    "active": True
}


url = 'http://127.0.0.1:5000/webhook'  # to test the Flask Web App running local
header = {'content-type': 'application/json'}
response = requests.post(url, auth=basic_auth, data=json.dumps(dnac_param), headers=header, verify=False)
response_json = response.json()
print(response_json)


# test the Webhook with a Cisco DNA Center notification

url = WEBHOOK_URL
header = {'content-type': 'application/json'}
response = requests.post(url, auth=basic_auth, data=json.dumps(dnac_param), headers=header, verify=False)
response_json = response.json()
print('\n', response_json)


# print the HTTP BasicAuth encoding - needed for Cisco DNA Center webhook configuration
# print('\nThe HTTP Basic Auth you will need for the Webhooks Configuration is:\n' + response.request.headers['Authorization'])


