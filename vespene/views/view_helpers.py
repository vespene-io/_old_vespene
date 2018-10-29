#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  view_helpers.py - various reusable functions used to implement the
#  main routes in views.py.  Most notably, the CRUD pages are mostly
#  served off the same templates and feed in some behavior classes as input.
#  See views.py for usage.
#  --------------------------------------------------------------------------

from urllib.parse import parse_qs
import traceback

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone


from vespene.version import VERSION
from vespene.manager import Shared
from vespene.common.logger import Logger
from vespene.models.build import (ABORTED, ABORTING, FAILURE, QUEUED, RUNNING,
                                  SUCCESS, UNKNOWN)
from vespene.manager.permissions import PermissionsManager
from vespene.common.templates import template as common_template

permissions = PermissionsManager()
LOG = Logger()

# ============================================================================================

def template(request, template, context, content_type='text/html'):
    """
    Basic wrapper around Jinja2 template calls for the WebUI, in case we want to make it more complex later.
    """
    return render(request, template, context=context, content_type=content_type)

# ============================================================================================

def get_context(request, cfg, **args):
    """
    Constructs a dictionary of variables for use in common templates.
    Variables are passed in in **args, but we add lots of items from the View
    class (cfg) to save repeated code.
    """
    global permissions

    # FIXME: remove those below that aren't used in templates

    args.update(dict(
        version = VERSION,
        user = request.user,
        messages = messages.get_messages(request),
        object_label = cfg.object_label,
        name_cell = cfg.name_cell,
        new_view = "%s_new" % cfg.view_prefix,
        list_view = "%s_list" % cfg.view_prefix,
        delete_view = "%s_delete" % cfg.view_prefix,
        edit_view = "%s_edit" % cfg.view_prefix,
        detail_view = "%s_detail" % cfg.view_prefix,
        permissions = permissions,
        supports_edit = cfg.supports_edit,
        supports_delete = cfg.supports_delete
    ))
    return args

# ============================================================================================

def querystring_dict(request):
    """
    Rough utility code hack. Why isn't this a part of Django? Maybe it is.
    Return a GET request query string as a dictionary
    """
    result = dict()
    query_str = request.META['QUERY_STRING']
    if query_str is None or query_str == "":
        return dict()
    orig_dict = parse_qs(query_str)
    # because a query string item *CAN* be repeated, though unlikely, the values are a list.  Get the first parameter.
    for (k,v) in orig_dict.items():
        try:
            result[k] = int(v[0])
        except:
            result[k] = v[0]
    return result

# ============================================================================================

def generic_list(cfg, request, *args, **kwargs):
    """
    Generic support for rendering all object list pages.
    """
    Shared().request = request

    # most other anonymous handling works by get_object_or_404 / auth checks, but this one is important for friendly navigation
    if request.user.is_anonymous:
        return redirect('login')

    # what database queryset are we starting with?
    queryset = cfg.get_queryset(request)

    # get URL parameters as a dictionary
    querydict = querystring_dict(request)

    # trim down the DB queryset based on then View code and permissions, then sort it.
    queryset = permissions.filter_queryset_for_list(queryset, request, *args, **kwargs)
    page = querydict.pop('page', None)
    queryset = cfg.filtering(request, queryset).filter(**querydict)
    queryset = cfg.ordering(queryset)

    # handle database pagination of long result sets.
    if page is None:
        page = 1
    # TODO: page size is hard coded for now. make that configurable in settings.
    paginator = Paginator(queryset, settings.DEFAULT_PAGE_SIZE)
    objects = paginator.get_page(page)

    # render the generic list page.
    context_params = dict(
        form = None,
        objects = objects,
        extra_columns = cfg.extra_columns,
        page = page,
        num_pages = paginator.num_pages,
        page_range = paginator.page_range,
        supports_new = permissions.check_can_create(cfg.model, request),
        object_count = paginator.count
    )
    return template(request, 'generic_list.j2', get_context(request, cfg, **context_params))

# ============================================================================================

def process_new(cfg, request):
    """
    Handle a new object creation form submission
    """

    form = cfg.form(request.POST)
    if form.is_valid():
        obj = form.save()
        obj.created_by = request.user
        cfg.finalize(request, obj, create=True)
        obj.save()
        messages.add_message(request, messages.SUCCESS, "%s created." % obj)
        return redirect("%s_list" % cfg.view_prefix)
    else:
        # on error, re-render the page and errors will show up inline
        messages.add_message(request, messages.WARNING, "There are some errors to correct.")
        return template(request, 'generic_new.j2', get_context(request, cfg, flavor='New', form=form))
    
def generic_new(cfg, request, *args, **kwargs):
    """
    Support for rendering all object creation pages & processing submissions
    """
    Shared().request = request
    if not permissions.check_can_create(cfg.model, request, *args, **kwargs):
        return redirect('index')
    if request.method == 'POST': 
        try:
            result = process_new(cfg, request)
            return result
        except Exception as e:
            LOG.error(traceback.format_exc())
            return HttpResponseServerError(e, content_type='text/plain')
    else:
        return template(request, 'generic_new.j2', get_context(request, cfg, flavor='New', form=cfg.form())) 
        
# ============================================================================================

def process_edit(cfg, request, obj):
    """
    Handle an edit form submission
    """
    form = cfg.form(request.POST, instance=obj)
    # FIXME: we should call out to a method in the model to see if it is internally consistent vs just
    # relying on the form code.
    if form.is_valid():
        # save the object then go back to the list page
        form.save() # BOOKMARK: was obj.save
        messages.add_message(request, messages.SUCCESS, "%s saved." % obj)
        cfg.finalize(request, obj, create=False)
        return redirect("%s_list" % cfg.view_prefix)
    else: 
        # invalid form, so go over to the edit page
        messages.add_message(request, messages.WARNING, "There are some errors to correct.")
        return template(request, 'generic_edit.j2', get_context(request, cfg, flavor='Edit', obj=obj, form=form, read_only=False))

def generic_edit(cfg, request, *args, **kwargs):
    """
    Support for rendering all object edit pages & processing submissions.
    """
    Shared().request = request
    pk = kwargs.get('pk')
    obj = get_object_or_404(cfg.model.objects, pk=pk)
    if not permissions.check_can_edit(obj, request, *args, **kwargs):
        return redirect("%s_detail" % cfg.view_prefix, pk=pk)
    qs = permissions.filter_queryset_for_edit(cfg.model.objects, request, *args, **kwargs)
    obj = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        return process_edit(cfg, request, obj)
    else:
        form = cfg.form(instance=obj)
        return template(request, 'generic_edit.j2', get_context(request, cfg, flavor='Edit', obj=obj, form=form, read_only=False))

# ============================================================================================

def generic_detail(cfg, request, *args, **kwargs):
    """
    Support for rendering all object list pages, which are like edit pages with no submit button.
    """
    Shared().request = request
    pk = kwargs.get('pk')
    # TODO: is it possible to streamline all of this for all object types WRT permission code?
    qs = permissions.filter_queryset_for_view(cfg.model.objects, request, *args, **kwargs)
    obj = get_object_or_404(qs, pk=pk)
    if not permissions.check_can_view(obj, request, *args, **kwargs):
        return redirect('index')
    form = cfg.form(instance=obj)
    return template(request, 'generic_edit.j2', get_context(request, cfg, flavor='Detail', obj=obj, form=form, read_only=True))

# ============================================================================================

def process_delete(cfg, request, obj, **kwargs):
    """
    Handle a delete form submission, which are done in the UI by AJAXey means and force
    a reload, hence no need for a redirect reload here.
    """
    try:
        pk = kwargs.get('pk')
        obj = get_object_or_404(cfg.model, pk=pk)
        messages.add_message(request, messages.WARNING, "%s deleted." % obj)
        # FIXME: just mark (most) objects as deleted and filter them out instead
        obj.delete()
        return HttpResponse("ok", content_type="text/plain")
    except Exception as e:
        return HttpResponseServerError(e)

def generic_delete(cfg, request, *args, **kwargs):
    """
    Support for rendering all delete object pages & processing submissions.
    """
    Shared().request = request
    # FIXME: access control using ViewSet code
    # FIXME: as there is no delete page, merge in the process delete code directly into this function
    pk = kwargs.get('pk')
    obj = cfg.model.objects.get(pk=pk)
    if obj is not None and not permissions.check_can_delete(obj, request, *args, **kwargs):
        return HttpResponse("You do not have permission to delete this object.", status=403)
    if request.method == 'POST':
        return process_delete(cfg, request, obj, **kwargs)
    else:
        # FIXME: I suspect the generic delete page is *NOT* used, so can't we delete this?
        form = cfg.form(instance=obj)
        return template(request, 'generic_delete.j2', get_context(request, cfg, form=form, obj=obj)) 

# ============================================================================================

def icon(fa_icon, fa_color="", family="fas", alt="", tooltip=""):
    """
    Render a font-awesome icon with class set by 'fa_icon' and optional color, family, and tooltip.
    FIXME: investigate whether tooltip-JS is working.
    Color text is like 'text-warning', 'text-success', or 'text-failure'
    Family is like 'fas' for 'solid'
    Tooltip may contain an optional explanation
    """
    # TODO: verify that these work or otherwise just use alt tags everywhere
    if tooltip != "":
        tooltip =" data-toggle='tooltip' tooltip='%s'" % tooltip
    if alt != "":
        alt = " alt='%s'" % alt
    if fa_color != "":
        fa_color = " %s " % fa_color
    options = dict(family=family, icon=fa_icon, fa_color=fa_color, tooltip=tooltip, alt=alt)
    return "<i class=\"{family} {icon}{fa_color}\"{tooltip}{alt}></i>".format(**options)

# ============================================================================================

def link(url, body, fn=None, confirm_message=None):
    """
    Render a basic HTML link with URL 'url', pointing at 'body'.  If set 'fn' can render
    a javascript action instead of a URL, which is done for start (without launch questions), stop,
    and delete links.
    """
    if fn is None:
        # classic link
        return "<a href=\"%s\">%s</a>" % (url, body)
    elif fn == 'confirm_post':
        # javascript post link w/ confirmation message
        params = dict(url=url, confirm_message=confirm_message, body=body)
        return "<a onclick=\"confirm_post('{url}', '{confirm_message}', csrf_token);\">{body}</a>".format(**params)
    else:
        params = dict(url=url, body=body, fn=fn)
        return "<a onclick=\"{fn}('{url}', csrf_token);\">{body}</a>".format(**params)

# ============================================================================================

def build_status_icon(build, compact=False, include_buildroot_link=False):
    """
    Return the icon for a given build status.  The icon will link to the detail page
    for the build (builds are not user editable, so there is no edit page).
    """
    if build is None:
        return "%s -" % (icon('fa-question-circle', 'text-info', tooltip='No builds yet'))
    else:
        ic = None
        status = build.status
        if status == SUCCESS:
            ic = icon('fa-check-circle', 'text-success', tooltip='Ok')
        elif status == UNKNOWN:
            ic = icon('fa-question-circle', 'text-info', tooltip='Unknown')
        elif status == FAILURE:
            ic = icon('fa-times-circle', 'text-danger', tooltip='Failed')
        elif status == ABORTED:
            ic = icon('fa-stop-circle', 'text-info', tooltip='Aborted')
        elif status == RUNNING:
            ic = icon('fa-spinner', 'text-info', tooltip='Running')
        elif status == QUEUED:
            ic = icon('fa-stopwatch', 'text-info', tooltip='Queued')
        elif status == ABORTING:
            ic = icon('fa-ban', 'text-info', tooltip='Aborting')
        else:
            ic = "(status=%s, if you see this, it is a bug)" % status
        if not compact:
            body = "%s %s" % (ic, build.id)
        else:
            body = ic
        output = link("/ui/builds/%s/detail" % build.id, body)

        if include_buildroot_link:
            output = output + "&nbsp;" + build_root_link(build)

        return output

# ============================================================================================


def build_root_link(build):
    """
    If the build should have been published, link to the web root.
    """
    web_link = settings.BUILDROOT_WEB_LINK
    complete = build.is_complete()
    if complete:
        if web_link:
            url = common_template(web_link, dict(build=build.as_dict()), strict_undefined=True)
            ic = icon('fa-globe')
            return link(url, ic)
        elif build.worker and build.worker.hostname:
            url = "http://%s:%s/srv/%s/d?p=/" % (build.worker.hostname, build.worker.port, build.id)
            ic = icon('fa-globe')
            return link(url, ic)
        else:
            return ""
    elif web_link == "":
        return icon('ban', alt="this feature has not been configured by the Vespene admin")
    else:
        return icon('clock')

# ============================================================================================

def project_controls_icon(project, build, compact=False):
    """
    Return the status for a project's current build, and maybe a start/stop link.
    """
    # FIXME: we should eventually move all of these hardcoded URLs to use Django's reverse 
    # function to make it easier to change view paths (everywhere)

    if build is None:
        # no active build? Show a start link.
        # if the project has launch questions, there's an intermediate page to link to
        # otherwise, it's an AJAXy link to invoke the project start.
        if project.has_launch_questions():
            proj_link = "/ui/projects/%s/start_prompt" % project.id
            return link(proj_link, icon('fa-play-circle', '', tooltip='Start'))
        else:
            proj_link = "/ui/projects/%s/start" % project.id
            return link(proj_link, icon('fa-play-circle', '', tooltip='Start'), fn='do_post')
          
    else:

        if build.is_stoppable():
            # present a AJAXy stop link
            ic = icon('fa-stop-circle', '', tooltip='Stop')
            if not compact:
                ic = "%s %s" % (ic, link("/ui/builds/%s/detail" % build.id, build.id))
            return link("/ui/builds/%s/stop" % build.id, ic, fn='do_post')
        else:
            ic = icon('fa-play-circle', '', tooltip='Start')
            if not compact:
                # we should only show the build ID if the active build is set and ACTIVE
                if build.active_build_for_project and build.is_active():
                    ic = "%s %s" % (ic, link("/ui/builds/%s/detail" % build.id, build.id))
                return link("/ui/projects/%s/start" % project.id, ic, fn='do_post')

# ============================================================================================

def build_control_icon(build, compact=False):
    """
    Return an icon to adjust the running state of a build.
    """
    if build.is_stoppable():
        return link("/ui/builds/%s/stop" % build.id, icon('fa-stop', '', tooltip='Stop'), fn='do_post')
    else:
        return "-"

# ============================================================================================

def guard_none(obj):
    """
    Return a value, or a placeholder to draw instead if it is None.
    """
    if obj is None:
        return "-"
    return obj

# ============================================================================================

def format_time(t):
    """
    FIXME: Pretty print code for time display
    """
    # FIXME ...
    if t is None:
        return "-"
    t = timezone.localtime(t)
    fmt = settings.TIME_DISPLAY_FORMAT
    return t.strftime(fmt)
