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

def get_default_lb_service():
    lb_services = LbService.objects.all()
    if lb_services:
        return lb_services[0]
    return None

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class HealthSerializer(PlusModelSerializer):
    id = ReadOnlyField()

    class Meta:
        model = Healthmonitor
        fields = ('id', 'name', 'type', 'delay', 'max_retries', 'timeout', 'http_method', 'admin_state_up', 'url_path', 'expected_codes')

class HealthViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    base_name = "healthmonitors"
    method_name = "healthmonitors"
    method_kind = "viewset"
    queryset = Healthmonitor.objects.all()
    serializer_class = HealthSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(HealthViewSet, self).get_urlpatterns(api_path=api_path)

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

    def get_rsp_body(self, health_monitor_id):
        health = Healthmonitor.objects.get(health_monitor_id=health_monitor_id)

        root_obj = {}
        health_obj = {}
        pool_list = []
        pool_obj = {}
        root_obj['health_monitor'] = health_obj

        health_obj['id'] = health.id
        health_obj['name'] = health.name
        health_obj['admin_state_up'] = health.admin_state_up
        health_obj['delay'] = health.delay
        health_obj['expected_codes'] = health.expected_codes
        health_obj['max_retries'] = health.max_retries
        health_obj['http_method'] = health.http_method
        health_obj['timeout'] = health.timeout

        health_obj['pools'] = pool_list
        try:
            pool = Pool.objects.get(health_monitor_id=health.id)
            pool_obj['status'] = pool.status
            pool_obj['pool_id'] = pool.pool_id
            pool_list.append(pool_obj)
        except Exception as err:
            logger.error("%s (health_monitor_id=%s)" % (str(err), health_monitor_id))

        health_obj['url_path'] = health.url_path
        health_obj['type'] = health.type
        health_obj['health_monitor_id'] = health.health_monitor_id

        return root_obj, health_obj

    def update_health_info(self, health, request):
        required_flag = True
        if request.method == "POST":
            if not 'name' in request.data or request.data["name"]=="":
                required_flag = False
            if not 'delay' in request.data or request.data["delay"]=="":
                required_flag = False
            if not 'http_method' in request.data or request.data["http_method"]=="":
                required_flag = False
            if not 'max_retries' in request.data or request.data["max_retries"]=="":
                required_flag = False
            if not 'timeout' in request.data or request.data["timeout"]=="":
                required_flag = False
            if not 'type' in request.data or request.data["type"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'name' in request.data and request.data["name"]:
                health.name = request.data["name"]
            if 'admin_state_up' in request.data and request.data["admin_state_up"]:
                health.admin_state_up = request.data["admin_state_up"]
            if 'delay' in request.data and request.data["delay"]:
                health.delay = request.data["delay"]
            if 'expected_codes' in request.data and request.data["expected_codes"]:
                health.expected_codes = request.data["expected_codes"]
            if 'http_method' in request.data and request.data["http_method"]:
                health.http_method = request.data["http_method"]
            if 'max_retries' in request.data and request.data["max_retries"]:
                health.max_retries = request.data["max_retries"]
            if 'timeout' in request.data and request.data["timeout"]:
                health.timeout = request.data["timeout"]
            if 'type' in request.data and request.data["type"]:
                health.type = request.data["type"]
            if 'url_path' in request.data and request.data["url_path"]:
                health.url_path = request.data["url_path"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None

        health.save()
        return health

    def update_loadbalancer_model(self, health_monitor_id):
        health = Healthmonitor.objects.get(health_monitor_id=health_monitor_id)
        pools = Pool.objects.filter(health_monitor_id=health.id)
        
        for pool in pools:
            lbs = Loadbalancer.objects.filter(pool_id=pool.pool_id)
            for lb in lbs:
                lb.save()

            if lbs.count() == 0:
                logger.info("pool_id does not exist in Loadbalancer table (pool_id=%s)" % pool.pool_id)

        if pools.count() == 0:
            logger.info("health_monitor_id does not exist in Pool table (health_monitor_id=%s)" % health.id)

    # GET: /api/tenant/healthmonitors
    def list(self, request):
        self.print_message_log("REQ", request)
        queryset = self.filter_queryset(self.get_queryset())

        root_obj = {}
        health_list = []
        root_obj['health_monitors'] = health_list

        for health in queryset:
            temp_obj, health_obj = self.get_rsp_body(health.health_monitor_id)
            health_list.append(health_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/tenant/healthmonitors
    def create(self, request):
        self.print_message_log("REQ", request)

        health = Healthmonitor()
        health.health_monitor_id = str(uuid.uuid4())

        health = self.update_health_info(health, request)
        if health == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, health_obj = self.get_rsp_body(health.health_monitor_id)

        self.update_loadbalancer_model(health.health_monitor_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/tenant/healthmonitors/{health_monitor_id}
    def retrieve(self, request, pk=None):
        self.print_message_log("REQ", request)
        rsp_data, health_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/tenant/healthmonitors/{health_monitor_id}
    def update(self, request, pk=None):
        self.print_message_log("REQ", request)
        health = Healthmonitor.objects.get(health_monitor_id=pk)

        health = self.update_health_info(health, request)
        if health == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, health_obj = self.get_rsp_body(pk)

        self.update_loadbalancer_model(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/tenant/healthmonitors/{health_monitor_id}
    def destroy(self, request, pk=None):
        self.print_message_log("REQ", request)

        self.update_loadbalancer_model(pk)
        Healthmonitor.objects.filter(health_monitor_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)
