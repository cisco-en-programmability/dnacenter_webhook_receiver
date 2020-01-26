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
import utils

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

from config import WEBEX_TEAMS_URL, WEBEX_TEAMS_AUTH, WEBEX_TEAMS_ROOM, WEBEX_BOT_ID

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


def get_room_id(room_name):
    """
    This function will find the Webex Teams space id based on the {space_name}
    Call to Webex Teams - /rooms
    :param room_name: The Webex Teams room name
    :return: the Webex Teams room Id
    """
    room_id = None
    url = WEBEX_TEAMS_URL + '/rooms' + '?max=1000'
    header = {'content-type': 'application/json', 'authorization': WEBEX_TEAMS_AUTH}
    space_response = requests.get(url, headers=header, verify=False)
    space_list_json = space_response.json()
    space_list = space_list_json['items']
    for spaces in space_list:
        if spaces['title'] == room_name:
            room_id = spaces['id']
    return room_id


def post_room_message(space_name, message):
    """
    This function will post the {message} to the Webex Teams space with the {space_name}
    Call to function get_space_id(space_name) to find the space_id
    Followed by API call /messages
    :param space_name: the Webex Teams space name
    :param message: the text of the message to be posted in the space
    :return: none
    """
    space_id = get_room_id(space_name)
    payload = {'roomId': space_id, 'text': message}
    url = WEBEX_TEAMS_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_TEAMS_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def post_room_markdown_message(space_name, message):
    """
    This function will post a markdown {message} to the Webex Teams space with the {space_name}
    Call to function get_space_id(space_name) to find the space_id
    Followed by API call /messages
    :param space_name: the Webex Teams space name
    :param message: the text of the markdown message to be posted in the space
    :return: none
    """
    space_id = get_room_id(space_name)
    payload = {'roomId': space_id, 'markdown': message}
    url = WEBEX_TEAMS_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_TEAMS_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def post_room_url_message(space_name, message, url):
    """
    This function will post an URL to the Webex Teams space with the {space_name}
    Call to function get_space_id(space_name) to find the space_id
    Followed by API call /messages
    :param space_name: the Webex Teams space name
    :param message: the text of the markdown message to be posted in the space
    :param url: URL for the text message
    :return: none
    """
    space_id = get_room_id(space_name)
    payload = {'roomId': space_id, 'markdown': ('[' + message + '](' + url + ')')}
    url = WEBEX_TEAMS_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_TEAMS_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def get_bot_message_by_id(message_id, bot_id):
    """
    This function will get the message content using the {message_id}
    :param message_id: Webex Teams message_id
    :param bot_id: the Bot id to validate message
    :return: message content
    """
    url = WEBEX_TEAMS_URL + '/messages/' + message_id
    header = {'content-type': 'application/json', 'authorization': WEBEX_TEAMS_AUTH}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    all_people = response_json['mentionedPeople']
    for people in all_people:
        if people == bot_id:
            return response_json['text']
    return None

