#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

import json
import traceback
from django.shortcuts import get_object_or_404, redirect
from django.http.response import HttpResponse, HttpResponseServerError
from vespene.views import forms
from vespene.models.project import Project
from vespene.manager.permissions import PermissionsManager
from vespene.manager.jobkick import start_project_from_ui
from vespene.views.view_helpers import (build_status_icon, get_context, icon, link, project_controls_icon, template)
from vespene.views import BaseView

permissions = PermissionsManager()

class ProjectView(BaseView):
    """
    View configuration for the Project model.
    Projects are fairly editable, and also offer stop/stop navigation for builds.
    """

    model = Project
    form = forms.ProjectForm
    view_prefix = 'project'
    object_label = 'Project'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Project.objects.prefetch_related('last_build', 'active_build', 'last_successful_build')

    @classmethod
    def build_history_column(cls, obj):
        """
        The builds column shows a link to the history of past builds, as well as the status
        of the last build.  The controls icon is a play/stop button for the project, and appears
        conditionally based on whether there is an active build.
        """
        all_link = "/ui/builds?project_id=%s" % obj.id
        all_icon = link(all_link, icon('fa-list-alt', '', tooltip='Build History'))
        return all_icon

    @classmethod
    def controls_column(cls, obj):
        return project_controls_icon(obj, obj.active_build, compact=False)

    @classmethod
    def last_build_column(cls, obj):
        return build_status_icon(obj.last_build, include_buildroot_link=True)

    @classmethod
    def last_successful_build_column(cls, obj):
        return build_status_icon(obj.last_successful_build, include_buildroot_link=True)

    @classmethod
    def pipeline_column(cls, obj):
        """
        If the project is part of a pipeline, we'll show it here with a link to the map
        view to the pipeline, as well as the pipeline name and stage name.
        """
        if not obj.pipeline:
            return "-"
        map_link = icon('fa-empty-circle', family='fas', tooltip='None')
        my_link = "/ui/pipelines/%s/map" % obj.pipeline.id
        my_icon = icon('fa-map', family='fas', tooltip='Map View')
        map_link = link(my_link, my_icon)
            # we don't want to do database lookups here so not checking permissions
            # in future UI upgrades we may have an "edit" button on the detail page
        my_link2  = "/ui/pipelines/%s/detail" % obj.pipeline.id
        pipeline_link = link(my_link2, obj.pipeline.name)
        return "%s %s" % (map_link, pipeline_link)

    @classmethod 
    def stage_column(cls, obj):
        if obj.stage is None:
            return "-"
        my_link = "/ui/stages/%s/detail" % obj.stage.pk
        return link(my_link, obj.stage.name)

    @classmethod
    def project_start_prompt(cls, request, *args, **kwargs):
        """
        This is a POST entry point for when the project has "launch questions" enabled.
        Instead of just kicking off the project, we'll present a page of questions, and
        then inject the results of those questions into the build variables. This is
        covered in the web docs.
        """
        if request.method == "POST":
            # TODO: reduce duplication with start_project and elsewhere
            try:
                qs = permissions.filter_queryset_for_view(Project.objects, request, *args, **kwargs)
                obj = get_object_or_404(qs, pk=kwargs.get('pk'))
                if not permissions.check_can_start(obj, request, *args, **kwargs):
                    raise Exception("insufficient permissions")
                start_project_from_ui(request, obj)
                return redirect('index')
            except Exception as e:
                if str(e) == "insufficient permissions":
                    # TODO: custom exception type catching instead
                    return HttpResponseServerError(str(e))
                else:
                    return HttpResponseServerError(traceback.format_exc())
        else:
            qs = permissions.filter_queryset_for_view(Project.objects, request, *args, **kwargs)
            obj = get_object_or_404(qs, pk=kwargs.get('pk'))
            if not obj.has_launch_questions():
                # user manually constructed this URL?
                raise Exception("this project has no launch questions")
            if not permissions.check_can_start(obj, request, *args, **kwargs):
                # TODO: fix exception type and raise 403
                raise Exception("insufficient permissions")
            if not permissions.check_can_start(obj, request, *args, **kwargs):
                return redirect('index')
            try:
                launch_questions = json.loads(obj.launch_questions)
            except:
                raise Exception("failed to parse launch question specification: %s" % launch_questions)
            context = get_context(request, questions=launch_questions, cfg=cls, obj=obj)
            return template(request, 'project_start_prompt.j2', context)

    @classmethod
    def project_start(cls, request, *args, **kwargs):
        """
        If the project doesn't have launch questions, we'll just launch the project.
        """
        if request.method != "POST":
            raise Exception('invalid')
        try:
            qs = permissions.filter_queryset_for_view(Project.objects, request, *args, **kwargs)
            obj = get_object_or_404(qs, pk=kwargs.get('pk'))
            if not permissions.check_can_start(obj, request, *args, **kwargs):
                # TODO: fix exception type and raise 403
                raise Exception("insufficient permissions")
            if obj.has_launch_questions():
                # the UI doesn't render this page in this scenario, so just a safeguard
                raise Exception("this project has launch questions")
            start_project_from_ui(request, obj)
            return HttpResponse("ok", content_type="text/plain")
        except Exception as e:
            if str(e) == "insufficient permissions":
                # TODO: custom exception type catching instead
                return HttpResponseServerError(str(e))
            else:
                return HttpResponseServerError(traceback.format_exc())

    @classmethod
    def project_stop(cls, request, *args, **kwargs): 
        """
        POST endpoint that puts in a request to stop the project.
        """
        if request.method != "POST":
            raise Exception('invalid')
        try:
            qs = permissions.filter_queryset_for_view(Project.objects, request, *args, **kwargs)
            obj = get_object_or_404(qs, pk=kwargs.get('pk'))
            if not permissions.check_can_start(obj, request, *args, **kwargs):
                # TODO: fix exception type and raise 403
                raise Exception("insufficient permissions")  
            stop_project_from_ui(request, obj)
            return HttpResponse("ok", content_type="text/plain")
        except Exception as e:
            traceback.print_exc()
            return HttpResponseServerError(e)

ProjectView.extra_columns = [
    ('Controls', ProjectView.controls_column),
    ('Last', ProjectView.last_build_column),
    ('Last Successful', ProjectView.last_successful_build_column),
    ('History', ProjectView.build_history_column),
    ('Pipeline', ProjectView.pipeline_column),
    ('Stage', ProjectView.stage_column)
]