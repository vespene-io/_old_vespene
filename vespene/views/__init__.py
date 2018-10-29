#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  --------------------------------------------------------------------------
#  __init__.py - common code for all view subclasses and a few top level
#  view routes, which we want to minimize
#  --------------------------------------------------------------------------

import traceback
from urllib.parse import parse_qs

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from vespene.views import forms
from vespene.common.logger import Logger
from vespene.manager.permissions import PermissionsManager
from vespene.views.view_helpers import (generic_delete, generic_detail,
                                  generic_edit, generic_list, generic_new)
from vespene.manager.webhooks import Webhooks

LOG = Logger()
permissions = PermissionsManager()

class BaseView(object):
    """
    Base class for all object-type view configurations.  
    Vespene uses this class structure to make it easier to build new views without construction
    of a lot of extra CRUD functions and templates.
    """

    extra_columns = []        # extra columns are inserted in between id and edit/delete controls
    model = None              # Django Model for this object type
    form = forms.ProjectForm  # Django form for processing this object type
    view_prefix = 'project'   # all view methods start with this prefix
    object_label = 'Project'  # capitilized singular name for this object type
    supports_new = True       # is any kind of addition allowed?
    supports_edit = True      # is any kind of editing allowed?
    supports_delete = True    # is any kind of deletion allowed?

    def get_queryset(cls, request):
        """
        Return the basic queryset for this object type, for instance 
        ProjectView would return Project.objects.all()
        """
        raise NotImplementedError()

    @classmethod
    def edit(cls, request, *args, **kwargs):
        """
        Renders edit templates and processes form submissions.
        Shouldn't have to override this.
        """
        return generic_edit(cls, request, *args, **kwargs)

    @classmethod
    def new(cls, request, *args, **kwargs):
        """
        Renders creation templates and processes form submissions.
        Shouldn't have to override this.
        """
        return generic_new(cls, request, *args, **kwargs)

    @classmethod
    def list(cls, request, *args, **kwargs):
        """
        Renders list templates and processes form submissions.
        Shouldn't have to override this.
        """
        return generic_list(cls, request, *args, **kwargs)

    @classmethod
    def delete(cls, request, *args, **kwargs):
        """
        Renders deletion templates and processes form submissions.
        Shouldn't have to override this.
        """
        return generic_delete(cls, request, *args, **kwargs)

    @classmethod
    def detail(cls, request, *args, **kwargs):
        """
        Renders detail templates (basically read-only edit views) and processes form submissions.
        Shouldn't have to override this.
        """
        return generic_detail(cls, request, *args, **kwargs)

    @classmethod
    def ordering(cls, queryset):
        """
        Returns the queryset in the default sort order
        """
        return queryset.order_by('name')

    @classmethod
    def filtering(cls, request, queryset):
        """
        Filters the queryset to remove anything the user shouldn't be able to see.
        This does not mean the object type can't be selected in other forms, but it does mean users can't see any details and
        that the objects will now show up in a list view. The default behavior is to not filter anything.
        """
        return queryset

    @classmethod
    def name_cell(cls, obj):
        """
        How should the object be displayed in the first column of a list view?
        """
        return obj.name  

    @classmethod
    def finalize(cls, request, obj, create=True):
        # when saving this object via form submissions, should any post-processing be performed?
        return obj


#========================================================================================================

@csrf_exempt
def webhook_post(request, *args, **kwargs):
    """
    Receive an incoming webhook and potentially trigger a build using
    the code in webhooks.py
    """

    if request.method != 'POST':
        return redirect('index')

    try:
        query = parse_qs(request.META['QUERY_STRING'])
        token = query.get('token', None)
        if token is not None:
            token = token[0]
        Webhooks(request, token).handle()
    except Exception as e:
        traceback.print_exc()
        LOG.error("error processing webhook: %s" % str(e))
        return HttpResponseServerError("webhook processing error")

    return HttpResponse("ok", content_type="text/plain")

#========================================================================================================

def index(request): 
    if request.user.is_anonymous:
        return redirect("login")
    return redirect("project_list")