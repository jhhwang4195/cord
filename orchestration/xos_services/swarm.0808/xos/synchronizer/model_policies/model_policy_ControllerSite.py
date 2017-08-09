from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class ControllerSitePolicy(Policy):
    model_name = "ControllerSite"

    def handle_create(self, controller_site):
        self.logger.info("controller_site: %s" % str(controller_site))
        return self.handle_update(controller_site)

    def handle_update(self, controller_site):
        self.logger.info("controller_site: %s" % str(controller_site))
        my_status_code = int(controller_site.backend_status[0])
        try:
            his_status_code = int(controller_site.site.backend_status[0])
        except:
            his_status_code = 0

        if (my_status_code not in [0,his_status_code]):
            controller_site.site.backend_status = controller_site.backend_status
            controller_site.site.save(update_fields = ['backend_status'])

        self.logger.info("controller_site.backend_status[0]: %s    controller_site.site.backend_status[0]: %s" % (controller_site.backend_status[0], controller_site.site.backend_status[0]))
