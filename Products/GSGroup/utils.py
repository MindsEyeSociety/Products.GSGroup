#coding: utf-8

import datetime
from AccessControl.PermissionRole import rolesForPermissionOn #@UnresolvedImport
from gs.cache import cache, SimpleCache

PERM_ODD = 0
PERM_ANN = 1
PERM_GRP = 2

def ck(instance):
    instance_id = 'REPLACEME'
    if instance:
        cache_key = instance_id+':'+'%'.join(instance.getPhysicalPath())
    else:
        cache_key = instance_id+':None'
        
    assert type(cache_key) == str
    return cache_key

@cache('GSGroup.utils.get_visibility', ck)
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

def clear_visibility_cache(instance):
    cache = SimpleCache('GSGroup.utils.get_visibility', ck(instance))  
    
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
