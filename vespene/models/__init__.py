#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
# ---------------------------------------------------------------------------
# models.py: base class of all DB models, some minor utility functions
# models are smart objects that include behavior as well as representation
# ---------------------------------------------------------------------------

class BaseModel(object):

    def __str__(self):
        return self.name

def as_dict(obj):
    if obj is None:
        return None
    else:
        return obj.as_dict()