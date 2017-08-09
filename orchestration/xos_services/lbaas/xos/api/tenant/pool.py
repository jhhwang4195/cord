from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

from xos.logger import Logger, logging
logger = Logger(level=logging.INFO)

from rest_framework.authentication import *

from services.lbaas.models import LbService, Loadbalancer, Listener, Pool, Member, Healthmonitor

import json
import uuid
import traceback

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

def get_default_lb_service():
    lb_services = LbService.objects.all()
    if lb_services:
        return lb_services[0]
    return None

def update_pool_status(pool_id):
    pool_status = ""

    pool = Pool.objects.get(pool_id=pool_id)
    members = Member.objects.filter(memberpool=pool.id)
    if members.count() > 0:
        try:
            pool = Pool.objects.get(pool_id=pool_id)
        except Exception as err:
            logger.error("%s (pool_id=%s)" % ((str(err), request.data["pool_id"])))
            pool_status = "PENDING_CREATE"

        healths = Healthmonitor.objects.filter(id=pool.health_monitor_id)
        if healths.count() > 0:
            pool_status = "ACTIVE"
        else:
            logger.error("Healthmonitor information does not exist (pool_id=%s)" % pool_id)
            pool_status = "PENDING_CREATE"
    else:
        logger.error("Member information does not exist (pool_id=%s)" % pool.id)
        pool_status = "PENDING_CREATE"

    pool = Pool.objects.get(pool_id=pool_id)
    pool.status = pool_status
    pool.save()

    return pool.status

class PoolSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    provider_service = serializers.PrimaryKeyRelatedField(queryset=LbService.objects.all(), default=get_default_lb_service)

    class Meta:
        model = Pool
        fields = ('id', 'provider_service', 'name', 'subnet_id', 'health_monitor', 'lb_algorithm', 'protocol', 'description', 'admin_state_up')


class PoolViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    base_name = "pools"
    method_name = "pools"
    method_kind = "viewset"
    queryset = Pool.objects.all()
    serializer_class = PoolSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(PoolViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def print_message_log(self, msg_type, http):
        if msg_type == "REQ":
            logger.info("###################################################")
            logger.info("[Server] <--- [Client]")
            logger.info("METHOD=%s" % http.method)
            logger.info("URI=%s" % http.path)
            logger.info("%s\n" % http.data)
        elif msg_type == "RSP":
            logger.info("[Server] ---> [Client]")
            logger.info("%s" % http)
            logger.info("Send http rsponse Success..\n")
        else:
            logger.error("Unvalid msg_type(%s)" % msg_type)

    def get_rsp_body(self, pool_id):
        update_pool_status(pool_id)

        pool = Pool.objects.get(pool_id=pool_id)

        root_obj = {}
        pool_obj = {}
        health_list = []
        member_list = []
        health_status_list = []
        root_obj['pool'] = pool_obj

        pool_obj['id'] = pool.id
        pool_obj['status'] = pool.status
        pool_obj['lb_algorithm'] = pool.lb_algorithm
        pool_obj['protocol'] = pool.protocol
        pool_obj['description'] = pool.description

        pool_obj['members'] = member_list
        members = Member.objects.filter(memberpool=pool.id)
        for member in members:
            member_list.append(member.member_id)

        pool_obj['pool_id'] = pool.pool_id
        pool_obj['name'] = pool.name
        pool_obj['admin_state_up'] = pool.admin_state_up
        pool_obj['subnet_id'] = pool.subnet_id
        
        pool_obj['health_monitors'] = health_list
        health_list.append(pool.health_monitor.health_monitor_id)

        pool_obj['health_monitors_status'] = health_status_list
        healths = Healthmonitor.objects.filter(id=pool.health_monitor_id)
        for health in healths:
            health_status_obj = {}
            health_status_obj['monitor_id'] = health.health_monitor_id
            health_status_obj['status'] = "ACTIVE"
            health_status_obj['status_description'] = None
            health_status_list.append(health_status_obj)

        pool_obj['provider'] = "haproxy"

        return root_obj, pool_obj

    def update_pool_info(self, pool, request):
        required_flag = True
        if request.method == "POST":
            if not 'lb_algorithm' in request.data or request.data["lb_algorithm"]=="":
                required_flag = False
            if not 'health_monitor_id' in request.data or request.data["health_monitor_id"]=="":
                required_flag = False
            if not 'name' in request.data or request.data["name"]=="":
                required_flag = False
            if not 'protocol' in request.data or request.data["protocol"]=="":
                required_flag = False
            if not 'subnet_id' in request.data or request.data["subnet_id"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'name' in request.data and request.data["name"]:
                pool.name = request.data["name"]
            if 'subnet_id' in request.data and request.data["subnet_id"]:
                pool.subnet_id = request.data["subnet_id"]
            if 'health_monitor_id' in request.data and request.data["health_monitor_id"]:
                pool.health_monitor_id = request.data["health_monitor_id"]
            if 'lb_algorithm' in request.data and request.data["lb_algorithm"]:
                pool.lb_algorithm = request.data["lb_algorithm"]
            if 'description' in request.data and request.data["description"]:
                pool.description = request.data["description"]
            if 'protocol' in request.data and request.data["protocol"]:
                pool.protocol = request.data["protocol"]
            if 'admin_state_up' in request.data and request.data["admin_state_up"]:
                pool.admin_state_up = request.data["admin_state_up"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None
        
        pool.save()
        return pool

    def update_loadbalancer_model(self, pool_id):
        pool = Pool.objects.get(pool_id=pool_id)
        lbs = Loadbalancer.objects.filter(pool_id=pool.id)
        for lb in lbs:
            lb.save()

        if lbs.count() == 0:
            logger.info("pool_id does not exist in Loadbalancer table (pool_id=%s)" % pool.id)

    # GET: /api/tenant/pools
    def list(self, request):
        self.print_message_log("REQ", request)
        queryset = self.filter_queryset(self.get_queryset())

        root_obj = {}
        pool_list = []
        root_obj['pools'] = pool_list

        for pool in queryset:
            temp_obj, pool_obj = self.get_rsp_body(pool.pool_id)
            pool_list.append(pool_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/tenant/pools
    def create(self, request):
        self.print_message_log("REQ", request)

        try:
            health = Healthmonitor.objects.get(id=request.data["health_monitor_id"])
        except Exception as err:
            logger.error("%s (health_monitor_id=%s)" % ((str(err), request.data["health_monitor_id"])))
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pool = Pool()
        pool.provider_service_id = request.data["provider_service"]
        pool.pool_id = str(uuid.uuid4())

        pool = self.update_pool_info(pool, request)
        if pool == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        rsp_data, pool_obj = self.get_rsp_body(pool.pool_id)

        self.update_loadbalancer_model(pool.pool_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/tenant/pools/{pool_id}
    def retrieve(self, request, pk=None):
        self.print_message_log("REQ", request)
        rsp_data, pool_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/tenant/pools/{pool_id}
    def update(self, request, pk=None):
        self.print_message_log("REQ", request)
        pool = Pool.objects.get(pool_id=pk)

        pool = self.update_pool_info(pool, request)
        if pool == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, pool_obj = self.get_rsp_body(pk)

        self.update_loadbalancer_model(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/tenant/pools/{pool_id}
    def destroy(self, request, pk=None):
        self.print_message_log("REQ", request)

        self.update_loadbalancer_model(pk)
        Pool.objects.filter(pool_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)



class MemberSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    provider_service = serializers.PrimaryKeyRelatedField(queryset=LbService.objects.all(), default=get_default_lb_service)

    class Meta:
        model = Member
        fields = ('id', 'provider_service', 'memberpool', 'address', 'protocol_port', 'subnet_id', 'weight', 'admin_state_up')

class MemberViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    base_name = "pools"
    method_name = "pools/(?P<pool_id>[a-zA-Z0-9\-_]+)/members"
    method_kind = "viewset" 
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(MemberViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def print_message_log(self, msg_type, http):
        if msg_type == "REQ":
            logger.info("###################################################")
            logger.info("[Server] <--- [Client]")
            logger.info("METHOD=%s" % http.method)
            logger.info("URI=%s" % http.path)
            logger.info("%s\n" % http.data)
        elif msg_type == "RSP":
            logger.info("[Server] ---> [Client]")
            logger.info("%s" % http)
            logger.info("Send http rsponse Success..\n")
        else:
            logger.error("Unvalid msg_type(%s)" % msg_type)

    def get_rsp_body(self, member_id):
        member = Member.objects.get(member_id=member_id)

        root_obj = {}
        member_obj = {}
        root_obj['member'] = member_obj

        member_obj['member_id'] = member.member_id
        member_obj['address'] = member.address
        member_obj['admin_state_up'] = member.admin_state_up
        member_obj['protocol_port'] = member.protocol_port

        try:
            pool = Pool.objects.get(id=member.memberpool_id)
            member_obj['subnet_id'] = pool.subnet_id
        except Exception as err:
            logger.error("%s (memberpool_id=%s)" % ((str(err), member.memberpool_id)))
            member_obj['subnet_id'] = None

        member_obj['weight'] = member.weight

        return root_obj, member_obj

    def update_member_info(self, member, request):
        required_flag = True
        if request.method == "POST":
            if not 'memberpool' in request.data or request.data["memberpool"]=="":
                required_flag = False
            if not 'address' in request.data or request.data["address"]=="":
                required_flag = False
            if not 'protocol_port' in request.data or request.data["protocol_port"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'memberpool' in request.data and request.data["memberpool"]:
                member.memberpool_id = request.data["memberpool"]
            if 'address' in request.data and request.data["address"]:
                member.address = request.data["address"]
            if 'protocol_port' in request.data and request.data["protocol_port"]:
                member.protocol_port = request.data["protocol_port"]
            if 'subnet_id' in request.data and request.data["subnet_id"]:
                member.subnet_id = request.data["subnet_id"]
            if 'weight' in request.data and request.data["weight"]:
                member.weight = request.data["weight"]
            if 'admin_state_up' in request.data and request.data["admin_state_up"]:
                member.admin_state_up = request.data["admin_state_up"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None

        member.save()
        return member

    def update_loadbalancer_model(self, pool_id):
        pool = Pool.objects.get(pool_id=pool_id)
        lbs = Loadbalancer.objects.filter(pool=pool.id)
        for lb in lbs:
            lb.save()
        
        if lbs.count() == 0:
            logger.info("pool_id does not exist in Loadbalancer table (pool_id=%s)" % pool.id)

    # GET: /api/tenant/pools/{pool_id}/members
    def list(self, request, pool_id=None):
        self.print_message_log("REQ", request)
        pool = Pool.objects.get(pool_id=pool_id)
        queryset = Member.objects.filter(memberpool=pool.id)

        root_obj = {}
        member_list = []
        root_obj['members'] = member_list

        for member in queryset:
            temp_obj, member_obj = self.get_rsp_body(member.member_id)
            member_list.append(member_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/tenant/pools/{pool_id}/members
    def create(self, request, pool_id=None):
        self.print_message_log("REQ", request)

        # Check whether the pool_id exists in the Pool table
        try:
            pool = Pool.objects.get(id=request.data["memberpool"])
        except Exception as err:
            logger.error("%s (memberpool_id=%s)" % ((str(err), request.data["memberpool"])))
            return Response(status=status.HTTP_400_BAD_REQUEST)

        member = Member()
        member.provider_service_id = request.data["provider_service"]
        member.member_id = str(uuid.uuid4())
        member.operating_status = "ONLINE"
        member.provisioning_status = "ACTIVE"

        member = self.update_member_info(member, request)
        if member == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, member_obj = self.get_rsp_body(member.member_id)

        update_pool_status(member.memberpool.pool_id)
        self.update_loadbalancer_model(member.memberpool.pool_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/tenant/pools/{pool_id}/members/{member_id}
    def retrieve(self, request, pool_id=None, pk=None):
        self.print_message_log("REQ", request)
        rsp_data, member_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/tenant/pools/{pool_id}/members/{member_id}
    def update(self, request, pool_id=None, pk=None):
        self.print_message_log("REQ", request)
        member = Member.objects.get(member_id=pk)

        member = self.update_member_info(member, request)
        if member == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, member_obj = self.get_rsp_body(pk)
 
        self.update_loadbalancer_model(pool_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/tenant/pools/{pool_id}/members/{member_id}
    def destroy(self, request, pool_id=None, pk=None):
        self.print_message_log("REQ", request)

        update_pool_status(pool_id)
        self.update_loadbalancer_model(pool_id)

        Member.objects.filter(member_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)
