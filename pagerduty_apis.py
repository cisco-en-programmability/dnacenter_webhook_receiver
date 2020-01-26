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
import json

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

from config import PAGERDUTY_INTEGRATION_KEY, PAGERDUTY_EVENTS_URL

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


def trigger_incident(summary, source, event_action, dedup_key, component, severity, timestamp, group, links):
    """
    This function will send a PagerDuty notification using the Common Event Format (PD-CEF)
    :param summary: A high-level, text summary message of the event. Will be used to construct an alert's description
    :param source: Specific human-readable unique identifier, such as a hostname, for the system having the problem
    :param event_action: action PagerDuty will take, enum {'trigger', 'resolve', 'acknowledge'}
    :param dedup_key: pre-defined PagerDuty alert id, submit the same to resolve issue
    :param component: The part or component of the affected system that is broken.
    :param severity: must be one of: Info, Warning, Error, Critical.
     How impacted the affected system is. Displayed to users in lists and influences the priority of any created incidents
    :param timestamp: IOS 8601 timestamp
    :param group: A cluster or grouping of sources. For example, {Network} or {WAN}
    :param links: list of links required for rich incident info,  sample format:
                    [{"href": "https://example.com/", "text": "Link text"}]
    :return:
    """
    # This section will format a PagerDuty notification using the Common Event Format (PD-CEF):

    # summary:    A high-level, text summary message of the event. Will be used to construct an alert"s description
    # source:     Specific human-readable unique identifier, such as a hostname, for the system having the problem
    # event_action: action PagerDuty will take, enum {'trigger', 'resolve', 'acknowledge'}
    # dedup_key:  pre-defined PagerDuty alert id, submit the same to resolve issue
    # component:  The part or component of the affected system that is broken.
    # severity:  must be one of: Info, Warning, Error, Critical.
    #           How impacted the affected system is.
    #           Displayed to users in lists and influences the priority of any created incidents.
    # timestamp:  IOS 8601 timestamp
    # group:      A cluster or grouping of sources. For example, {Network} or {WAN}
    # links:      list of links required for rich incident info,  sample format:
    #                [{"href": "https://example.com/", "text": "Link text"}]

    # Triggers a PagerDuty incident with a previously generated incident key
    # Uses Events V2 API - documentation: https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2
    # format message using the Common Event Format (PD-CEF)

    # Payload is built with the main important parameters required to trigger an incident, more options are supported by PagerDuty

    payload = {
        'routing_key': PAGERDUTY_INTEGRATION_KEY,
        'event_action': event_action,
        'dedup_key': dedup_key,
        'links': links,
        'payload': {
            'summary': summary,
            'source': source,
            'component': component,
            'severity': severity,
            'timestamp': timestamp,
            'group': group
        }
    }

    url = PAGERDUTY_EVENTS_URL
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=header)
    response_json = response.json()

    # print the PagerDuty payload
    print('PagerDuty payload: \n', payload)

    if response_json['status'] == 'success':
        dedup_key = response_json['dedup_key']
        print('Incident created with with dedup key (also known as incident / alert key) of ' + '"' + dedup_key + '"')
        return dedup_key
    else:
        print(response.text)  # print error message if not successful
        return "PagerDuty Error"
