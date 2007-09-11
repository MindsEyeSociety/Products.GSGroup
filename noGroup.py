"""The No Group. A No group is like a normal group, except no one can do
  anything in a No group. Mostly used for testing, or locking something
  down hard.
"""

from zope.interface import implements
from zope.component import adapts

from Products.CustomUserFolder.CustomUserFolder import CustomUserFolder

from interfaces import *
from Products.XWFChat.interfaces import IGSGroupFolder

class NoPostingInfo(object):
    implements(IGSPostingInfo)
    adapts(IGSGroupFolder)
    
    def __init__(self, context):
        self.context = context
        
    @property
    def whoCanPost(self):
        retval = 'No one can post.'
        assert retval
        return retval
        
    def can_post(self, user):
        retval = False
        assert retval in (True, False)
        return retval
        
    def status(self, user):
        retval = 'no one can post to the group'
        assert retval
        return retval

