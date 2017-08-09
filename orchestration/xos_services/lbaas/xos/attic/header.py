# models.py -  LbService Models

from core.models import Service, XOSBase, TenantWithContainer
from django.db import transaction
from django.db.models import *

SERVICE_NAME = 'lbaas'
SERVICE_NAME_VERBOSE = 'LB-as-a-Service'
SERVICE_NAME_VERBOSE_PLURAL = 'LB-as-a-Services'
TENANT_NAME_VERBOSE = 'LoadBalancer'
TENANT_NAME_VERBOSE_PLURAL = 'LoadBalancers'
