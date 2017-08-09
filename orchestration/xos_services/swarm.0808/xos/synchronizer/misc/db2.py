#!/usr/bin/env python
import os
import argparse
import sys

sys.path.append('/opt/xos')
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/swarm_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
#from xos.logger import Logger, logging, logger
import time

from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.backend import Backend
from synchronizers.new_base.event_loop import set_driver

#logger = Logger(level=logging.DEBUG)

import synchronizers.swarm.swarmlog as slog


def main(): 
    try: 
        slog.info("this is test")
        #listener = Listener()

    except Exception as ex:
        slog.info("[THREAD-UPDATE] Exception: %s" % ex)

if __name__ == '__main__':
    
    main() 
