# admin.py - LbService Django Admin

from core.admin import ReadOnlyAwareAdmin, SliceInline
from core.middleware import get_request
from core.models import User

from django import forms
from django.contrib import admin

from services.lbaas.models import *

class LbServiceForm(forms.ModelForm):

    class Meta:
        model = LbService
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LbServiceForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['service_id'].initial = self.instance.service_id
            self.fields['service_name'].initial = self.instance.service_name

    def save(self, commit=True):
        self.instance.service_id = self.cleaned_data.get('service_id')
        self.instance.service_name = self.cleaned_data.get('service_name')
        return super(LbServiceForm, self).save(commit=commit)

class LbServiceAdmin(ReadOnlyAwareAdmin):

    model = LbService
    verbose_name = SERVICE_NAME_VERBOSE
    verbose_name_plural = SERVICE_NAME_VERBOSE_PLURAL
    form = LbServiceForm
    inlines = [SliceInline]

    list_display = ('backend_status_icon', 'name', 'service_id', 'service_name', 'enabled')
    list_display_links = ('backend_status_icon', 'name', 'service_id', 'service_name' )

    fieldsets = [(None, {
        'fields': ['backend_status_text', 'name', 'enabled', 'versionNumber', 'service_id', 'service_name', 'description',],
        'classes':['suit-tab suit-tab-general',],
        })]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['name', 'enabled', 'versionNumber', 'description',]

    extracontext_registered_admins = True

    suit_form_tabs = (
        ('general', 'Lb Service Details', ),
        ('slices', 'Slices',),
        )

    suit_form_includes = ((
        'top',
        'administration'),
        )

    def get_queryset(self, request):
        return LbService.select_by_user(request.user)

admin.site.register(LbService, LbServiceAdmin)

class LoadbalancerForm(forms.ModelForm):

    class Meta:
        model = Loadbalancer
        fields = '__all__'

    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        super(LoadbalancerForm, self).__init__(*args, **kwargs)

        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['kind'].initial = SERVICE_NAME

        self.fields['provider_service'].queryset = LbService.objects.all()

        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields['loadbalancer_id'].initial = self.instance.loadbalancer_id
            self.fields['listener_id'].initial = self.instance.listener_id
            self.fields['pool_id'].initial = self.instance.pool_id
            self.fields['lb_name'].initial = self.instance.lb_name
            self.fields['description'].initial = self.instance.description
            self.fields['vip_subnet_id'].initial = self.instance.vip_subnet_id
            self.fields['vip_address'].initial = self.instance.vip_address
            self.fields['admin_state_up'].initial = self.instance.admin_state_up

        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            if LbService.objects.exists():
                self.fields['provider_service'].initial = LbService.objects.all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get('creator')
        self.instance.loadbalancer_id = self.cleaned_data.get('loadbalancer_id')
        self.instance.listener_id = self.cleaned_data.get('listener_id')
        self.instance.pool_id = self.cleaned_data.get('pool_id')
        self.instance.lb_name = self.cleaned_data.get('lb_name')
        self.instance.description = self.cleaned_data.get('description')
        self.instance.vip_subnet_id = self.cleaned_data.get('vip_subnet_id')
        self.instance.vip_address = self.cleaned_data.get('vip_address')
        self.instance.admin_state_up = self.cleaned_data.get('admin_state_up')

        return super(LoadbalancerForm, self).save(commit=commit)

class LoadbalancerAdmin(ReadOnlyAwareAdmin):

    verbose_name = TENANT_NAME_VERBOSE
    verbose_name_plural = TENANT_NAME_VERBOSE_PLURAL

    list_display = ('id', 'backend_status_icon', 'instance', 'loadbalancer_id', 'listener_id', 'pool_id', 'lb_name', 'vip_subnet_id', 'vip_address', 'description', 'admin_state_up')
    list_display_links = ('backend_status_icon', 'instance', 'loadbalancer_id', 'listener_id', 'pool_id', 'lb_name', 'vip_subnet_id', 'vip_address', 'description', 'admin_state_up', 'id')

    fieldsets = [(None, {
        'fields': ['backend_status_text', 'kind', 'provider_service', 'instance', 'creator', 'loadbalancer_id', 'listener_id', 'pool_id', 'lb_name', 'vip_subnet_id', 'vip_address', 'description', 'admin_state_up'],
        'classes': ['suit-tab suit-tab-general'],
        })]


    readonly_fields = ('backend_status_text', 'instance',)

    form = LoadbalancerForm

    suit_form_tabs = (('general', 'Details'),)

    def get_queryset(self, request):
        return Loadbalancer.select_by_user(request.user)

admin.site.register(Loadbalancer, LoadbalancerAdmin)
