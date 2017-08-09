import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
import json
from synchronizers.new_base.modelaccessor import *
from xos.logger import observer_logger as logger


class SyncControllerSites(SwarmSyncStep):
    requested_interval=0
    provides=[Site]
    observes=ControllerSite
    playbook = 'sync_controller_sites.yaml'

    def fetch_pending(self, deleted=False):
        lobjs = super(SyncControllerSites, self).fetch_pending(deleted)
        logger.info("lobjs: %r" % lobjs) 

        logger.info("deleted: %s" % deleted)
        if not deleted:
            # filter out objects with null controllers
            lobjs = [x for x in lobjs if x.controller]
            logger.info("lobjs: %r" % lobjs)

        return lobjs

    def map_sync_inputs(self, controller_site):
        swarm_manager_url = controller_site.controller.auth_url
        logger.info("swarm_manager_url: %s" % swarm_manager_url)
        (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
        logger.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port))

        input_fields = {
                        'swarm_manager_address' : swarm_manager_address,
                        'endpoint':controller_site.controller.auth_url,
                        'endpoint_v3': controller_site.controller.auth_url_v3,
                        'domain': controller_site.controller.domain,
                        'admin_user': controller_site.controller.admin_user,
                        'admin_password': controller_site.controller.admin_password,
                        'admin_tenant': controller_site.controller.admin_tenant,
                        'ansible_tag': '%s@%s'%(controller_site.site.login_base,controller_site.controller.name), # name of ansible playbook
                        'tenant': controller_site.site.login_base,
                        'tenant_description': controller_site.site.name}

        logger.info("input_fields: %s" % input_fields) 

        return input_fields

    def map_sync_outputs(self, controller_site, res):
        logger.info("res: %s" % res) 
        logger.info("controller_site: %r" % controller_site) 
        ## controller_site.tenant_id = res[0]['id']
        controller_site.tenant_id = 'andrew-123456789'   ## FIXME
        controller_site.backend_status = '1 - OK'
        controller_site.save()

    def delete_record(self, controller_site):
        logger.info("controller_site: %r" % controller_site) 
        controller_register = json.loads(controller_site.controller.backend_register)
        logger.info("controller_register: %s" % controller_register) 
        if (controller_register.get('disabled',False)):
            logger.info('Controller %s is disabled'%controller_site.controller.name) 
            raise InnocuousException('Controller %s is disabled'%controller_site.controller.name)

        ''' andrew
        if controller_site.tenant_id:
            driver = self.driver.admin_driver(controller=controller_site.controller)
            driver.delete_tenant(controller_site.tenant_id)
        '''

        """
        Ansible does not support tenant deletion yet

        import pdb
        pdb.set_trace()
        template = os_template_env.get_template('delete_controller_sites.yaml')
        input_fields = {'endpoint':controller_site.controller.auth_url,
                        'admin_user': controller_site.controller.admin_user,
                        'admin_password': controller_site.controller.admin_password,
                        'admin_tenant': 'admin',
                        'ansible_tag': 'controller_sites/%s@%s'%(controller_site.controller_site.site.login_base,controller_site.controller_site.deployment.name), # name of ansible playbook
                        'tenant': controller_site.controller_site.site.login_base,
                        'delete': True}

        rendered = template.render(input_fields)
        res = run_template('sync_controller_sites.yaml', input_fields)

        if (len(res)!=1):
            raise Exception('Could not assign roles for user %s'%input_fields['tenant'])
        """
