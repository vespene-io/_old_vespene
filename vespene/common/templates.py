#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  jinja2_env.py - defines what functions are available to Jinja2 templates
#  used by views.py. Templates are in 'jinja2/'.
#  --------------------------------------------------------------------------

from crispy_forms.utils import render_crispy_form
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment, contextfunction, StrictUndefined

@contextfunction
def crispy(context, form):
    return render_crispy_form(form, context=context)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'crispy' : crispy
    })
    return env

def template(str, template_context, strict_undefined=False):
    """
    Return the value of string templated through the dictionary 'template_context'
    """
    if strict_undefined:
        env = Environment(undefined=StrictUndefined)
    else:
        env = Environment()
    t = env.from_string(str)
    result = t.render(**template_context)
    return result