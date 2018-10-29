#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from vespene.views import forms
from vespene.manager.jobkick import stop_build_from_ui
from vespene.models.build import Build
from vespene.manager.permissions import PermissionsManager
from vespene.views.view_helpers import (guard_none, build_control_icon, build_status_icon,
                                  format_time, link, build_root_link)
from vespene.views import BaseView

permissions = PermissionsManager()

#  --------------------------------------------------------------------------
#  __init__.py - common code for all view subclasses and a few top level
#  view routes, which we want to minimize
#  --------------------------------------------------------------------------

class BuildView(BaseView):
    """
    View configuration for the Build model.
    Builds cannot be edited from the main UI, but can be stopped.
    """

    model = Build
    form = forms.BuildForm
    view_prefix = 'build'
    object_label = 'Build'

    supports_new = False
    supports_edit = False
    supports_delete = False

    @classmethod
    def get_queryset(cls, request):
        return Build.objects.prefetch_related('project')
  
    @classmethod
    def name_cell(cls, obj):
        # the builds are just numbered by the database ID
        return build_status_icon(obj, compact=False)

    @classmethod
    def status_column(cls, obj):
        # explain the status in text
        return obj.explain_status()

    @classmethod
    def root_column(cls, obj):
        return build_root_link(obj)

    @classmethod
    def revision_column(cls, obj):
        # display the revision from source code if associated from a repo
        return guard_none(obj.revision)
        
    @classmethod
    def revision_username(cls, obj):
        return guard_none(obj.revision_username)

    @classmethod
    def start_column(cls, obj):
        # when did this build start?
        return format_time(obj.start_time)

    @classmethod
    def end_column(cls, obj):
        # when did this build finish?
        return format_time(obj.end_time)

    @classmethod
    def controls_column(cls, obj):
        # show links to stop this build, if it is running
        return build_control_icon(obj)  

    @classmethod
    def project_column(cls, obj):
        # link to the project detail page for this build
        project = obj.project
        if project:
            return link("/ui/projects/%s/detail" % project.id, project.name)
        return "import"

    @classmethod
    def ordering(cls, queryset):
        return queryset.order_by('-id')  

    @classmethod
    def build_stop(cls, request, *args, **kwargs):  
        """
        A POST endpoint that stops a build.
        """
        if request.method != "POST":
            raise Exception('invalid method')
        try:
            qs = permissions.filter_queryset_for_view(Build.objects, request, *args, **kwargs)
            obj = get_object_or_404(qs, pk=kwargs.get('pk'))
            if not permissions.check_can_stop(obj, request, *args, **kwargs):
                raise PermissionDenied()
            stop_build_from_ui(request, obj)
            return HttpResponse("ok", content_type="text/plain")
        except Exception as e:
            return HttpResponseServerError(e)

    @classmethod
    def duration_column(cls, obj):
        """
        How long has the build been running?
        """
        d = obj.duration()
        if d is None:
            return "-"
        else:
            return "%.1f" % (d.seconds / 60)

    @classmethod
    def pool_column(cls, obj):
        pool = obj.worker_pool
        return link("/ui/worker_pools/%s/detail" % pool.id, pool.name)


BuildView.extra_columns = [
    ('Status', BuildView.status_column),
    ('Build Root', BuildView.root_column),
    ('Project', BuildView.project_column),
    ('Worker Pool', BuildView.pool_column),
    ('Controls', BuildView.controls_column),
    ('Revision', BuildView.revision_column),
    ('Revision User', BuildView.revision_username),
    ('Start', BuildView.start_column),
    ('End', BuildView.end_column),
    ('Run Time (minutes)', BuildView.duration_column)
]