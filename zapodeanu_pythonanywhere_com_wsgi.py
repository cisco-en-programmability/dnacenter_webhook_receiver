
import sys
import os

path = '/home/zapodeanu/get_webhooked_p'
if path not in sys.path:
    sys.path.append(path)

from flask_receiver import app as application  # noqa
