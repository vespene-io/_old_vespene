#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from vespene.views import forms
from vespene.models.worker_pool import WorkerPool
from vespene.views import BaseView

class WorkerPoolView(BaseView):
    model = WorkerPool
    form = forms.WorkerPoolForm
    view_prefix = 'worker_pool'
    object_label = 'Worker Pool'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return WorkerPool.objects

WorkerPoolView.extra_columns = []