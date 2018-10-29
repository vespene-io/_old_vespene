#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from vespene.views import forms
from vespene.models.ssh_key import SshKey
from vespene.views import BaseView

class SshKeyView(BaseView):
    model = SshKey
    form = forms.SshKeyForm
    view_prefix = 'ssh_key'
    object_label = 'SSH Key'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return SshKey.objects    

SshKeyView.extra_columns = []