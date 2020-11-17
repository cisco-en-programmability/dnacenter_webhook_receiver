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

import requests
import json
import urllib3

from requests.auth import HTTPBasicAuth  # for Basic Auth

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

from config import WEBHOOK_URL, WEBHOOK_USERNAME, WEBHOOK_PASSWORD


# set the payload for a Cisco DNA Center new event notification

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

# set the payload for a Cisco DNA Center resolved event notification

dnac_param_resolved = {
    "version": "",
    "instanceId": "4292b3bc-a8a7-4a2e-8349-ddfae1ea8b9e",
    "eventId": "NETWORK-NON-FABRIC_WIRED-1-251",
    "namespace": "",
    "name": "",
    "description": "",
    "type": "NETWORK",
    "category": "ALERT",
    "domain": "Connectivity",
    "subDomain": "Non-Fabric Wired",
    "severity": 1,
    "source": "Cisco DNA Assurance",
    "timestamp": 1576122993751,
    "tags": "",
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
    "context": "",
    "tenantId": ""
}


# test the Webhook with a Cisco DNA Center sample notification

basic_auth = HTTPBasicAuth(WEBHOOK_USERNAME, WEBHOOK_PASSWORD)

url = WEBHOOK_URL
header = {'content-type': 'application/json'}
response = requests.post(url, auth=basic_auth, data=json.dumps(dnac_param), headers=header, verify=False)
print('\nWebhook notification status code: ', response.status_code)
print('\nWebhook notification response: ', response.text)
