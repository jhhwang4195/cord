import os
import base64
from synchronizers.new_base.syncstep import SyncStep

class SwarmSyncStep(SyncStep):
    """
    XOS Sync step for copying data to Docker Swarm Manager
    """ 
    
    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        return

    def __call__(self, **args):
        return self.call(**args)
