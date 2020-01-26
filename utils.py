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


# the utils module includes common utilized utility functions

import json
import os
import os.path
import time
import re  # needed for regular expressions matching
import select
import socket  # needed for IPv4 validation
import sys
import urllib3
import subprocess  # needed for the ping function
import ipaddress  # needed for IPv4 address validation
import datetime  # needed for epoch time conversion

from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_input_ip():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    ip_address = input('Input the IP address to be validated, (or q to exit) ?  ')
    return ip_address


def get_input_mac():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    mac_address = input('Input the MAC address to be validated, (or q to exit) ?  ')
    return mac_address


def get_input_timeout(message, wait_time):
    """
    This function will ask the user to input the value requested in the {message}, in the time specified {time}
    :param message: message to provide the user information on what is required
    :param wait_time: time limit for the user input
    :return: user input as string
    """

    print(message + ' in ' + str(wait_time) + ' seconds')
    i, o, e = select.select([sys.stdin], [], [], wait_time)
    if i:
        input_value = sys.stdin.readline().strip()
        print('User input: ', input_value)
    else:
        input_value = None
        print('No user input in ', wait_time, ' seconds')
    return input_value


def validate_ipv4_address(ipv4_address):
    """
    This function will validate if the provided string is a valid IPv4 address
    :param ipv4_address: string with the IPv4 address
    :return: true/false
    """
    try:
        ipaddress.ip_address(ipv4_address)
        return True
    except:
        return False


def identify_ipv4_address(configuration):
    """
    This function will return a list of all valid IPv4 addresses part of the { ip address x.x.x.x} CLI commands
    from the string {configuration}
    :param configuration: string with the configuration (single or muliple lines)
    Sample string '!\ninterface Loopback65\n ip address 10.93.130.21 255.255.255.255\n!'
    :return: list of IPv4 addresses
    """
    ipv4_list = []
    pattern = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    split_lines = configuration.split('\n')  # split configuration file in individual commands'
    for line in split_lines:
        if 'ip address' in line:  # check if command includes the string 'ip address'
            split_config = line.split(' ')  # split the command in words
            try:
                split_config.remove('')  # remove the first ' ' if existing in the command
            except:
                pass
            line_begins = split_config[0:3]  # select the three items in the list
            for word in line_begins:
                check_ip = pattern.match(word)  # match each word with the pattern from regex
                if check_ip:
                    if validate_ipv4_address(word):  # validate if the octets are valid IP addresses
                        ipv4_list.append(word)
    return ipv4_list


def ping_return(hostname):
    """
    Use the ping utility to attempt to reach the host by using a hostname or IPv4 address
    We send 5 packets ('-c 5') and wait 1 second ('-W 1000') for a response. The function
    returns the return code from the ping utility.
    It will also save the output to the file {ping_hostname}
    :param hostname: hostname or the IPv4 address of the device to ping
    :return status - enum {'Success', 'Failed', 'Unknown'}
    """
    ret_code = subprocess.call(['ping', '-c', '5', '-W', '1000', hostname], stdout=open('ping_' + hostname, 'w'))
    if ret_code == 0:
        return_code = 'Success'
    elif ret_code == 2:
        return_code = 'Failed'
    else:
        return_code = 'Unknown'
    return return_code


def get_epoch_current_time():
    """
    This function will return the epoch time for the {timestamp}, UTC time format, for current time
    :return: epoch time including msec
    """
    epoch = time.time()*1000
    return int(epoch)


def time_sleep(time_sec):
    """
    This function will wait for the specified time_sec, while printing a progress bar, one '!' / second
    Sample Output :
    Wait for 10 seconds
    !!!!!!!!!!
    :param time_sec: time, in seconds
    :return: none
    """
    print('\nWait for ' + str(time_sec) + ' seconds')
    for i in range(time_sec):
        print('!', end='')
        time.sleep(1)
    return

