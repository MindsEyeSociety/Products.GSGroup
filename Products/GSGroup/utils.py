import datetime
from Products.XWFCore.cache import SimpleCacheWithExpiry

visibilityCache = SimpleCacheWithExpiry('GSGroup.utils.visibilityCache')
visibilityCache.set_expiry_interval(datetime.timedelta(0,60))

#coding: utf-8
PERM_ODD = 0
PERM_ANN = 1
PERM_GRP = 2

def get_cache_key(instance):
    if instance:
        cache_key = str(instance.getPhysicalPath())
    else:
        cache_key = 'None'
        
    assert type(cache_key) == str
    return cache_key

def get_visibility(instance):
    cache_key = get_cache_key(instance)
    cached_retval = visibilityCache.get(cache_key)
    if cached_retval:
        retval = cached_retval    
    else:
        retval = PERM_ODD
        roles = get_roles_with_perm(instance, 'View')
        if (('Anonymous' in roles) and ('Authenticated' in roles)):
            retval = PERM_ANN
        elif ('GroupMember' in roles):
            retval = PERM_GRP

        visibilityCache.add(cache_key, retval)
    assert type(retval) == int
    assert retval in (PERM_ODD, PERM_ANN, PERM_GRP)
    return retval

    
def clear_visibility_cache(instance):
    cache_key = get_cache_key(instance)
    visibilityCache.remove(cache_key)

def get_roles_with_perm(instance, perm):
    assert instance
    assert hasattr(instance, 'rolesOfPermission'),\
      u'Instance %s has no rolesOfPermission' % instance
    retval = [r['name'] for r in instance.rolesOfPermission(perm)
                  if r and (r['selected'] == 'SELECTED' and r['name']) ]
    assert type(retval) == list
    return retval
    
def is_public(g):
    retval = (get_visibility(g) == PERM_ANN)\
      and hasattr(g, 'messages')\
      and (get_visibility(g.messages) == PERM_ANN)
    assert type(retval) == bool
    return retval

