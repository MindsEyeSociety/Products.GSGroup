# This Python file uses the following encoding: utf-8
"""The standard GroupServer discussion group. All other groups
are based on the adaptor specified here.
"""
import time, pytz
from datetime import datetime
from zope.interface import Interface, implements
from zope.component import adapts

from Products.CustomUserFolder.CustomUserFolder import CustomUserFolder

from interfaces import *

# Specific Group Types.

class IGSDiscussionGroup(Interface):
    """Marker interface for the GS Discussion Group"""
        
class GSJoiningInfo(object):

    def __init__(self, context):
        self.context = context

    @property
    def joinability(self): 
        mailingList = mailing_list_from_group(group)
        subscribe = mailingList.getProperty('subscribe','')
        joinCondition = group.getProperty('join_condition','')
        isOpen = (subscribe == 'subscribe')
        isRequest = (joinCondition == 'apply')
        isInvitation = (joinCondition != 'apply')

        if isOpen:
            retval = u'anyone'
        elif isRequest:
            retval = u'request'
        elif isInvitation:
            retval = u'invite'
        
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_join(self, user):
        isMember = is_member(user, self.context)
        retval = not(isMember) and (self.joinability == 'anyone')

        assert type(retval) == bool
        return retval
        
    def status(self, user):
        isMember = is_member(user, self.context)
        isInvite = (self.joinability == 'invite')
        isRequest = (self.joinability == 'request')
        
        if isMember:
            retval = u'already a group member'
        elif isInvite:
            retval = u'be invited'
        elif isRequest:
            retval = u'request permission'
        else:
            retval = u'allowed'
        
        assert retval
        assert type(retval) == unicode
        return retval
        
class GSLeavingInfo(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def leavability(self):
        retval = u'anyone'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_leave(self, user):
        retval = is_member(user, self.context)
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if is_member(user, self.context):
            retval = u'a member'
        else:
            retval = u'not a member'
        assert type(retval) == unicode
        return retval
    
class GSDiscussionMessagePostingInfo(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def whoCanPost(self):
        retval = u'all group members'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_post(self, user):
        isMember = is_member(user, self.context)
        isBelowLimit = below_posting_limit(user, self.context)[0]
        
        retval = isMember and isBelowLimit
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        isMember = is_member(user, self.context)
        belowLimit = below_posting_limit(user, self.context)
        isBelowLimit = belowLimit[0]
        
        if isMember and isBelowLimit:
            retval = u'a member'
        elif not(isMember):
            retval = u'not a member'
        elif isMember and not(isBelowLimit):
            retval = belowLimit[1]
            
        assert retval
        assert type(retval) == unicode
        return retval
        
class GSChatPostingInfo(object):
    
    def __init__(self, context):
        self.context = context
        
    @property
    def whoCanPost(self):
        retval = u'all group members'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_post(self, user):
        retval = is_member(user, self.context)
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if is_member(user, self.context):
            retval = u'a member'
        else:
            retval = u'not a member'
        assert retval
        assert type(retval) == unicode
        return retval

def mailing_list_from_group(group):
    # --= Dear God, this is an awful place. =--
    gId = group.getId()
    site_root = group.site_root()
    
    listManager = site_root.objectValues('XWF Mailing List Manager')[0]
    mailingList = listManager.get_list(gId)
    
    assert mailingList, 'Mailing list for group "%s" not found' % gId
    return mailingList

def below_posting_limit(user, group):
    retval = (False, u'never post')
    
    mailingList = mailing_list_from_group(group)
    senderLimit = mailingList.getValueFor('senderlimit')
    senderInterval = mailingList.getValueFor('senderinterval')
    
    # --=mpj17=-- The adapters for administration should be used here.
    isPtnCoach = (user.getId() == mailingList.getProperty('ptn_coach_id', ''))
    
    if isPtnCoach:
        retval = (True, u'administrator')
    else:
        # Not an admin or participation coach
        for emailAddress in user.get_emailAddresses():
            currentTime = int(time.time())
            count = 0
            elapsedTime = currentTime-senderinterval
            earliest = 0
            for postingTime in mailingList.sendercache.get(emailAddress, []):
                if postingTime > elapsedTime:
                    if not earliest or postingTime < earliest:
                        earliest = postingTime
                    count += 1
                else:
                    break

            if count >= senderlimit:
                d = datetime.fromtimestamp(earliest+senderinterval, pytz.utc)
                ds = XWFCore.XWFUtils.munge_date(group, d)
                m = u'post again at %s' % ds
                retval = (False, m)
                break

    assert type(retval) == tuple
    assert len(retval) == 2
    assert type(retval[0]) == bool
    assert type(retval[1]) == unicode
    return retval

def is_member(user, group):
    retval = 'GroupMember' in user.getRolesInContext(group)
    assert type(retval) == bool
    return retval
    
class GSChatViewingInfo(object):
    
    def __init__(self, context):
        self.context = context
        self.visibleChat = context.getProperty('visible_chat', True)
        
    @property
    def whoCanView(self):
        if self.visibleChat:
            retval = u'all group members'
        else:
            retval = u'no one'
        assert retval
        assert type(retval) == unicode
        return retval
        
    def can_view(self, user):
        retval = (is_member(user, self.context) and self.visibleChat)
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        isMember = is_member(user, self.context)
        if isMember and self.visibleChat:
            retval = u'group member'
        elif not(isMember):
            retval = u'not a member'
        elif isMember and not(self.visibleChat):
            retval = u'chat disabled'

        assert retval
        assert type(retval) == unicode
        return retval

