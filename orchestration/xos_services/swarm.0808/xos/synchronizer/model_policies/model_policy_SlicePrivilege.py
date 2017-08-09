from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class SlicePrivilegePolicy(Policy):
    model_name = "SlicePrivilege"

    def handle_create(self, slice_privilege):
        self.logger.info("slice_privilege: %s" % str(slice_privilege))
        return self.handle_update(slice_privilege)

    def handle_update(self, slice_privilege):
        self.logger.info("slice_privilege: %s" % str(slice_privilege))
        # slice_privilege = SlicePrivilege.get(slice_privilege_id)
        # apply slice privilage at all controllers
        controller_slice_privileges = ControllerSlicePrivilege.objects.filter(
            slice_privilege = slice_privilege,
            )
        existing_controllers = [sp.controller for sp in controller_slice_privileges]
        all_controllers = Controller.objects.all()
        for controller in all_controllers:
            if controller not in existing_controllers:
                ctrl_slice_priv = ControllerSlicePrivilege(controller=controller, slice_privilege=slice_privilege)
                ctrl_slice_priv.save()
                self.logger.info("ctrl_slice_priv: %s" % str(ctrl_slice_priv))

