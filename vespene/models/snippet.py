#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# snippet.py - snippets are large chunks of text that are available as
# jinja2 variables, but are  unique in that they too are templated before
# being made available as variables. A good way to reuse text between
# multiple build scripts.
#---------------------------------------------------------------------------

from django.contrib.auth.models import Group, User
from django.db import models

from vespene.models import BaseModel

class Snippet(models.Model, BaseModel):

    class Meta:
        db_table = 'snippets'

    # TODO: assert that there are no spaces or characters not legal in python variables in the template name, using a custom validator / pre-save / etc.

    name = models.CharField(unique=True, max_length=512, help_text="Snippet names must be a valid python identifiers (ex: just_like_this1)")
    description = models.TextField(blank=True)
    text = models.TextField(help_text="this value will be used wherever the {{snippet_name}} appears in a build script")

    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='snippets', blank=True)

    def __str__(self):
        return self.name
