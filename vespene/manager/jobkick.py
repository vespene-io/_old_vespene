#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  jobkick.py - support functions for starting/stopping builds from the view
#  side of the house.  All actual processing is handled by code in 'workers/'
#  --------------------------------------------------------------------------

import datetime
import json
import traceback
from urllib.parse import parse_qs

from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from vespene.common.logger import Logger
from vespene.models.build import ABORTING, FAILURE, QUEUED, Build
from vespene.models.project import Project
from vespene.common.variables import VariableManager
from vespene.common.templates import template
from vespene.manager.permissions import PermissionsManager

permissions = PermissionsManager()
LOG = Logger()

# TODO: convert all Exceptions to typed exceptions

def stop_build_from_ui(request, build):
    """
    Handle a POST request from the UI to stop a build from a project.
    """
    if not permissions.check_can_stop(build, request):
        raise PermissionDenied()
    stop_build(build, request=request)
    return HttpResponse("")

def start_project_from_ui(request, project):
    """
    Handle a POST request from the UI to start a build from a project
    """
    if not permissions.check_can_start(project, request):
        raise PermissionDenied()

    if project.has_launch_questions():

        launch_answers = parse_qs(request.body)
        # launch_answers.pop('csrfmiddlewaretoken', None)

        # this hack is because request.POST.dict() does this: 
        # https://stackoverflow.com/questions/31568702/django-request-data-dictionary-returns-last-item-instead-of-list-for-post-data-f
        # so we can't use it

        # TODO: this is getting a bit complex, split this into smaller functions / refactor

        try:
            questions = json.loads(project.launch_questions)
        except:
            raise Exception("failed to load JSON: %s" % project.launch_questions)

        for q in questions:
            variable_name = q.get('variable', '')
            # this could break if the project questions are changed before the build actually runs
            # in that case the variable won't make it in and that is ok.
            encoded = variable_name.encode('utf-8')
            answer = launch_answers.get(encoded, None)
            if not answer:
                continue
            if q.get('type', '') not in [ 'multi' ]:
                answer = answer[0].decode('utf-8')
            else:
                answer = [ a.decode('utf-8') for a in answer]
            launch_answers[variable_name] = answer
            launch_answers.pop(encoded, None)
            launch_answers.pop('csrfmiddlewaretoken'.encode('utf-8'), None)

    else:
        launch_answers = {}

    start_project(project, launch_answers=launch_answers, request=request)
    return HttpResponse("")

def start_project(project, launch_answers=None, request=None, pipeline_parent_build=None):
    """
    Create a stub build object that is good enough for the backend job system to complete when it has time.
    """

    if project.is_active():
        raise Exception("Can not build this project while another build is active, please stop it first")
    if launch_answers is None:
        launch_answers = {}

    variables = compute_variable_chain(project)
    variables.update(launch_answers)

    new_build = Build.objects.create(
        project = project,
        status = QUEUED,
        variables = json.dumps(variables),
        queued_time = datetime.datetime.now(tz=timezone.utc),
        worker_pool = project.worker_pool,
        launch_answers = json.dumps(launch_answers),
        script = ""
    )
    new_build.save()

    try:
        script = compute_script(project, new_build, variables)
    except Exception as e:
        traceback.print_exc()
        # FIXME: failure triggers won't run if we hit a failure here, we should catch and re-raise a proper
        # exception.
        new_build.append_output("the project could not be started due to a template error")
        new_build.append_output(str(e))
        new_build.status=FAILURE
        new_build.save()
        project.last_build=new_build
        project.save(update_fields=['last_build'])
        # FIXME: only catch correct type of exception
        return

    new_build.script = script

    if request:
        new_build.created_by = request.user

    if pipeline_parent_build:
        new_build.pipeline_parent_build_id = pipeline_parent_build.pk
        new_build.pipeline_origin_build_id = pipeline_parent_build.pipeline_origin_build_id
    else:
        new_build.pipeline_origin_build_id = new_build.pk

    new_build.save()

    project.active_build = new_build
    project.save(update_fields=['active_build'])     
    if request:
        messages.add_message(request, messages.SUCCESS, "Build <A HREF='/ui/builds/%s/detail'>%s</A> started for Project <A HREF='/ui/projects/%s/detail'>%s</A>" % (new_build, new_build.pk, project.pk, project.name))

def stop_build(build, request=None):
    """
    Stop a specific build, by moving it into "ABORTING" state and then waiting for the worker to figure out how
    to kill it.
    """
    if build is None or not build.is_stoppable():
        return
    else:
        build.status = ABORTING
        projects = Project.objects.filter(active_build=build).all()
        # there should only be one project for this build
        for project in projects:
            project.active_build = None
            project.save()
        build.save()
        if request:
            messages.add_message(request, messages.WARNING, "Build <A HREF='/ui/builds/%s/detail'>%s</A> stopped for Project <A HREF='/ui/projects/%s/detail'>%s</A>" % (build, build.pk, project.pk, project.name))

def compute_script(project, build, variable_chain):
    return template(project.script, variable_chain, strict_undefined=True)

def compute_variable_chain(project):
    return VariableManager(project).compute()
