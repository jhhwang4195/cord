import os
import sys
import json
import collections
import time
from datetime import datetime
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)

class SyncLoadbalancer(SyncInstanceUsingAnsible):
    provides = [Loadbalancer]
    observes = Loadbalancer
    requested_interval = 0
    template_name = "loadbalancer_playbook.yaml"
    service_key_name = "/opt/xos/synchronizers/lbaas/lbaas_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncLoadbalancer, self).__init__(*args, **kwargs)

    def convert_unicode_to_str(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert_unicode_to_str, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert_unicode_to_str, data))
        else:
            return data

    def update_pool_status(self, pool_id):
        pool_status = ""

        pool = Pool.objects.get(id=pool_id)
        members = Member.objects.filter(memberpool_id=pool.id)
        if len(members) > 0:
            try:
                pool = Pool.objects.get(id=pool_id)
            except Exception as err:
                logger.error("%s (id=%s)" % ((str(err), pool_id)))
                pool_status = "ERROR"

            healths = Healthmonitor.objects.filter(id=pool.health_monitor_id)
            if len(healths) > 0:
                pool_status = "ACTIVE"
            else:
                logger.error("Healthmonitor information does not exist (id=%s)" % pool.health_monitor_id)
                pool_status = "ERROR"
        else:
            logger.error("Member information does not exist (memberpool_id=%s)" % pool.id)
            pool_status = "ERROR"

        try:
            pool = Pool.objects.get(id=pool_id)
            pool.status = pool_status
            pool.save()
        except Exception as err:
            logger.error("id does not exist in Pool table (id=%s)" % pool_id)

        return pool_status

    def update_loadbalancer_status(self, lb_id):
        lb = Loadbalancer.objects.get(loadbalancer_id=lb_id)
        if lb:
            listeners = Listener.objects.filter(id=lb.listener_id)
            for listener in listeners:
                pools = Pool.objects.filter(id=lb.pool_id)
                for pool in pools:
                    members = Member.objects.filter(memberpool_id=pool.id)
                    if len(members) > 0:
                        healths = Healthmonitor.objects.filter(id=pool.health_monitor_id)
                        if len(healths) > 0:
                            lb.provisioning_status = "ACTIVE"
                        else:
                            logger.error("Healthmonitor information does not exist (id=%s)" % pool.health_monitor_id)
                            lb.provisioning_status = "ERROR"
                    else:
                        logger.error("Member information does not exist (memberpool_id=%s)" % pool.id)
                        lb.provisioning_status = "ERROR"
                if len(pools) == 0:
                    logger.error("Pool information does not exist (loadbalancer_id=%s, id=%s)" % (lb_id, lb.pool_id))
                    lb.provisioning_status = "ERROR"
            if len(listeners) == 0:
                logger.error("Listener information does not exist (id=%s)" % lb.listener_id)
                lb.provisioning_status = "ERROR"
        else:
            logger.error("Loadbalancer information does not exist (loadbalancer_id=%s)" % lb_id)
            lb.provisioning_status = "ERROR"

        logger.info("lb.provisioning_status=%s" % lb.provisioning_status)
        lb.save()

        return lb.provisioning_status

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        logger.info("===============================================================")
        logger.info("instance_name=%s, instance_id=%d, instance_uuid=%s" \
        % (o.instance.instance_name, o.instance_id, o.instance.instance_uuid))

        lb_status = True
        if self.update_pool_status(o.pool_id) != "ACTIVE":
            logger.error("Pool status is not ACTIVE (pool_id=%s)" % o.pool_id)
            lb_status = False

        if self.update_loadbalancer_status(o.loadbalancer_id) != "ACTIVE":
            logger.error("Loadbalancer status is not ACTIVE (loadbalancer_id=%s)" % o.loadbalancer_id)
            lb_status = False

        if lb_status == False:
            return None

        fields = {}
        fields['instance_id'] = o.instance.id
        fields['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fields["baremetal_ssh"] = True

        loadbalancer = {}
        loadbalancer['loadbalancer_id'] = o.loadbalancer_id
        loadbalancer['lb_name'] = o.name
        loadbalancer['vip_address'] = o.vip_address

        try:
            network = Network.objects.get(name='public')
            try:
                port = Port.objects.get(instance_id=o.instance_id, network_id=network.id)
                loadbalancer['vip_address'] = port.ip
                try:
                    lb = Loadbalancer.objects.get(loadbalancer_id=o.loadbalancer_id)
                    lb.vip_address = port.ip
                    lb.save()
                except Exception as err:
                    logger.error("Loadbalancer information does not exist(loadbalancer_id=%s)" % o.loadbalancer_id)

            except Exception as err:
                logger.error("Port information does not exist(instance_id=%d, network_id=%d)" % (o.instance_id, network.id))
        except Exception as err:
            logger.error("Network information does not exist")

        fields['loadbalancer'] = json.dumps(loadbalancer, indent=4)
       
        logger.info(">>>>> Loadbalancer")
        logger.info("%s" % json.dumps(loadbalancer, indent=4))

        try:
            listener = {}
            obj = Listener.objects.get(id=o.listener_id)
            listener['listener_name'] = obj.name
            listener['listener_id'] = obj.listener_id
            listener['protocol'] = obj.protocol
            listener['protocol_port'] = obj.protocol_port
            listener['stat_port'] = obj.stat_port
            listener['connection_limit'] = obj.connection_limit
            fields['listener'] = json.dumps(listener, indent=4)

            logger.info(">>>>> Listener")
            logger.info("%s" % json.dumps(listener, indent=4))
        except Exception as e:
            logger.log_exc("Listener.objects.get() failed - %s" % e)
            return None

        try:
            pool = {}
            obj = Pool.objects.get(id=o.pool_id)
            pool['pool_name'] = obj.name
            pool['pool_id'] = obj.pool_id
            pool['health_monitor_id'] = obj.health_monitor_id
            pool['lb_algorithm'] = obj.lb_algorithm
            pool['protocol'] = obj.protocol
            fields['pool'] = json.dumps(pool, indent=4)

            logger.info(">>>>> Pool")
            logger.info("%s" % json.dumps(pool, indent=4))
        except Exception as e:
            logger.log_exc("Pool.objects.get() failed - %s" % e)
            return None

        try:
            root_obj = {}
            member_list = []
            root_obj['members'] = member_list

            objs = Member.objects.filter(memberpool_id=o.pool_id)
            for obj in objs:
                member_obj = {}
                member_obj['member_id'] = obj.member_id
                member_obj['address'] = obj.address
                member_obj['protocol_port'] = obj.protocol_port
                member_obj['weight'] = obj.weight
                member_list.append(member_obj)

            fields['members'] = json.dumps(root_obj, indent=4)

            logger.info(">>>>> Members")
            logger.info("%s" % json.dumps(root_obj, indent=4))
        except Exception as e:
            logger.log_exc("Member.objects.get() failed - %s" % e)

        try:
            health_monitor = {}
            obj = Healthmonitor.objects.get(id=pool['health_monitor_id'])
            
            health_monitor['health_monitor_id'] = obj.health_monitor_id
            health_monitor['type'] = obj.type
            health_monitor['delay'] = obj.delay
            health_monitor['max_retries'] = obj.max_retries
            health_monitor['timeout'] = obj.timeout
            health_monitor['http_method'] = obj.http_method
            health_monitor['url_path'] = obj.url_path
            health_monitor['expected_codes'] = obj.expected_codes
            fields['health_monitor'] = json.dumps(health_monitor, indent=4)

            logger.info(">>>>> Healthmonitor")
            logger.info("%s" % json.dumps(health_monitor, indent=4))
        except Exception as e:
            logger.log_exc("Healthmonitor.objects.get() failed - %s" % e)

        logger.info("===============================================================")
        logger.info(">>> curl command for haproxy test")
        logger.info("curl %s:%s" % (loadbalancer['vip_address'], listener['protocol_port']))

        try:
            listener = Listener.objects.get(id=o.listener_id)
        except Exception as e:
            logger.log_exc("Listener.objects.get() failed - %s" % e)

        try:
            instance = Instance.objects.get(id=o.instance.id)
            instance.updated = time.time()
            instance.volumes = "/usr/local/etc/haproxy"
            userdata = "--publish-add %d:%d --publish-add %d:%d" \
                % (listener.protocol_port, listener.protocol_port, listener.stat_port, listener.stat_port)
            instance.userData = userdata
            instance.save()

        except Exception as e:
            logger.log_exc("Instance.objects.get() failed - %s" % e)
        
        fields = self.convert_unicode_to_str(fields)

        return fields

    def delete_record(self, port):
        # Nothing needs to be done to delete an lbaas; it goes away
        # when the instance holding the lbaas is deleted.
        pass
