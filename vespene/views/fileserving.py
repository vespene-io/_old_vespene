#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  fileserving.py - serve up build roots from different workers
#  --------------------------------------------------------------------------

import traceback
from urllib.parse import parse_qs
import os
from wsgiref.util import FileWrapper
import mimetypes

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseServerError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import PermissionDenied

from vespene.models.build import Build
from vespene.common.logger import Logger

LOG = Logger()

def legal_path(path):
    segments = os.path.split(path)
    if "." in segments or ".." in segments:
        return False
 
    for x in range(1, len(segments)):
        rejoined = os.pathsep.join(segments[0:x])
        if os.path.islink(rejoined):
            return False
    return True

def do_serve_file(build, request, root, path):
    fh = open(path, 'rb')
    wrapper = FileWrapper(fh)
    mtype = mimetypes.guess_type(path)
    response = HttpResponse(wrapper, content_type=mtype)
    response['Content-Length'] = os.path.getsize(path)
    return response

def do_serve_dir(build, request, root, path):
    contents = os.listdir(path)
    contents = [ c for c in contents if contents not in [ ".", ".."]]
    files = []
    for c in contents: 
        joined = os.path.join(path, c)
        partial = joined.replace(root, "", 1)
        item = dict()
        item["directory"] = os.path.isdir(joined)
        item["full_path"] = partial
        item["basename"]  = c
        # TODO: add size, time
        files.append(item)
    context = dict(
        path = path,
        url = "%s/%s" % (settings.FILESERVING_URL, build.id),
        files = files
    )
    return render(request, "dir_index.j2", context=context)

def get_path(request):
    qs = parse_qs(request.META['QUERY_STRING'])
    path = qs.get('p',None)
    if path is None:
        path = "/"
    else:
        path = path[0]
    return path

@csrf_exempt
def serve_file(request, *args, **kwargs):
    path = get_path(request)
    return fileserver(request, path, *args, **kwargs)

@csrf_exempt
def serve_dir(request, *args, **kwargs):
    path = get_path(request)
    return fileserver(request, path, *args, **kwargs)

def fileserver(request, fname, *args, **kwargs):
    """
    Handle incoming file serving requests for a worker to serve
    up it's own build roots.  Doesn't handle requests to other
    workers.
    """
    if not settings.FILESERVING_ENABLED:
        raise PermissionDenied()

    build = get_object_or_404(Build.objects, pk=kwargs.get('pk')) 
    worker = build.worker
    if worker is None:
        raise PermissionDenied()

    root = os.path.join(settings.BUILD_ROOT, str(build.pk))
    if not os.path.exists(root):
        raise PermissionDenied()

    while fname.startswith("/"):
        fname = fname.replace("/","",1)
    fname = os.path.join(root, fname)
    if not legal_path(fname):
        raise PermissionDenied()
    if os.path.isdir(fname):
        return do_serve_dir(build, request, root, fname)
    else:
        return do_serve_file(build, request, root, fname)
   