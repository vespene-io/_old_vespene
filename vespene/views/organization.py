#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

import json
import traceback
from django.shortcuts import get_object_or_404, redirect
from django.http.response import HttpResponse, HttpResponseServerError
from vespene.views import forms
from vespene.models.organization import Organization
from vespene.manager.permissions import PermissionsManager
from vespene.manager.jobkick import start_project_from_ui
from vespene.views.view_helpers import (build_status_icon, get_context, icon, link, project_controls_icon, template)
from vespene.views import BaseView

permissions = PermissionsManager()

class OrganizationView(BaseView):
    """
    View configuration for the Project model.
    Projects are fairly editable, and also offer stop/stop navigation for builds.
    """

    model = Organization
    form = forms.OrganizationForm
    view_prefix = 'organization'
    object_label = 'Organization'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Organization.objects.prefetch_related('last_build', 'active_build', 'last_successful_build')

    @classmethod
    def last_build_column(cls, obj):
        return build_status_icon(obj.last_build, include_buildroot_link=False)

    @classmethod
    def active_build_column(cls, obj):
        return build_status_icon(obj.last_build, include_buildroot_link=False)

    @classmethod
    def last_successful_build_column(cls, obj):
        return build_status_icon(obj.last_successful_build, include_buildroot_link=False)

OrganizationView.extra_columns = [
    ('Active Import', OrganizationView.active_build_column),
    ('Last Import', OrganizationView.last_build_column),
    ('Last Successful Import', OrganizationView.last_successful_build_column),
]