import os
import base64
from synchronizers.swarm.swarmsyncstep import SwarmSyncStep
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
from synchronizers.new_base.modelaccessor import * 
from xos.logger import observer_logger as logger 
import synchronizers.swarm.swarmlog as slog



class SyncControllerImages(SwarmSyncStep):
    provides=[ControllerImages]
    observes = ControllerImages
    requested_interval=0
    playbook='sync_controller_images.yaml' 

    def fetch_pending(self, deleted):
        if (deleted):
            return []

        return super(SyncControllerImages, self).fetch_pending(deleted) 

    def map_sync_inputs(self, controller_image):
        '''
        (Example) 
            swarm_manager_url     : "manager.swarm.cord.lab:5000"
            swarm_manager_address : "manager.swarm.cord.lab"
            docker_registry_port  : "5000"
        '''
        swarm_manager_url = controller_image.controller.auth_url
        slog.info("swarm_manager_url: %s" % swarm_manager_url) 
        (swarm_manager_address, docker_registry_port) = swarm_manager_url.split(':')
        slog.info("swarm_manager_address: %s    docker_registry_port: %s" % (swarm_manager_address, docker_registry_port)) 

        input_fields = {
                        'swarm_manager_address' : swarm_manager_address,
                        'docker_registry_port'  : docker_registry_port,
                        'image_file_path'       : controller_image.image.path,
                        'image_dir'             : os.path.dirname(controller_image.image.path),
                        'image_name'            : controller_image.image.name,
                        'image_tag'             : controller_image.image.tag, 
                        'ansible_tag': '%s@%s'%(controller_image.image.name,controller_image.controller.name)  # name of ansible playbook
                        } 

        slog.info("input_fields: %s" % str(input_fields))

        return input_fields 

    def map_sync_outputs(self, controller_image, res):
        slog.debug("( andrew:50 ) Ansible playbook result: %s" % str(res))
        slog.debug("( andrew:51 ) Ansible playbook result[4]: %s" % str(res[4]))
        slog.debug("( andrew:52 ) Ansible playbook result[4]['image']: %s" % str(res[4]['image']))
        slog.debug("( andrew:53 ) Ansible playbook result[4]['image']['Id']: %s" % str(res[4]['image']['Id']))
        ## controller_image.glance_image_id = 'sha256:c75bebcdd211f41b3a460c7bf82970ed6c75acaab9c'
        controller_image.glance_image_id = str(res[4]['image']['Id'])  ## (ex) sha256:c75bebcdd211f41b3a460c7bf82970ed6c75acaab9c
        if len(controller_image.glance_image_id) > 2:
            controller_image.backend_status = '1 - OK'
        else:
            controller_image.backend_status = '2 - Ansible playbook failure'
        controller_image.save()
