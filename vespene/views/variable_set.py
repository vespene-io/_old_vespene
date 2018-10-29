#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause


from vespene.views import forms
from vespene.models.variable_set import VariableSet
from vespene.views import BaseView

class VariableSetView(BaseView):
    model = VariableSet
    form = forms.VariableSetForm
    view_prefix = 'variable_set'
    object_label = 'Variable Set'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return VariableSet.objects

    @classmethod
    def description_column(cls, obj):
        return obj.description

VariableSetView.extra_columns = [ 
    ('Description', VariableSetView.description_column)
]
