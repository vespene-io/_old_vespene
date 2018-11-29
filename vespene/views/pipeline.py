#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0

from django.shortcuts import get_object_or_404
from vespene.views import forms
from django.http.response import HttpResponse, HttpResponseServerError
from vespene.common.logger import Logger
from vespene.models.pipeline import Pipeline
from vespene.models.project import Project
from vespene.manager.permissions import PermissionsManager
from vespene.views.view_helpers import (build_status_icon,
                                  format_time, icon, link,
                                  project_controls_icon, template)
from vespene.views import BaseView

LOG = Logger()

permissions = PermissionsManager()

class PipelineView(BaseView):
    model = Pipeline
    form = forms.PipelineForm
    view_prefix = 'pipeline'
    object_label = 'Pipeline'
    supports_new = True
    supports_edit = True
    supports_delete = True

    @classmethod
    def get_queryset(cls, request):
        return Pipeline.objects    

    @classmethod
    def map(cls, request, *args, **kwargs):
        """
        This generates a custom web page that shows all the projects that are in each pipeline.
        The view is a grid, with each stage presented in order of appearance.
        """

        pipeline = get_object_or_404(Pipeline, pk=kwargs.get('pk'))

        def describe_project(project):
            """
            This draws a cell within the table for each project that is a member of each stage.
            """
            if project is None:
                return ""
            if project.active_build is None:
                which = build_status_icon(project.last_build, compact=False)
            else:
                which = build_status_icon(project.active_build, compact=False)
            controls = project_controls_icon(project, project.active_build, compact=True)
            project_link = link("/ui/projects/%d/detail" % project.id, project.name)
            return "%s<br/>%s %s" % (project_link, which, controls)
                            
        stages = pipeline.all_stages()
        projects_by_stage = dict()
        max_width = 0
        # Build up a hash table of each project in each stage. 
        # TODO: move this code into models/stage.py
        for stage in stages:
            projects = Project.objects.filter(stage=stage, pipeline=pipeline).order_by('name').all()
            width = len(projects)
            if width > max_width:
                max_width = width
            projects_by_stage[stage.name] = projects        

        # This pads out the tables to make the table display even, because not every
        # stage may have the same number of rows.
        for (k,v) in projects_by_stage.items():
            stage_length = len(v)
            values = [ x for x in v ]
            if stage_length < max_width:
                padding = max_width - stage_length
                values.extend(None for x in range(0,padding))
            projects_by_stage[k] = values

        # With all data calculated, render the template.
        context = dict(
            pipeline = pipeline,
            width = max_width,
            stages = stages,
            projects_by_stage = projects_by_stage,
            describe_project = describe_project
        )
        return template(request, 'pipeline_map.j2', context)

    @classmethod
    def status_column(cls, obj):
        return obj.explain_status()

    @classmethod
    def map_column(cls, obj):
        # show a link to see the build history of this project
        my_link = "/ui/pipelines/%s/map" % obj.id
        my_icon = icon('fa-map', family='fas', tooltip='Map View')
        return link(my_link, my_icon)

    @classmethod
    def last_completed_date_column(cls, obj):
        return format_time(obj.last_completed_date)

    @classmethod
    def last_completed_by_column(cls, obj):
        if obj.last_completed_by:
            return build_status_icon(obj.last_completed_by)
        else:
            return "-"

PipelineView.extra_columns = [
    ('Last Completed Date', PipelineView.last_completed_date_column),
    ('Last Endpoint Build', PipelineView.last_completed_by_column),
    ('Map', PipelineView.map_column)
]