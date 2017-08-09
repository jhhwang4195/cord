from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

class UserPolicy(Policy):
    model_name = "User"

    def handle_create(self, user):
        self.logger.info("user: %s" % str(self.logger.info))
        return self.handle_update(user)

    def handle_update(self, user):
        self.logger.info("user: %s" % str(self.logger.info))
        controller_users = ControllerUser.objects.filter(user_id=user.id)
        existing_controllers = [cu.controller for cu in controller_users]
        existing_controller_ids = [c.id for c in existing_controllers]
        all_controllers = Controller.objects.all()
        for controller in all_controllers:
            if controller.id not in existing_controller_ids:
                ctrl_user = ControllerUser(controller=controller, user=user)
                ctrl_user.save()
                self.logger.info("ctrl_user: %s" % str(ctrl_user))

