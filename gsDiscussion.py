# This Python file uses the following encoding: utf-8
"""The standard GroupServer discussion group. All other groups
are based on the adaptor specified here.
"""
import time, pytz
from datetime import datetime
import AccessControl
from zope.interface import Interface, implements
from zope.component import adapts, createObject

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
        
class GSSiteAdministrationInfo(object):
    
    def __init__(self, context):
        self.context = context
        siteInfo = createObject('groupserver.SiteInfo', context)
        siteMemberName = '%s_member' % siteInfo.get_id()
        acl_users = context.site_root().acl_users()
        self.members = acl_users.getGroupById(siteMemberName).getUsers()
        
        self.__admins = ()
        
    @property
    def siteAdministrators(self):
        if not self.__admins:
            admins = [member for member in self.members 
                if 'DivisionAdmin' in member.getRolesInContext(self.context)]
            self.__admins = tuple(admins)
        retval = self.__admins
        assert type(retval) == tuple
        return retval
        
    def site_administrator(self, user):
        retval = user in self.siteAdministrators
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if self.site_administrator(user):
            retval = u'a site administrator'
        else:
            retval = u'not a site administrator'
        assert type(retval) == unicode
        assert retval
        return retval
    
class GSGroupAdministrationInfo(object):

    def __init__(self, context):
        self.context = context
        acl_users = context.site_root().acl_users
        groupname = '%s_member' % context.getId()
        self.members = acl_users.getGroupById(groupname).getUsers()
        self.siteAdminInfo = IGSSiteAdministrationInfo(context)

        self.__admins = ()
        
    @property
    def groupAdministrators(self):
        if not self.__admins:
            admins = [member for member in self.members 
                if 'GroupAdmin' in member.getRolesInContext(self.context)]
            self.__admins = tuple(admins)
        retval = self.__admins
        assert type(retval) == tuple
        return retval
      
    def administrator(self, user):
        siteAdmins = self.siteAdminInfo.siteAdministrators
        groupAdmins = self.groupAdministrators
        retval = (user in siteAdmins) or (user in groupAdmins)
        assert type(retval) == bool
        return retval
        
    def group_administrator(self, user):
        retval = user in self.groupAdministrators
        assert type(retval) == bool
        return retval

    def status(self, user):
        if user in self.siteAdminInfo.siteAdministrators:
            retval = u'a site administrator'
        elif user in self.groupAdministrators:
            retval = u'a group administrator'
        else:
            retval = u'not an administrator'
        assert type(retval) == unicode
        assert retval
        return retval

class GSParticipationCoachInfo(object):
    
    def __init__(self, context):
        self.context = context
        
        self.__ptnCoach = None
        
    @property
    def participationCoach(self):
        if not self.__ptnCoach:
            participationCoachId = context.aq_explicit.getProperty('ptn_coach_id','')
            if participationCoachId:
                acl_users = context.site_root().acl_users
                self.__ptnCoach = acl_users.getUser(participationCoachId)
        retval = self.__ptnCoach
        return retval
        
    def coach(self, user):
        retval = self.participationCoach and \
            (user.getId() == self.participationCoach.getId())
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if self.coach(user):
            retval = u'the participation coach'
        else:
            retval = u'not the participation coach'
        assert type(retval) == unicode
        assert retval
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
            retval = u'a group member'
        elif not(isMember):
            retval = u'not a group member'
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
            retval = u'a group member'
        else:
            retval = u'not a group member'
        assert retval
        assert type(retval) == unicode
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
            retval = u'a group member'
        elif not(isMember):
            retval = u'not a group member'
        elif isMember and not(self.visibleChat):
            retval = u'chat disabled'

        assert retval
        assert type(retval) == unicode
        return retval

class GSModerationInfo(object):
        
    def __init__(self, context):
        self.context = context
        self.mailingList = mailing_list_from_group(context)
        
    @property
    def moderationOn(self):
        retval = self.mailingList.getProperty('moderated', False)
        assert type(retval) == bool
        return retval
    
    @property
    def moderationStatus(self):
        moderateNewMembers = self.mailingList.getProperty('moderate_new_members',
            False)
        if self.moderationOn and moderateNewMembers:
            retval = u'specific members and all new members moderated'
        elif self.moderationOn and (not moderateNewMembers):
            retval = u'specific members moderated'
        else:
            retval = u'not moderated'
        assert retval
        assert type(retval) == unicode
        return retval
        
class GSModeratedInfo(object):

    def __init__(self, context):
        self.context = context
        self.moderatedInfo = IGSModerationInfo(context)
        self.moderationOn = self.moderatedInfo.moderationOn
        self.mailingList = mailing_list_from_group(context)
        
    @property
    def moderatedMembers(self):
        if self.moderationOn:
            retval = tuple(self.mailingList.get_moderatedUserObjects(ids_only=False))
        else:
            retval = ()
        assert type(retval) == tuple
        return retval
        
    def moderated(self, user):
        retval = user in self.moderatedMembers
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if self.moderated(user):
            retval = u'moderated'
        else:
            retval = u'not moderated'
        assert retval
        assert type(retval) == unicode
        return retval

class GSModeratorInfo(object):

    def __init__(self, context):
        self.context = context
        self.moderatedInfo = IGSModerationInfo(context)
        self.moderationOn = self.moderatedInfo.moderationOn
        self.mailingList = mailing_list_from_group(context)
        
    @property
    def moderators(self):
        if self.moderationOn:
            retval = tuple(self.mailingList.get_moderatorUserObjects(ids_only=False))
        else:
            retval = ()        
        assert type(retval) == tuple
        return retval
        
    def moderator(self, user):
        retval = user in self.moderators
        assert type(retval) == bool
        return retval
        
    def status(self, user):
        if self.moderator(user):
            retval = u'a moderator'
        else:
            retval = u'not a moderator'
        assert retval
        assert type(retval) == unicode
        return retval

def messages_visible(group):
    securityManager = AccessControl.getSecurityManager()

    groupVisible = securityManager.checkPermission('View', group)
    messagesVisible = securityManager.checkPermission('View',
      group.aq_explicit.messages)
      
    retval = groupVisible and messagesVisible
    assert type(retval) == bool
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
