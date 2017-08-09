import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from xos.logger import observer_logger as logger
from synchronizers.new_base.modelaccessor import *

class SyncImages(SwarmSyncStep):
    provides=[Image]
    requested_interval=0
    observes=[Image]

    def sync_record(self, role):
        logger.info("SyncImages:: role: %r" % role)
        # nothing to do
        pass
