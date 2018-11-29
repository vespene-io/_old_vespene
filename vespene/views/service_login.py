#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0


from vespene.views import forms
from vespene.models.service_login import ServiceLogin
from vespene.views import BaseView

class ServiceLoginView(BaseView):
    model = ServiceLogin
    form = forms.ServiceLoginForm
    view_prefix = 'service_login'
    object_label = 'Service Login'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return ServiceLogin.objects    

ServiceLoginView.extra_columns = []