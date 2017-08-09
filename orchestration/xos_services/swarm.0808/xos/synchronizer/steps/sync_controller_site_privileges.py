## andrew.  Swarm synchronizer doesn't use this class
import os
import base64
import json
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from xos.logger import observer_logger as logger
from synchronizers.new_base.ansible_helper import *
from synchronizers.new_base.modelaccessor import *

class SyncControllerSitePrivileges(SwarmSyncStep):
    provides=[SitePrivilege]
    requested_interval=0
    observes=ControllerSitePrivilege
    playbook='sync_controller_users.yaml'

    ## andrew.  swarm does not use this method.
    def map_sync_inputs(self, controller_site_privilege):
        logger.info("begin map_sync_input()") 
        controller_register = json.loads(controller_site_privilege.controller.backend_register)
        if not controller_site_privilege.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_site_privilege.controller)
            return

        roles = [controller_site_privilege.site_privilege.role.role]
        logger.info("roles: %s" % roles) 
        # setup user home site roles at controller 
        if not controller_site_privilege.site_privilege.user.site:
            logger.info("Siteless user %s" % controller_site_privilege.site_privilege.user.email)
            raise Exception('Siteless user %s'%controller_site_privilege.site_privilege.user.email)
        else:
            swarm_manager_url = controller_site_privilege.controller.auth_url
            logger.info("swarm_manager_url: %s" % swarm_manager_url)
            (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
            logger.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port)) 

            user_fields = {
                            'swarm_manager_address' : swarm_manager_address, 
                            'endpoint':controller_site_privilege.controller.auth_url,
                            'endpoint_v3': controller_site_privilege.controller.auth_url_v3,
                            'domain': controller_site_privilege.controller.domain,
                            'name': controller_site_privilege.site_privilege.user.email,
                            'email': controller_site_privilege.site_privilege.user.email,
                            'password': controller_site_privilege.site_privilege.user.remote_password,
                            'admin_user': controller_site_privilege.controller.admin_user,
                            'admin_password': controller_site_privilege.controller.admin_password,
                            'ansible_tag':'%s@%s'%(controller_site_privilege.site_privilege.user.email.replace('@','-at-'),controller_site_privilege.controller.name),
                            'admin_tenant': controller_site_privilege.controller.admin_tenant,
                            'roles':roles,
                            'tenant':controller_site_privilege.site_privilege.site.login_base
                            }

        logger.info("user_fields: %s" % user_fields)

        return user_fields

    def map_sync_outputs(self, controller_site_privilege, res):
        # results is an array in which each element corresponds to an 
        # "ok" string received per operation. If we get as many oks as
        # the number of operations we issued, that means a grand success.
        # Otherwise, the number of oks tell us which operation failed.
        logger.info("res: %s" % res) 
        controller_site_privilege.role_id = res[0]['id']
        controller_site_privilege.save()

    def delete_record(self, controller_site_privilege):
        controller_register = json.loads(controller_site_privilege.controller.backend_register)
        logger.info("controller_register: %s" % controller_register)

        if (controller_register.get('disabled',False)):
            logger.info("Controller %s is disabled" % controller_site_privilege.controller.name) 
            raise InnocuousException('Controller %s is disabled'%controller_site_privilege.controller.name)

        logger.info("Nothing to do on Swarm cluster") 
        pass
        ''' andrew
        if controller_site_privilege.role_id:
            driver = self.driver.admin_driver(controller=controller_site_privilege.controller)
            user = ControllerUser.objects.get(
                                            controller=controller_site_privilege.controller, 
                                            user=controller_site_privilege.site_privilege.user
                                            )
            site = ControllerSite.objects.get(
                                            controller=controller_site_privilege.controller, 
                                            user=controller_site_privilege.site_privilege.user
                                            )
            driver.delete_user_role(
                                    user.kuser_id, 
                                    site.tenant_id, 
                                    controller_site_privilege.site_prvilege.role.role
                                    )
        '''
