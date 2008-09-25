#coding: utf-8
PERM_ODD = 0
PERM_ANN = 1
PERM_GRP = 2

def get_visibility(instance):
    retval = PERM_ODD
    if instance:
        assert hasattr(instance, 'rolesOfPermission'),\
          u'Instance %s has no rolesOfPermission' % instance
        roles = [r['name'] for r in instance.rolesOfPermission('View')
                  if r and (r['selected'] and r['name']) ]
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

