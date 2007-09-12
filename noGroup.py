# This Python file uses the following encoding: utf-8
"""The No Group. A No group is like a normal group, except no one can do
  anything in a No group. Mostly used for testing, or locking something
  down hard.
"""
from zope.interface import Interface, implements
from zope.component import adapts

from Products.CustomUserFolder.CustomUserFolder import CustomUserFolder

from interfaces import *

# Specific Group Types.

class INoGroup(Interface):
    """Marker interface for the No Group"""

class NoJoiningInfo(object):

    def __init__(self, context):
        self.context = context

    @property
    def joinability(self):
        retval = u'no one can join the group.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_join(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can join the group'
        assert retval
        assert type(retval) == unicode
        return retval
        
class NoLeavingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def leavability(self):
        retval = u'no one can ever leave the group.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_leave(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'you can ♯never leave♯'
        assert type(retval) == unicode
        return retval

class NoSiteAdministrationInfo(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def siteAdministrators(self):
        retval = ()
        assert type(retval) == tuple
        return retval
        
    def site_administrator(self, user):
        retval = False
        assert type(retval) == bool
        return retval

class NoGroupAdministrationInfo(object):

    def __init__(self, context):
        self.context = context
        
    @property
    def groupAdministrators(self):
        retval = ()
        assert type(retval) == tuple
        return retval
      
    def administrator(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def group_administrator(self, user):
        retval = False
        assert type(retval) == bool
        return retval

    def status(self, user):
        retval = u'no one is an administrator'
        assert type(retval) == unicode
        assert retval
        return retval

class NoParticipationCoach(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def participationCoach(self):
        retval = None
        return retval
        
    def coach(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one is the participation coach'
        assert type(retval) == unicode
        assert retval
        return retval

class NoMessagePostingInfo(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def whoCanPost(self):
        retval = u'No one can post messages.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_post(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can post messages to the group'
        assert retval
        assert type(retval) == unicode
        return retval

class NoChatPostingInfo(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def whoCanPost(self):
        retval = u'No one can post chat messages.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_post(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can post chat messages to the group'
        assert retval
        assert type(retval) == unicode
        return retval

class NoGroupViewingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def whoCanView(self):
        retval = u'No one can view the group.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_view(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can view the group.'
        assert retval
        assert type(retval) == unicode
        return retval

class NoMembersViewingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def whoCanView(self):
        retval = u'No one can view the members list.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_view(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can view the members list.'
        assert retval
        assert type(retval) == unicode
        return retval
        
class NoMessageViewingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def whoCanView(self):
        retval = u'No one can view the messages.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_view(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can view the messages.'
        assert retval
        assert type(retval) == unicode
        return retval

class NoChatViewingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def whoCanView(self):
        retval = u'No one can view chat.'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_view(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'no one can view chat.'
        assert retval
        assert type(retval) == unicode
        return retval

class NoModerationInfo(object):
        
    def __init__(self, context):
        self.context = context

    @property
    def moderationOn(self):
        retval = False
        assert type(retval) == bool
        return retval
    
    @property
    def moderationStatus(self):
        retval = u'There is no moderation.'
        assert retval
        assert type(retval) == unicode
        return retval
        
class NoModeratedInfo(object):

    def __init__(self, context):
        self.context = context
        
    @property
    def moderatedMembers(self):
        retval = ()
        assert type(retval) == tuple
        return retval
        
    def moderated(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'not moderated'
        assert retval
        assert type(retval) == unicode
        return retval
        
class NoModeratorInfo(object):

    def __init__(self, context):
        self.context = context
        
    @property
    def moderators(self):
        retval = ()
        assert type(retval) == tuple
        return retval
        
    def moderator(self, user):
        retval = False
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        retval = u'not a moderator'
        assert retval
        assert type(retval) == unicode
        return retval
        

