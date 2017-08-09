from service import XOSService
from services.lbaas.models import LbService

class LbaasLbService(XOSService):
    provides = "tosca.nodes.LbService"
    xos_model = LbService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "private_key_fn", "versionNumber", "service_name"]


