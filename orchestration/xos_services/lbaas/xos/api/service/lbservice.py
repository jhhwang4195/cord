from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from django.conf.urls import patterns, url
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess
import uuid
from services.lbaas.models import LbService

from xos.logger import Logger, logging
logger = Logger(level=logging.INFO)

from rest_framework.authentication import *


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class LbServiceSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = LbService
            fields = ('humanReadableName', 'id', 'service_id', 'service_name')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

class LbServiceViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    base_name = "lbservices"
    method_name = "lbservices"
    method_kind = "viewset"
    queryset = LbService.objects.all()
    serializer_class = LbServiceSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(LbServiceViewSet, self).get_urlpatterns(api_path=api_path)

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

    def get_rsp_body(self, service_id):
        lb = LbService.objects.get(service_id=service_id)

        root_obj = {}
        lb_obj = {}
        root_obj['lbservice'] = lb_obj
        lb_obj['service_id'] = lb.service_id
        lb_obj['service_name'] = lb.service_name
        return root_obj, lb_obj

    def update_lb_info(self, lb, request):
        required_flag = True
        if request.method == "POST":
            if not 'service_name' in request.data or request.data["service_name"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'service_id' in request.data and request.data["service_id"]:
                lb.service_id = request.data["service_id"]
            if 'service_name' in request.data and request.data["service_name"]:
                lb.service_name = request.data["service_name"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None

        lb.save()
        return lb

    # GET: /api/service/lbservices/
    def list(self, request):
        self.print_message_log("REQ", request)
        object_list = self.filter_queryset(self.get_queryset())
        
        root_obj = {}
        lb_list = []
        root_obj['lbservices'] = lb_list

        for lb in object_list:
            temp_obj, lb_obj = self.get_rsp_body(lb.service_id)
            lb_list.append(lb_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/service/lbservices/
    def create(self, request):
        self.print_message_log("REQ", request)

        lbs = LbService.objects.filter(service_name=request.data["service_name"])
        if lbs.count() > 0:
            logger.error("The service_name already exists in the LbService table (service_name=%s)" % request.data["service_name"])
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        lb = LbService()
        lb.service_id = str(uuid.uuid4())

        lb = self.update_lb_info(lb, request)
        if lb == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, lb_obj = self.get_rsp_body(lb.service_id)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/service/lbservices/{service_id}
    def retrieve(self, request, pk=None):
        self.print_message_log("REQ", request)
        rsp_data, lb_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/service/lbservices/{service_id}
    def update(self, request, pk=None):
        self.print_message_log("REQ", request)
        try:
            lb = LbService.objects.get(service_id=pk)
        except Exception as err:
            logger.error("%s (service_id=%s)" % ((str(err), request.data["service_id"])))
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lb = self.update_lb_info(lb, request)
        if lb == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        rsp_data, health_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/service/lbservices/{service_id}
    def destroy(self, request, pk=None):
        self.print_message_log("REQ", request)
        LbService.objects.filter(service_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)
