#!/usr/bin/env python
import os
import argparse
import sys
import time

sys.path.append('/opt/xos')
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/swarm_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.backend import Backend
from synchronizers.new_base.event_loop import set_driver

import synchronizers.swarm.swarmlog as slog


def main():
    try:
        slog.info("[EXAMPLE] This is test")
        net_template1 = NetworkTemplate()
        net_template1.controller_kind = "kuryr-controller"
        net_template1.leaf_model_name = "kuryr"
        net_template1.name            = "kuryr-net"                 ## docker network name
        net_template1.description     = "this is andrew_net"
        net_template1.visibility      = "neutry-swarm"
        net_template1.translation     = "kuryr-overlay"
        net_template1.access          = "kuryr/libnetwork2:latest"  ## --driver, --ipam-driver
        net_template1.shared_network_id = "neutron.pool.name=kuryr-subnetpool"  ## --ipam-opt, -o
        net_template1.topology_kind   = "kuryr"
        net_template1.vtn_kind        = "PUBLIC"

        net_template1.save()

        net_template2 = NetworkTemplate.objects.get(name="kuryr-net")
        slog.info("[EXAMPLE] net_template2.description       : %s" % str(net_template2.description  ))
        slog.info("[EXAMPLE] net_template2.translation       : %s" % str(net_template2.translation  ))
        slog.info("[EXAMPLE] net_template2.access            : %s" % str(net_template2.access       ))
        slog.info("[EXAMPLE] net_template2.shared_network_id : %s" % str(net_template2.shared_network_id))
        slog.info("[EXAMPLE] net_template2.topology_kind     : %s" % str(net_template2.topology_kind))
    except Exception as ex:
        slog.info("[EXAMPLE] Exception: %s" % ex)

if __name__ == '__main__':
    main()
