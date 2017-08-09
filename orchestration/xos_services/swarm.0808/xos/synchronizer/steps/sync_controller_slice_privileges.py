import os
import base64
import json
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
from xos.logger import observer_logger as logger
from synchronizers.new_base.modelaccessor import *

class SyncControllerSlicePrivileges(SwarmSyncStep):
    provides=[SlicePrivilege]
    requested_interval=0
    observes=ControllerSlicePrivilege
    playbook = 'sync_controller_users.yaml'

    def map_sync_inputs(self, controller_slice_privilege):
        logger.info("controller_slice_privilege: %r" % controller_slice_privilege) 
        if not controller_slice_privilege.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_slice_privilege.controller)
            return

        template = os_template_env.get_template('sync_controller_users.yaml')
        logger.info("sync_controller_users.yaml --> template: %s" % template) 
        roles = [controller_slice_privilege.slice_privilege.role.role]
        # setup user home slice roles at controller 
        if not controller_slice_privilege.slice_privilege.user.site:
            logger.info('Sliceless user %s' % controller_slice_privilege.slice_privilege.user.email)
            raise Exception('Sliceless user %s'%controller_slice_privilege.slice_privilege.user.email)
        else:
            swarm_manager_url = controller_slice_privilege.controller.auth_url
            logger.info("swarm_manager_url: %s" % swarm_manager_url)
            (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
            logger.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port))

            user_fields = {
                            'swarm_manager_address' : swarm_manager_address,
                            'endpoint':controller_slice_privilege.controller.auth_url,
                            'endpoint_v3': controller_slice_privilege.controller.auth_url_v3,
                            'domain': controller_slice_privilege.controller.domain,
                            'name': controller_slice_privilege.slice_privilege.user.email,
                            'email': controller_slice_privilege.slice_privilege.user.email,
                            'password': controller_slice_privilege.slice_privilege.user.remote_password,
                            'admin_user': controller_slice_privilege.controller.admin_user,
                            'admin_password': controller_slice_privilege.controller.admin_password,
                            'ansible_tag':'%s@%s@%s'%(controller_slice_privilege.slice_privilege.user.email.replace('@','-at-'),controller_slice_privilege.slice_privilege.slice.name,controller_slice_privilege.controller.name),
                            'admin_tenant': controller_slice_privilege.controller.admin_tenant,
                            'roles':roles,
                            'tenant':controller_slice_privilege.slice_privilege.slice.name}    

            logger.info("user_fields: %s" % user_fields) 

            return user_fields

    def map_sync_outputs(self, controller_slice_privilege, res):
        logger.info("res: %s" % res)
        controller_slice_privilege.role_id = res[0]['id']
        controller_slice_privilege.save()

    def delete_record(self, controller_slice_privilege):
        controller_register = json.loads(controller_slice_privilege.controller.backend_register)
        logger.info("controller_register: %s" % controller_register)
        if (controller_register.get('disabled',False)):
                raise InnocuousException('Controller %s is disabled'%controller_slice_privilege.controller.name)

        ''' andrew
        if controller_slice_privilege.role_id:
            driver = self.driver.admin_driver(controller=controller_slice_privilege.controller)
            user = ControllerUser.objects.filter(
                controller_id=controller_slice_privilege.controller.id,
                user_id=controller_slice_privilege.slice_privilege.user.id
            )
            user = user[0]
            slice = ControllerSlice.objects.filter(
                controller_id=controller_slice_privilege.controller.id,
                user_id=controller_slice_privilege.slice_privilege.user.id
            )
            slice = slice[0]
            driver.delete_user_role(
                user.kuser_id, 
                slice.tenant_id, 
                controller_slice_privilege.slice_prvilege.role.role
            )
        '''
