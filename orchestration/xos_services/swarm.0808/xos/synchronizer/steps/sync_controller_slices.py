import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
from xos.logger import observer_logger as logger
from synchronizers.new_base.modelaccessor import *

class SyncControllerSlices(SwarmSyncStep):
    provides=[Slice]
    requested_interval=0
    observes=ControllerSlice
    playbook='sync_controller_slices.yaml'

    def map_sync_inputs(self, controller_slice):
        logger.info("sync'ing slice controller %s" % controller_slice)

        if not controller_slice.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_slice.controller)
            return

        logger.info("controller_slice.slice.creator.id: %s    controller_slice.controller.id: %s" % (controller_slice.slice.creator.id, controller_slice.controller.id))
        controller_users = ControllerUser.objects.filter(user_id=controller_slice.slice.creator.id,
                                                             controller_id=controller_slice.controller.id)
        if not controller_users:
            logger.info("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
            raise Exception("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
        else:
            controller_user = controller_users[0]
            ''' andrew
            driver = self.driver.admin_driver(controller=controller_slice.controller)
            roles = [driver.get_admin_role().name]
            ''' 

        max_instances=int(controller_slice.slice.max_instances)
        logger.info("controller_slice.slice.max_instances: %s" % controller_slice.slice.max_instances)

        swarm_manager_url = controller_slice.controller.auth_url
        logger.info("swarm_manager_url: %s" % swarm_manager_url)
        (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
        logger.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port)) 

        tenant_fields = {
                        'swarm_manager_address' : swarm_manager_address, 
                        'endpoint':controller_slice.controller.auth_url,
                        'endpoint_v3': controller_slice.controller.auth_url_v3,
                        'domain': controller_slice.controller.domain,
                        'admin_user': controller_slice.controller.admin_user,
                        'admin_password': controller_slice.controller.admin_password,
                        'admin_tenant': 'admin',
                        'tenant': controller_slice.slice.name,
                        'tenant_description': controller_slice.slice.description,
                        'roles':'andrew',
                        'name':controller_user.user.email,
                        'ansible_tag':'%s@%s'%(controller_slice.slice.name,controller_slice.controller.name),
                        'max_instances':max_instances}

        logger.info("tenant_fields: %s" % tenant_fields) 

        return tenant_fields

    def map_sync_outputs(self, controller_slice, res):
        '''
        tenant_id = res[0]['id']
        if (not controller_slice.tenant_id):
            try:
                driver = self.driver.admin_driver(controller=controller_slice.controller)
                driver.shell.nova.quotas.update(tenant_id=tenant_id, instances=int(controller_slice.slice.max_instances))
            except:
                logger.log_exc('Could not update quota for %s'%controller_slice.slice.name)
                raise Exception('Could not update quota for %s'%controller_slice.slice.name)
        '''

        controller_slice.tenant_id = 'andrew-123'
        controller_slice.backend_status = '1 - OK'
        controller_slice.save()


    def map_delete_inputs(self, controller_slice):
        logger.info("controller_slice: %r" % controller_slice) 
        controller_users = ControllerUser.objects.filter(user_id=controller_slice.slice.creator.id,
                                                              controller_id=controller_slice.controller.id)
        logger.info("controller_slice.slice.creator.id: %s   controller_slice.controller.id: %s" % (controller_slice.slice.creator.id, controller_slice.controller.id))

        if not controller_users:
            logger.info("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
            raise Exception("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
        else:
            controller_user = controller_users[0]

        tenant_fields = {'endpoint':controller_slice.controller.auth_url,
                          'admin_user': controller_slice.controller.admin_user,
                          'admin_password': controller_slice.controller.admin_password,
                          'admin_tenant': 'admin',
                          'tenant': controller_slice.slice.name,
                          'tenant_description': controller_slice.slice.description,
                          'name':controller_user.user.email,
                          'ansible_tag':'%s@%s'%(controller_slice.slice.name,controller_slice.controller.name),
                          'delete': True}
        logger.info("tenant_fields: %s" % tenant_fields)

        return tenant_fields
