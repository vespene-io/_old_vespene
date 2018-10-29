#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from vespene.views import forms
from django.contrib.auth.models import User
from vespene.views import BaseView

class UserView(BaseView):
    model = User
    form = forms.UserForm
    view_prefix = 'user'
    object_label = 'User'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def name_cell(cls, obj):
        return obj.username

    @classmethod
    def ordering(cls, queryset):
        """
        Returns the queryset in the default sort order
        """
        return queryset.order_by('username')

    @classmethod
    def get_queryset(cls, request):
        return User.objects

    #@classmethod
    #def description_column(cls, obj):
    #    return obj.description

UserView.extra_columns = [ 
    #('Description', SnippetView.description_column)
]