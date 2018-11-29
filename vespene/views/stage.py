#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0

from vespene.views import forms
from vespene.models.stage import Stage
from vespene.views import BaseView

class StageView(BaseView):
    model = Stage
    form = forms.StageForm
    view_prefix = 'stage'
    object_label = 'Stage'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Stage.objects    

StageView.extra_columns = []