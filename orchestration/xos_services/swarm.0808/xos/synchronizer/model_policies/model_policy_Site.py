from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class SitePolicy(Policy):
    model_name = "Site"

    def handle_create(self, site):
        self.logger.info("site: %s" % str(self.logger.info))
        return self.handle_update(site)

    def handle_update(self, site):
        self.logger.info("site: %s" % str(self.logger.info))
        # site = Site.get(site_id)
        # make sure site has a ControllerSite record for each controller
        ctrl_sites = ControllerSite.objects.filter(site_id=site.id)
        existing_controllers = [cs.controller for cs in ctrl_sites]
        existing_controller_ids = [c.id for c in existing_controllers]

        all_controllers = Controller.objects.all()
        for ctrl in all_controllers:
            if ctrl.id not in existing_controller_ids:
                ctrl_site = ControllerSite(controller=ctrl, site=site)
                ctrl_site.save()
                self.logger.info("ctrl_site: %s" % str(ctrl_site))

