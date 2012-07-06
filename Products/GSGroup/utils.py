#coding: utf-8

import datetime
from AccessControl.PermissionRole import rolesForPermissionOn #@UnresolvedImport

PERM_ODD = 0
PERM_ANN = 1
PERM_GRP = 2

def get_visibility(instance):
    retval = PERM_ODD
    roles = rolesForPermissionOn('View', instance)
    if (('Anonymous' in roles) and ('Authenticated' in roles)):
        retval = PERM_ANN
    elif ('GroupMember' in roles):
        retval = PERM_GRP
    assert type(retval) == int
    assert retval in (PERM_ODD, PERM_ANN, PERM_GRP)
    return retval

def is_public(g):
    retval = (get_visibility(g) == PERM_ANN)\
      and hasattr(g, 'messages')\
      and (get_visibility(g.messages) == PERM_ANN)
    assert type(retval) == bool
    return retval

def is_secret(g):
    retval = (get_visibility(g) == PERM_GRP)\
      and hasattr(g, 'messages')\
      and (get_visibility(g.messages) == PERM_GRP)
    assert type(retval) == bool
    return retval
