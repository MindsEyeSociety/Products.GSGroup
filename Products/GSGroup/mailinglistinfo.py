from zope.interface import implements, implementedBy
from zope.component import adapts, createObject
from zope.app.folder.interfaces import IFolder
from zope.component.interfaces import IFactory

from interfaces import IGSMailingListInfo
from Products.GSGroupMember.groupmembership import GroupMembers, \
  user_admin_of_group, user_participation_coach_of_group

class GSMailingListInfoFactory(object):
    implements(IFactory)
    
    title = u'GroupServer Mailing List Info Factory'
    descripton = u'Create a new GroupServer Mailing List Information instance'
    
    def __call__(self, context, groupId=None):
        retval = GSMailingListInfo(context, groupId)
        return retval
        
    def getInterfaces(self):
        retval = implementedBy(GSMailingListInfo)
        assert retval
        return retval
        
    #########################################
    # Non-Standard methods below this point #
    #########################################

    def __get_mailing_list_object_by_id(self, context, groupId):
        site_root = context.site_root()
        assert hasattr(site_root, 'ListManager')
        retval = getattr(site_root.ListManager, groupId)
        assert retval
        return retval

class GSMailingListInfo(object):
    implements(IGSMailingListInfo)
    adapts(IFolder)
    
    def __init__(self, context, groupId=None):
        self.context = context
        self.groupId = groupId
        self.groupInfo = createObject('groupserver.GroupInfo',
                            self.context, groupId)
        self.groupObj = self.groupInfo.groupObj
        assert self.groupObj, 'No group. Blame Zope.'
        self.mlist = self.__get_mailing_list()
        
    def __get_mailing_list(self):
        retval = None
        if self.groupId:
            retval = self.__get_mailing_list_by_id(self.groupId)
        else:
            retval = self.__get_mailing_list_by_id(self.groupObj.getId())
        return retval

    def __get_mailing_list_by_id(self, groupId):
        site_root = self.context.site_root()
        mailingListManager = getattr(site_root, 'ListManager')
        assert mailingListManager, 'No MailingListManager found.'
        retval = mailingListManager.get_list(groupId)
        return retval
        
    @property
    def is_moderated(self):
        retval = self.get_mlist_property('moderated', False)
        return retval

    @property
    def is_moderate_new(self):
        retval = False
        if self.is_moderated:
            retval = self.get_mlist_property('moderate_new_members', False)
        return retval

    @property
    def moderators(self):
        return self.get_moderators()
    def get_moderators(self):
        """ Find and return all the moderators as a list of userInfo objects.
        The userIds of all moderators are assumed to be stored in a property 
        called 'moderator_members' of type 'lines'.
        """
        retval = []
        if self.is_moderated:
            memberIds = [ m.id for m in GroupMembers(self.groupObj).members ]
            retval = [ createObject('groupserver.UserFromId', \
                        self.context, uid) for uid in \
                          self.get_mlist_property('moderator_members', [])
                       if uid in memberIds ]
        assert type(retval) == list
        return retval

    @property
    def moderatees(self):
        return self.get_moderatees()
    def get_moderatees(self):
        """ Find and return all moderated members as a list of userInfo objects.
        The userIds of specified moderated members are assumed to be stored in a 
        property called 'moderated_members' of type 'lines'.
          If this property does not exist or does not contain any userIds, then
        there are two possibilities: either no members are moderated, or all
        group members (other than administrators, moderators and the ptn coach)
        are moderated. 
          The deciding factor is whether 'Moderate New Members' is on: 
           - If so, then it is assumed that *no members* are being moderated. 
           - If not, then it is assumed that *all normal members* are moderated.
        """
        retval = []
        if self.is_moderated:
            moderated_ids = self.get_mlist_property('moderated_members', [])
            group_members = GroupMembers(self.groupObj).members
            if moderated_ids:
                memberIds = [ m.id for m in group_members ]
                retval = [ createObject('groupserver.UserFromId', \
                            self.context, uid) for uid in \
                              moderated_ids if uid in memberIds ]
            elif not(self.is_moderate_new):
                retval = [ u for u in group_members if \
                          (not(user_admin_of_group(u, \
                              self.groupInfo)) and \
                           not(user_participation_coach_of_group(u, \
                              self.groupInfo) and \
                           (u not in self.moderators) and \
                           (u not in self.blocked_members))) ]
        assert type(retval) == list
        return retval

    @property
    def blocked_members(self):
        return self.get_blocked_members()
    def get_blocked_members(self):
        """ Find and return all blocked members as a list of userInfo objects.
        The userIds of all blocked members are assumed to be stored in a 
        property called 'blocked_members' of type 'lines'.
        """
        retval = [ createObject('groupserver.UserFromId', \
                    self.context, uid) for uid in \
                      self.get_mlist_property('blocked_members', []) ]
        assert type(retval) == list
        return retval

    @property
    def posting_members(self):
        return self.get_posting_members()
    def get_posting_members(self):
        """ Find and return all posting members as a list of userInfo objects.
        The userIds of specified posting members are assumed to be stored in a 
        property called 'posting_members' of type 'lines'. If this property does 
        not exist or does not contain any userIds, then all group members are 
        assumed to be posting members.
        """
        postingIds = self.get_mlist_property('posting_members', [])
        group_members = GroupMembers(self.groupObj).members
        if postingIds:
            memberIds = [ m.id for m in group_members ]
            retval = [ createObject('groupserver.UserFromId', \
                        self.context, uid) for uid in \
                          postingIds if uid in memberIds ]
        else:
            retval = group_members
        assert type(retval) == list
        return retval

    def get_property(self, prop, default=None):
        return self.get_mlist_property(prop, default=None)
    def get_mlist_property(self, prop, default=None):
        assert self.mlist, 'Mailing list does not exist\n'\
          'Context %s\nID %s' % (self.context, self.groupId)
        return self.mlist.getProperty(prop, default)

