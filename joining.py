# coding=utf-8
from Products.GSContent.interfaces import IGSGroupInfo
from zope.component import createObject

ANYONE  = 'anyone'
REQUEST = 'request'
INVITE  = 'invite'

class GSGroupJoining(object):
    
    def __init__(self, context):
        self.site_root = site_root = context.site_root()

        self.groupInfo = IGSGroupInfo(context)

        mailingListManager = site_root.ListManager
        self.mailingList = mailingListManager.get_list(self.groupInfo.id)
        
        self.__joinability = None
        
    @property
    def joinability(self):
        if self.__joinability == None:
            # --=mpj17=-- This is the rule, I shit you not
            if getattr(self.mailingList, 'subscribe', ''):#?hasattr?
                self.__joinability = ANYONE
            elif self.groupInfo.get_property('join_condition', 'open') == 'apply':
                self.__joinability = REQUEST
            else:
                self.__joinability = INVITE
            # --=mpj17=-- No, really, that is the rule: if the join_condition
            #   is 'open' then the group is invitation-only.
        retval = self.__joinability
        assert type(retval) == str
        assert retval in [ANYONE, REQUEST, INVITE]
        return retval
            
