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

class ListenerSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    provider_service = serializers.PrimaryKeyRelatedField(queryset=LbService.objects.all(), default=get_default_lb_service)

    class Meta:
        model = Listener
        fields = ('id', 'provider_service', 'name', 'protocol', 'protocol_port', 'stat_port', 'admin_state_up', 'connection_limit', 'description')

class ListenerViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    base_name = "listeners"
    method_name = "listeners"
    method_kind = "viewset"
    queryset = Listener.objects.all()
    serializer_class = ListenerSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ListenerViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def print_message_log(self, msg_type, http):
        if msg_type == "REQ":
            logger.info("###################################################")
            logger.info("[Server] <--- ient]")
            logger.info("METHOD=%s" % http.method)
            logger.info("URI=%s" % http.path)
            logger.info("%s\n" % http.data)
        elif msg_type == "RSP":
            logger.info("[Server] ---> [Client]")
            logger.info("%s" % http)
            logger.info("Send http rsponse Success..\n")
        else:
            logger.error("Unvalid msg_type(%s)" % msg_type)

    def get_rsp_body(self, listener_id):
        listener = Listener.objects.get(listener_id=listener_id)

        root_obj = {}
        listener_obj = {}
        lb_obj_list = []
        root_obj['listener'] = listener_obj

        listener_obj['id'] = listener.id
        listener_obj['admin_state_up'] = listener.admin_state_up
        listener_obj['connection_limit'] = listener.connection_limit
        listener_obj['description'] = listener.description
        listener_obj['listener_id'] = listener.listener_id

        listener_obj['loadbalancers'] = lb_obj_list
        lbs = Loadbalancer.objects.filter(listener_id=listener.id)
        for lb in lbs:
            lb_obj = {}
            lb_obj['id'] = lb.loadbalancer_id
            lb_obj_list.append(lb_obj)

        listener_obj['name'] = listener.name
        listener_obj['protocol'] = listener.protocol
        listener_obj['protocol_port'] = listener.protocol_port
        listener_obj['stat_port'] = listener.stat_port

        return root_obj, listener_obj

    def update_listener_info(self, listener, request):
        required_flag = True
        if request.method == "POST":
            if not 'name' in request.data or request.data["name"]=="":
                required_flag = False
            if not 'protocol' in request.data or request.data["protocol"]=="":
                required_flag = False
            if not 'protocol_port' in request.data or request.data["protocol_port"]=="":
                required_flag = False
            if not 'stat_port' in request.data or request.data["stat_port"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'name' in request.data and request.data["name"]:
                listener.name = request.data["name"]
            if 'protocol' in request.data and request.data["protocol"]:
                listener.protocol = request.data["protocol"]
            if 'protocol_port' in request.data and request.data["protocol_port"]:
                listener.protocol_port = request.data["protocol_port"]
            if 'stat_port' in request.data and request.data["stat_port"]:
                listener.stat_port = request.data["stat_port"]
            if 'description' in request.data and request.data["description"]:
                listener.description = request.data["description"]
            if 'admin_state_up' in request.data and request.data["admin_state_up"]:
                listener.admin_state_up = request.data["admin_state_up"]
            if 'connection_limit' in request.data and request.data["connection_limit"]:
                listener.connection_limit = request.data["connection_limit"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None

        listener.save()
        return listener

    def update_loadbalancer_model(self, listener_id):
        listener = Listener.objects.get(listener_id=listener_id)
        lbs = Loadbalancer.objects.filter(listener_id=listener.id)
        for lb in lbs:
            lb.save()

        if lbs.count() == 0:
            logger.info("listener_id does not exist in Loadbalancer table (listener_id=%s)" % listener.id)

    # GET: /api/tenant/listeners
    def list(self, request):
        self.print_message_log("REQ", request)
        queryset = self.filter_queryset(self.get_queryset())

        root_obj = {}
        listener_obj_list = []
        root_obj['listeners'] = listener_obj_list

        for listener in queryset:
            temp_obj, listener_obj = self.get_rsp_body(listener.listener_id)
            listener_obj_list.append(listener_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/tenant/listeners
    def create(self, request):
        self.print_message_log("REQ", request)

        listener = Listener()
        listener.provider_service_id = request.data["provider_service"]
        listener.listener_id = str(uuid.uuid4())

        listener = self.update_listener_info(listener, request)
        if listener == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, listener_obj = self.get_rsp_body(listener.listener_id)

        self.update_loadbalancer_model(listener.listener_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/tenant/listeners/{listener_id}
    def retrieve(self, request, pk=None):
        self.print_message_log("REQ", request)
        rsp_data, listener_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/tenant/listeners/{listener_id}
    def update(self, request, pk=None):
        self.print_message_log("REQ", request)
        listener = Listener.objects.get(listener_id=pk)

        listener = self.update_listener_info(listener, request)
        if listener == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, listener_obj = self.get_rsp_body(pk)

        self.update_loadbalancer_model(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/tenant/listeners/{listener_id}
    def destroy(self, request, pk=None):
        self.print_message_log("REQ", request)

        self.update_loadbalancer_model(pk)
        Listener.objects.filter(listener_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)
