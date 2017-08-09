#!/usr/bin/env python
import os
import argparse
import sys

sys.path.append('/opt/xos')
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/swarm_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from xos.logger import Logger, logging, logger
import time

from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.backend import Backend
from synchronizers.new_base.event_loop import set_driver

logger = Logger(level=logging.DEBUG)

def main():
    ## TODO   copy /opt/cord_profile/node_key to /root/.ssh
    models_active = False
    wait = False
    while not models_active:
        instance = Loadbalancer.objects.first() 

        try: 
            inst_id = instance.id
            logger.debug("[THREAD-UPDATE] inst_id          : %s" % inst_id)
            old_update = 0

            for idx in range(1, 100, 1):
                logger.debug("\n\n") 
                logger.debug("[THREAD-UPDATE] idx: %s" % idx) 
                new_inst = Instance.objects.get(id=inst_id)
##              logger.debug("[THREAD-UPDATE] enacted       : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(new_inst.enacted))) 

                if old_update == 0:
                    old_update = new_inst.updated 
                logger.debug("[THREAD-UPDATE] updated(old)     : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(old_update))) 

                if (new_inst.userData is not None) and (new_inst.volumes is not None) and (new_inst.instance_name is not None):
                    if (len(new_inst.userData) > 2) and (len(new_inst.volumes) > 2) and  (len(new_inst.instance_name) > 2): 
                        logger.debug("[THREAD-UPDATE] instance_name    : %s  (%s)" % (new_inst.instance_name, len(new_inst.instance_name)))
                        logger.debug("[THREAD-UPDATE] userData         : %s  (%s)" % (new_inst.userData,      len(new_inst.userData)))
                        logger.debug("[THREAD-UPDATE] volumes          : %s  (%s)" % (new_inst.volumes ,      len(new_inst.volumes )))
                        new_inst.numberCores = idx
                        new_inst.updated     = time.time()
                        logger.debug("[THREAD-UPDATE] updated to renew : %s (%s)" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(new_inst.updated)), new_inst.updated))
                        new_inst.save(update_fields=['updated', 'numberCores'])

                        time.sleep(1)
                        ## time.sleep(10)

                        clone_inst = Instance.objects.get(id=inst_id)
                        clone_inst.save(update_fields=['numberCores'])
                        logger.debug("[THREAD-UPDATE] updated          : %s (%s)" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(clone_inst.updated)), clone_inst.updated))
                        ## logger.debug("[THREAD-UPDATE] enacted          : %s (%s)" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(clone_inst.enacted)), clone_inst.updated))
                        if clone_inst.updated == old_update:
                            logger.debug("[THREAD-UPDATE] old & new updated date is same. Nothing is executed. Waiting 10 seconds, and I will check once more.") 
                            time.sleep(1)
                        else:
                            logger.debug("[THREAD-UPDATE] old & new updated date is different. Swarm synchronizer will run [docker service update ....]") 
                            return 
                            ##break 

        except Exception as ex:
            logger.info("[THREAD-UPDATE] Exception: %s" % ex)

        models_active = True













        """
            for idx in range(1, 100, 1):
                logger.debug("AA:: idx: %d" % idx) 

                inst1 = Instance.objects.get(instance_name="mysite_lbaas-1")
                logger.debug("AA:: inst1.instance_name : %s" % inst1.instance_name) 
                logger.debug("AA:: inst1.id            : %s" % inst1.id) 
                logger.debug("AA:: inst1.updated: %s   enacted: %s" % 
                                (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst1.updated)), 
                                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst1.enacted)))
                            ) 

                inst1.numberCores = idx
                inst1.userData    = "--publish-add %d:%d" % (idx * 100 + 10000, idx * 100 + 10000)
                inst1.updated     = time.time()
                ## inst1.save()  ## OK, but This method is not recommended. Because all attribute is saved with old value of a process memory
                inst1.save(update_fields=['updated', 'userData', 'numberCores'])  ## OK
                ## super(type(inst1), inst1).save(update_fields=['updated', 'userData', 'numberCores'])  ## OK
                ##inst1.save(commit=True)

                inst2 = Instance.objects.get(instance_name="mysite_lbaas-1") 
                inst2.save(update_fields=['updated']) 
                ##inst2.save(commit=True)
                ##super(type(inst2), inst2).save(commit=True)  ## OK
                logger.debug("AA:: inst1.updated       : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst1.updated)))
                logger.debug("AA:: inst1.enacted       : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst1.enacted)))
                logger.debug("AA:: inst2.updated       : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst2.updated)))
                logger.debug("AA:: inst2.enacted       : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(inst2.enacted)))
                time.sleep(10)

        """

            ##super(type(inst1), inst1).save(update_fields=['updated'])  ## OK
        """
        ## filter with "core_tenantwithcontainer.instance_id"
        loadbalancer1 = Loadbalancer.objects.first() 
        logger.debug("loadbalancer1.description : %s" % loadbalancer1.description) 
        logger.debug("loadbalancer1.instance.id : %s" % loadbalancer1.instance.id) 

        loadbalancer2 = Loadbalancer.objects.filter(tenantwithcontainer_ptr_id=1)
        logger.debug("loadbalancer2    : %s" % loadbalancer2)
        logger.debug("loadbalancer2[0] : %s" % loadbalancer2[0])
        logger.debug("loadbalancer2[0].description: %s" % loadbalancer2[0].description) 
        """ 

            ## models_active = True

        """
        except Exception,e:
            # logger.info(str(e))
            logger.info('AA:: Waiting for data model to come up before starting...   (%s)' % e)
            time.sleep(10)
            wait = True
        """

    ##logger.debug("Data Model is active (controller1: %s)" % controller1)


if __name__ == '__main__':
    
    main() 
