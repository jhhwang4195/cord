import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from xos.logger import observer_logger as logger
from synchronizers.new_base.modelaccessor import *

class SyncRoles(SwarmSyncStep):
    provides=[Role]
    requested_interval=0
    observes=[SiteRole,SliceRole,ControllerRole]

    def sync_record(self, role):
        logger.info("role: %r" % role) 
        logger.info("role.enacted: %s" % role.enacted) 
        if not role.enacted:
            controllers = Controller.objects.all()
            logger.info("controllers: %s" % controllers) 
            for controller in controllers:
                logger.info("controller: %s" % controller)
                '''
                driver = self.driver.admin_driver(controller=controller)
                driver.create_role(role.role)
                '''
            role.save()
 

