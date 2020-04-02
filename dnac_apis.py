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
import time
import urllib3
import utils

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth

from config import DNAC_URL, DNAC_PASS, DNAC_USER, DNAC_IP

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data: data to pretty print
    :return:
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_dnac_jwt_token(dnac_auth):
    """
    Create the authorization token required to access DNA C
    Call to Cisco DNA Center - /api/system/v1/auth/login
    :param dnac_auth - Cisco DNA Center Basic Auth string
    :return: Cisco DNA Center JWT token
    """

    url = DNAC_URL + '/dna/system/api/v1/auth/token'
    header = {'content-type': 'application/json'}
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    dnac_jwt_token = response.json()['Token']
    return dnac_jwt_token


def get_device_info(device_id, dnac_jwt_token):
    """
    This function will retrieve all the information for the device with the Cisco DNA Center device id
    :param device_id: Cisco DNA Center device_id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: device info
    """
    url = DNAC_URL + '/dna/intent/api/v1/network-device?id=' + device_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    device_response = requests.get(url, headers=header, verify=False)
    device_info = device_response.json()
    return device_info['response'][0]


def pnp_get_device_list(dnac_jwt_token):
    """
    This function will retrieve the PnP device list info
    :param dnac_jwt_token: DNA C token
    :return: PnP device info
    """
    url = DNAC_URL + '/dna/intent/api/v1/onboarding/pnp-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    pnp_device_json = response.json()
    return pnp_device_json


def check_ipv4_network_interface(ip_address, dnac_jwt_token):
    """
    This function will check if the provided IPv4 address is configured on any network interfaces
    :param ip_address: IPv4 address
    :param dnac_jwt_token: Cisco DNA Center token
    :return: None, or device_hostname and interface_name
    """
    url = DNAC_URL + '/dna/intent/api/v1/interface/ip-address/' + ip_address
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    response_status = response_json['response']

    # if response_status is a dict, it will include an error code. This means the IPv4 address is not assigned
    # to any managed network devices. We will check the PnP inventory next.
    # if the response_status is a list, it will include the info for the device with the interface
    # configured with the specified IPv4 address

    if type(response_status) is dict:
        pnp_device_list = pnp_get_device_list(dnac_jwt_token)
        for pnp_device in pnp_device_list:
            if pnp_device['deviceInfo']['httpHeaders'][0]['value'] == ip_address:
                device_hostname = pnp_device['deviceInfo']['hostname']
                return 'Found', device_hostname, 'unknown'
        return response_status['errorCode'], '', ''
    else:
        try:
            response_info = response_json['response'][0]
            interface_name = response_info['portName']
            device_id = response_info['deviceId']
            device_info = get_device_info(device_id, dnac_jwt_token)
            device_hostname = device_info['hostname']
            return 'Found', device_hostname, interface_name
        except:
            device_info = get_device_info_ip(ip_address, dnac_jwt_token)  # required for AP's
            device_hostname = device_info['hostname']
            return 'Found', device_hostname, 'unknown'


def create_path_trace(src_ip, src_port, dest_ip, dest_port, protocol, dnac_jwt_token):
    """
    This function will create a new Path Trace between the source IP address {src_ip} and the
    destination IP address {dest_ip}.
    The
    :param src_ip: Source IP address
    :param src_port: Source port, range (1-65535) or 'None'
    :param dest_ip: Destination IP address
    :param dest_port: Destination port, range (1-65535) or 'None'
    :param protocol: IP Protocol, range (1-254) or 'None'
    :param dnac_jwt_token: Cisco DNA Center token
    :return: Cisco DNA Center path visualisation id
    """

    param = {
        'destIP': dest_ip,
        'sourceIP': src_ip,
        'periodicRefresh': False,
        'inclusions': [
            'INTERFACE-STATS',
            'DEVICE-STATS',
            'ACL-TRACE',
            'QOS-STATS'
        ]
    }
    if src_port is not '':
        param.update({'sourcePort': src_port})
    if dest_port is not '':
        param.update({'destPort': dest_port})
    if protocol is not '':
        param.update({'protocol': protocol})

    url = DNAC_URL + '/dna/intent/api/v1/flow-analysis'
    header = {'accept': 'application/json', 'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    path_response = requests.post(url, data=json.dumps(param), headers=header, verify=False)
    path_json = path_response.json()
    path_id = path_json['response']['flowAnalysisId']
    return path_id


def get_path_trace_info(path_id, dnac_jwt_token):
    """
    This function will return the path trace details for the path visualisation {id}
    :param path_id: Cisco DNA Center path visualisation id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: Path visualisation status, and the details in a list [device,interface_out,interface_in,device...]
    """
    # check every 10 seconds to see if path trace completed
    path_status = 'INPROGRESS'
    while path_status == 'INPROGRESS':
        # wait 2 seconds for the path trace to be completed
        time.sleep(2)

        url = DNAC_URL + '/dna/intent/api/v1/flow-analysis/' + path_id
        header = {'accept': 'application/json', 'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        path_response = requests.get(url, headers=header, verify=False)
        path_json = path_response.json()
        path_info = path_json['response']
        path_status = path_info['request']['status']

    path_list = []
    if path_status == 'COMPLETED':
        network_info = path_info['networkElementsInfo']
        path_list.append(path_info['request']['sourceIP'])
        for elem in network_info:
            try:
                path_list.append(elem['ingressInterface']['physicalInterface']['name'])
            except:
                pass
            try:
                path_list.append(elem['name'])
            except:
                pass
            try:
                path_list.append(elem['egressInterface']['physicalInterface']['name'])
            except:
                pass
        path_list.append(path_info['request']['destIP'])
        return path_status, path_list
    else:
        if path_status == 'FAILED':
            path_error = [path_info['request']['failureReason']]
            return path_status, path_error
        else:
            return 'Something went wrong', ''


def get_client_info(ip_address, dnac_jwt_token):
    """
    This function will check if the host with the {ip_address} is connected to the network
    The function will create a path trace between the host with the {ip_address} and the Cisco DNA Center IP address
    :param ip_address: host (client) IPv4 address
    :param dnac_jwt_token: Cisco DNA Center token
    :return: Access Switch, Switchport, or None
    """
    path_trace_id = create_path_trace(ip_address, '', DNAC_IP, '', '', dnac_jwt_token)
    path_trace_result = get_path_trace_info(path_trace_id, dnac_jwt_token)
    if path_trace_result[0] == 'COMPLETED':
        access_switch = path_trace_result[1][2]
        switchport = path_trace_result[1][1]
        return access_switch, switchport
    if path_trace_result[0] == 'FAILED' and 'Not able to locate unique interface or host for source ip address' in \
            path_trace_result[1][0]:
        return None
    return 'Something went wrong'


def get_device_info_ip(ip_address, dnac_jwt_token):
    """
    This function will retrieve the device information for the device with the management IPv4 address {ip_address}
    :param ip_address: device management ip address
    :param dnac_jwt_token: Cisco DNA Center token
    :return: device information, or None
    """
    url = DNAC_URL + '/dna/intent/api/v1/network-device/ip-address/' + ip_address
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    device_info = response_json['response']
    if 'errorCode' == 'Not found':
        return None
    else:
        return device_info


def get_physical_topology(ip_address, dnac_jwt_token):
    """
    This function will retrieve the physical topology for the device with the {ip_address}
    :param ip_address: device/interface IP address
    :param dnac_jwt_token: Cisco DNA C token
    :return: topology info - connected device hostname and interface
    """
    url = DNAC_URL + '/dna/intent/api/v1/topology/physical-topology'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    topology_json = response.json()['response']
    topology_nodes = topology_json['nodes']
    topology_links = topology_json['links']

    # try to identify the physical topology
    for link in topology_links:
        try:
            if link['startPortIpv4Address'] == ip_address:
                connected_port = link['endPortName']
                connected_device_id = link['target']
                for node in topology_nodes:
                    if node['id'] == connected_device_id:
                        connected_device_hostname = node['label']
                break
        except:
            connected_port = None
            connected_device_hostname = None
    return connected_device_hostname, connected_port


def get_device_id_name(device_name, dnac_jwt_token):
    """
    This function will find the DNA C device id for the device with the name {device_name}
    :param device_name: device hostname
    :param dnac_jwt_token: DNA C token
    :return:
    """
    device_id = None
    device_list = get_all_device_info(dnac_jwt_token)
    for device in device_list:
        if device['hostname'] == device_name:
            device_id = device['id']
    return device_id


def sync_device(device_name, dnac_jwt_token):
    """
    This function will sync the device configuration from the device with the name {device_name}
    :param device_name: device hostname
    :param dnac_jwt_token: DNA C token
    :return: the response status code, 202 if sync initiated, and the task id
    """
    device_id = get_device_id_name(device_name, dnac_jwt_token)
    param = [device_id]
    url = DNAC_URL + '/dna/intent/api/v1/network-device/sync?forceSync=true'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    sync_response = requests.put(url, data=json.dumps(param), headers=header, verify=False)
    task = sync_response.json()['response']['taskId']
    return sync_response.status_code, task


def get_all_device_info(dnac_jwt_token):
    """
    The function will return all network devices info
    :param dnac_jwt_token: DNA C token
    :return: DNA C device inventory info
    """
    url = DNAC_URL + '/dna/intent/api/v1/network-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    all_device_response = requests.get(url, headers=header, verify=False)
    all_device_info = all_device_response.json()
    return all_device_info['response']

