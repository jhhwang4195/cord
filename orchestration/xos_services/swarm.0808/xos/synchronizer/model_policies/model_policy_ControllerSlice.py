from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class ControllerSlicePolicy(Policy):
    model_name = "ControllerSlice"

    def handle_create(self, controller_slice):
        self.logger.info("controller_slice: %s" % str(controller_slice))
        return self.handle_update(controller_slice)

    def handle_update(self, controller_slice):
        self.logger.info("controller_slice: %s" % str(controller_slice))
        my_status_code = int(controller_slice.backend_status[0])
        try:
            his_status_code = int(controller_slice.slice.backend_status[0])
        except:
            his_status_code = 0
 
        fields = []
        if (my_status_code not in [0,his_status_code]):
            controller_slice.slice.backend_status = controller_slice.backend_status
            fields+=['backend_status']

        if (controller_slice.backend_register != controller_slice.slice.backend_register):
            controller_slice.slice.backend_register = controller_slice.backend_register
            fields+=['backend_register']

        self.logger.info("controller_slice.backend_status[0]: %s    controller_slice.slice.backend_status[0]: %s    fields: %s" % (controller_slice.backend_status[0], controller_slice.slice.backend_status[0], str(fields)))
        controller_slice.slice.save(update_fields = fields)
