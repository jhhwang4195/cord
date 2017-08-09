from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class InstancePolicy(Policy):
    model_name = "Instance"

    def handle_create(self, instance):
        self.logger.info("instance: %s" % str(instance))
        return self.handle_update(instance)

    def handle_update(self, instance):
        self.logger.info("instance: %s" % str(instance))
        ## <Example>
        ##  instance id : 2
        ##    - slice_id   : 4
        ##    - network_id : 1, 3, 4
        networks = [ns.network for ns in NetworkSlice.objects.filter(slice_id=instance.slice.id)] 
        self.logger.info("networks: %s" % str(networks))
        ## <Example>
        ##  instance id : 1  --> node id : 1  --> site_deployment id : 1 --> controller id : 1
        ##    - controller_networks : 1, 2, 3, 4
        controller_networks = ControllerNetwork.objects.filter(controller_id=instance.node.site_deployment.controller.id)
        self.logger.info("controller_networks: %s" % str(controller_networks))

        # a little clumsy because the API ORM doesn't support __in queries
        network_ids = [x.id for x in networks]    ## network_ids: 1, 3, 4
        controller_networks = [x for x in controller_networks if x.network.id in network_ids]  ## controller_networks: 1,2,3,4 --> 1,3,4

        for cn in controller_networks:   ## controller_networks: 1,3,4
            if (cn.lazy_blocked):
                self.logger.info("MODEL POLICY: instance %s unblocking network %s" % (instance, cn.network))
            cn.lazy_blocked=False    ## I don't know the reason to set lazy_blocked=False
            cn.backend_register = '{}'
            cn.save()
