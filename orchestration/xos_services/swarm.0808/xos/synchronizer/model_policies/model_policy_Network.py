from synchronizers.new_base.modelaccessor import *
from collections import defaultdict
from synchronizers.new_base.policy import Policy

class NetworkPolicy(Policy):
    model_name = "Network"

    def handle_create(self, network):
        self.logger.info("handle_create:: network: %s" % str(network))
        return self.handle_update(network)

    def handle_update(self, network):
        self.logger.info("handle_update:: network: %s" % str(network))
        # if (not network.owner.policed) or (network.owner.policed<network.owner.updated):
        #    raise Exception("Cannot apply network policies until slice policies have completed")

        #expected_controllers = []
        #for slice_controller in ControllerSlice.objects.all():
        #    if slice_controller.slice.id == network.owner.id:
        #        expected_controllers.append(slice_controller.controller)

        # For simplicity, let's assume that a network gets deployed on all controllers.

        expected_controllers =  Controller.objects.all()
        self.logger.info("Controller.objects.all(): %s" % str(expected_controllers) )

        existing_controllers = []
        for cn in ControllerNetwork.objects.all():
            if cn.network.id == network.id:
                existing_controllers.append(cn.controller)

        existing_controller_ids = [c.id for c in existing_controllers]
        self.logger.info("existing_controller_ids: %s" % str(existing_controller_ids))

        for expected_controller in expected_controllers:
            if expected_controller.id not in existing_controller_ids:
                lazy_blocked=True

                # check and see if some instance already exists
                for networkslice in network.networkslices.all():
                    found = False
                    for instance in networkslice.slice.instances.all():
                       if instance.node.site_deployment.controller.id == expected_controller.id:
                           found = True
                    if found:
                       self.logger.info("MODEL_POLICY: network %s setting lazy_blocked to false because instance on controller already exists" % network)
                       lazy_blocked=False

                nd = ControllerNetwork(network=network, controller=expected_controller, lazy_blocked=lazy_blocked)
                self.logger.info("MODEL POLICY: network [%s] create ControllerNetwork [%s] lazy_blocked [%s]" % (network, nd, lazy_blocked))
                if network.subnet:
                    # XXX: Possibly unpredictable behavior if there is
                    # more than one ControllerNetwork and the subnet
                    # is specified.
                    nd.subnet = network.subnet
                nd.save()
