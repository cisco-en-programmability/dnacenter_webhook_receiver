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

import json
import requests

from config import PAGERDUTY_INTEGRATION_KEY
integration_key = PAGERDUTY_INTEGRATION_KEY

dnac_basicauth = "Basic YWRtaW46Q2lzY28xMjM="

event_body_json = {
    "version": "",
    "instanceId": "84bc5a0d-b211-4c50-81e0-a142da540d45",
    "eventId": "NETWORK-NON-FABRIC_WIRED-1-200",
    "namespace": "ASSURANCE",
    "name": "",
    "description": "",
    "type": "NETWORK",
    "category": "ALERT",
    "domain": "Connectivity",
    "subDomain": "Non-Fabric Wired",
    "severity": 1,
    "source": "ndp",
    "timestamp": 1569449708000,
    "tags": "",
    "details": {
        "Type": "Network Device",
        "Assurance Issue Details": "This network device PDX-3850-CAMPUS is unreachable from controller. The device role is ACCESS",
        "Assurance Issue Priority": "P1",
        "Device": "10.93.130.47",
        "Assurance Issue Name": "Network Device 10.93.130.47 Is Unreachable From Controller",
        "Assurance Issue Category": "Availability",
        "Assurance Issue Status": "active"},
    "ciscoDnaEventLink": "dna/assurance/issueDetails?issueId=84bc5a0d-b211-4c50-81e0-a142da540d45",
    "note": "To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "tntId": "",
    "context": "",
    "tenantId": ""}


dnac_resolved = {
    "version":"",
    "instanceId":"2beaafc5-433b-4f6a-94af-173dbdbb9f49",
    "eventId":"NETWORK-NON-FABRIC_WIRED-1-251",
    "namespace":"",
    "name":"",
    "description":"",
    "type":"NETWORK",
    "category":"ALERT",
    "domain":"Connectivity",
    "subDomain":"Non-Fabric Wired",
    "severity":1,
    "source":"Cisco DNA Assurance",
    "timestamp":1574464662637,
    "tags":"",
    "details":{
        "Type":"Network Device",
        "Assurance Issue Priority":"P1",
        "Assurance Issue Details":"Interface GigabitEthernet0/0 on the following network device is down: Local Node: PDX-ACCESS",
        "Device":"10.93.141.20",
        "Assurance Issue Name":"Interface GigabitEthernet0/0 is Down on Network Device 10.93.141.20",
        "Assurance Issue Category":"Connectivity",
        "Assurance Issue Status":"resolved"
    },
    "ciscoDnaEventLink":"https://10.93.141.35/dna/assurance/issueDetails?issueId=2beaafc5-433b-4f6a-94af-173dbdbb9f49",
    "note":"To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "tntId":"",
    "context":"",
    "tenantId":""
}


event_body = __getInputParameterValueByName("body")
event_body_json = json.loads(event_body)


# This section will format a PagerDuty notification using the Common Event Format (PD-CEF):

# summary:    A high-level, text summary message of the event. Will be used to construct an alert"s description
# source:     Specific human-readable unique identifier, such as a hostname, for the system having the problem
# event_action: action PagerDuty will take, enum {'trigger', 'resolve', 'acknowledge'}
# dedup_key:  pre-defined PagerDuty Alert id, submit the same to resolve issue
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

# Arrays to be used to translate Cisco DNA Center severity values to PagerDuty values
severity_dict = {"1": "critical", "2": "error", "3": "info"}

# The "ignore" action will trigger a new PagerDuty alert
event_action_dict = {"active": "trigger", "resolved": "resolve", "ignore": "trigger"}

# create the new PagerDuty alert action
notification_action = event_body_json["details"]["Assurance Issue Status"]
event_action = event_action_dict[notification_action]

# create the new PagerDuty alert severity
notification_severity = str(event_body_json["severity"])
event_severity = severity_dict[notification_severity]

# define the PagerDuty dedup_key == Assurance Instance Id. When the event will be resolved in Cisco DNA Center,
# it will send a notification to PagerDuty to resolve the alert
dedup_key = event_body_json["instanceId"]

# base url for DNA Center to construct the Assurance issue link
# has to be pre-configured in Cisco DNA Center: Systems Settings --> Settings --> Integration Settings

# create the PagerDuty links
event_link = [{"href": event_body_json["ciscoDnaEventLink"], "text": "Cisco DNA Center Issue Details"}]

# create the PagerDuty payload
pagerduty_request = {
    "routing_key": __getInputParameterValueByName("integration_key"),
    "event_action": event_action,
    "dedup_key": dedup_key,
    "payload": {
        "summary": event_body_json["details"]["Assurance Issue Details"],
        "source": "Cisco DNA Center " + event_body_json["namespace"],
        "component": event_body_json["details"]["Assurance Issue Name"],
        "severity": event_severity,
        "timestamp": event_body_json["timestamp"],
        "group": event_body_json["type"]
    },
    "links": event_link
}

event_request_str = json.dumps(pagerduty_request)

__setOutputParameterValueByName("pager_duty_req_body", event_request_str)