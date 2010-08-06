# coding=utf-8
from interfaces import IGSGroupInfo
from zope.component import createObject
from Products.XWFCore.XWFUtils import comma_comma_and
from Products.CustomUserFolder.userinfo import userInfo_to_anchor

ANYONE = 'anyone'
REQUEST = 'request'
INVITE = 'invite'

class GSGroupJoining(object):
    
    def __init__(self, context):
        self.site_root = site_root = context.site_root()

        self.groupInfo = IGSGroupInfo(context)

        mailingListManager = site_root.ListManager
        self.mailingList = mailingListManager.get_list(self.groupInfo.id)
        
        self.__joinability = None
        self.__rejoin_advice = None
        
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
            
    @property
    def rejoin_advice(self):
        if self.__rejoin_advice == None:
            if self.joinability == ANYONE:
                self.__rejoin_advice = u'you can rejoin at any time'
            elif self.joinability == REQUEST:
                admins = self.groupInfo.group_admins
                self.__rejoin_advice = u'to rejoin, you can apply to '\
                  u'%s at any time' % comma_comma_and([userInfo_to_anchor(a) for a in admins], conj='or')
            elif self.joinability == INVITE:
                admins = self.groupInfo.group_admins
                self.__rejoin_advice = u'to rejoin, you must be '\
                  u'invited by %s' % comma_comma_and([userInfo_to_anchor(a) for a in admins], conj='or')
        return self.__rejoin_advice
    
