import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
from xos.logger import observer_logger as logger
from synchronizers.new_base.modelaccessor import *

class SyncControllerUsers(SwarmSyncStep):
    provides=[User]
    requested_interval=0
    observes=ControllerUser
    playbook='sync_controller_users.yaml'

    def map_sync_inputs(self, controller_user):
        logger.info("Begin SyncControllerUsers.map_sync_inputs(%r)" % controller_user)
        if not controller_user.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_user.controller)
            return

        # All users will have at least the 'user' role at their home site/tenant.
        # We must also check if the user should have the admin role

        roles = ['user']
        ''' andrew
        if controller_user.user.is_admin:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            roles.append(driver.get_admin_role().name)
        '''

        # setup user home site roles at controller
        if not controller_user.user.site:
            raise Exception('Siteless user %s'%controller_user.user.email)
        else:
            swarm_manager_url = controller_user.controller.auth_url
            logger.info("swarm_manager_url: %s" % swarm_manager_url)
            (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
            logger.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port))

            user_fields = {
                            'swarm_manager_address' : swarm_manager_address,
                            'endpoint':controller_user.controller.auth_url,
                            'endpoint_v3': controller_user.controller.auth_url_v3,
                            'domain': controller_user.controller.domain,
                            'name': controller_user.user.email,
                            'email': controller_user.user.email,
                            'password': controller_user.user.remote_password,
                            'admin_user': controller_user.controller.admin_user,
                            'admin_password': controller_user.controller.admin_password,
                            'ansible_tag':'%s@%s'%(controller_user.user.email.replace('@','-at-'),controller_user.controller.name), # name of ansible playbook
                            'admin_project': controller_user.controller.admin_tenant,
                            'roles':roles,
                            'project':controller_user.user.site.login_base
                            }
        logger.info("user_fields: %s" % user_fields)
        return user_fields

    def map_sync_outputs(self, controller_user, res):
        logger.info("res: %s" % res) 
        ## controller_user.kuser_id = res[0]['user']['id']
        controller_user.kuser_id = 'andrew-123'
        controller_user.backend_status = '1 - OK'
        controller_user.save()

    def delete_record(self, controller_user):
        logger.info("Begin delete_record(%r)" % controller_user) 
        ''' andrew
        if controller_user.kuser_id:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            driver.delete_user(controller_user.kuser_id)
        '''

