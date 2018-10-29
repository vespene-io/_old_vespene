#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from vespene.views import forms
from django.contrib.auth.models import Group
from vespene.views import BaseView

class GroupView(BaseView):
    model = Group
    form = forms.GroupForm
    view_prefix = 'group'
    object_label = 'Group'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Group.objects

    #@classmethod
    #def description_column(cls, obj):
    #    return obj.description

GroupView.extra_columns = [ 
    #('Description', SnippetView.description_column)
]