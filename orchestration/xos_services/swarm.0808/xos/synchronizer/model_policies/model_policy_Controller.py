from collections import defaultdict
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class ControllerPolicy(Policy):
    model_name = "Controller"

    def handle_create(self, controller):
        self.logger.info("controller: %s" % str(controller))
        return self.handle_update(controller)

    def handle_update(self, controller):
        # relations for all sites
        self.logger.info("controller: %s" % str(controller))

        ctrls_by_site = defaultdict(list)
        ctrl_sites = ControllerSite.objects.all()
        for ctrl_site in ctrl_sites:
            ctrls_by_site[ctrl_site.site.id].append(ctrl_site.controller.id)

        self.logger.info("ctrls_by_site: %s" % str(ctrls_by_site))

        sites = Site.objects.all()
        for site in sites:
            if site.id not in ctrls_by_site or controller.id not in ctrls_by_site[site.id]:
                controller_site = ControllerSite(controller=controller, site=site)
                controller_site.save() 
                self.logger.info("controller_site: %s" % str(controller_site))

        # relations for all slices
        ctrls_by_slice = defaultdict(list)
        ctrl_slices = ControllerSlice.objects.all()
        for ctrl_slice in ctrl_slices:
            ctrls_by_slice[ctrl_slice.slice.id].append(ctrl_slice.controller.id)

        self.logger.info("ctrls_by_slice: %s" % str(ctrls_by_slice))

        slices = Slice.objects.all()
        for slice in slices:
            if slice.id not in ctrls_by_slice or controller.id not in ctrls_by_slice[slice.id]:
                controller_slice = ControllerSlice(controller=controller, slice=slice)
                controller_slice.save() 
                self.logger.info("controller_slice: %s" % str(controller_slice))

        # relations for all users
        ctrls_by_user = defaultdict(list)
        ctrl_users = ControllerUser.objects.all()
        for ctrl_user in ctrl_users:
            ctrls_by_user[ctrl_user.user.id].append(ctrl_user.controller.id)

        self.logger.info("ctrls_by_user: %s" % str(ctrls_by_user))

        users = User.objects.all()
        for user in users:
            if user.id not in ctrls_by_user or controller.id not in ctrls_by_user[user.id]:
                controller_user = ControllerUser(controller=controller, user=user)
                controller_user.save() 
                self.logger.info("controller_user: %s" % str(controller_user))

        # relations for all networks
        ctrls_by_network = defaultdict(list)
        ctrl_networks = ControllerNetwork.objects.all()
        for ctrl_network in ctrl_networks:
            ctrls_by_network[ctrl_network.network.id].append(ctrl_network.controller.id) 
        self.logger.info("ctrls_by_network: %s" % str(ctrls_by_network))

        networks = Network.objects.all()
        for network in networks:
            if network.id not in ctrls_by_network or controller.id not in ctrls_by_network[network.id]:
                controller_network = ControllerNetwork(controller=controller, network=network)
                if network.subnet and network.subnet.strip():
                    controller_network.subnet = network.subnet.strip()
                controller_network.save() 
                self.logger.info("controller_network: %s" % str(controller_network))

        # relations for all images
        ctrls_by_image = defaultdict(list)
        ctrl_images = ControllerImages.objects.all()
        for ctrl_image in ctrl_images:
            ctrls_by_image[ctrl_image.image.id].append(ctrl_image.controller.id) 
        self.logger.info("ctrls_by_image: %s" % str(ctrls_by_image))

        images = Image.objects.all()
        for image in images:
            if image.id not in ctrls_by_image or controller.id not in ctrls_by_image[image.id]:
                controller_image = ControllerImages(controller=controller, image=image)
                controller_image.save() 
                self.logger.info("controller_image: %s" % str(controller_image))
