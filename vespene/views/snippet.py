#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from vespene.views import forms
from vespene.models.snippet import Snippet
from vespene.views import BaseView
import html

class SnippetView(BaseView):
    model = Snippet
    form = forms.SnippetForm
    view_prefix = 'snippet'
    object_label = 'Snippet'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Snippet.objects

    @classmethod
    def description_column(cls, obj):
        return html.escape(obj.description)

SnippetView.extra_columns = [ 
    ('Description', SnippetView.description_column)
]