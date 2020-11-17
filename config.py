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


# This file contains:
# the Webhook username and password

WEBHOOK_URL = 'http://localhost:5000/webhook'  # test with Flask receiver running local
# WEBHOOK_URL = 'http://10.93.141.38:5000/webhook  # test with Flask receiver hosted remotely to a server or cloud

WEBHOOK_USERNAME = 'username'
WEBHOOK_PASSWORD = 'password'
