from zope.interface import implements, implementedBy
from zope.component import adapts, createObject
from zope.app.folder.interfaces import IFolder
from zope.component.interfaces import IFactory

from Products.CustomUserFolder.interfaces import IGSUserInfo
from interfaces import IGSGroupInfo, IGSMailingListInfo
from Products.GSGroupMember.groupmembership import user_admin_of_group,\
  user_participation_coach_of_group

class GSMailingListInfoFactory(object):
    implements(IFactory)
    
    title = u'GroupServer Mailing List Info Factory'
    descripton = u'Create a new GroupServer Mailing List Information instance'
    
    def __call__(self, context, groupId=None):
        retval = None
        if groupId:
            mlist = self.__get_mailinglist_object_by_id(context, groupId)
            retval = GSMailingListInfo(mlist)
        else:
            retval = GSMailingListInfo(context)
        return retval
        
    def getInterfaces(self):
        retval = implementedBy(GSMailingListInfo)
        assert retval
        return retval
        
    #########################################
    # Non-Standard methods below this point #
    #########################################

    def __get_mailinglist_object_by_id(self, context, groupId):
        site_root = context.site_root()
        assert hasattr(site_root, 'ListManager')
        retval = getattr(site_root.ListManager, groupId)
        assert retval
        return retval

class GSMailingListInfo(object):
    implements( IGSMailingListInfo )
    adapts( IFolder )
    
    def __init__(self, context, groupId=None):
        self.context = context
        self.groupId = groupId
        self.groupInfo = createObject('groupserver.GroupInfo', self.context)
        self.groupObj = self.groupInfo.groupObj
        self.mlist = self.__get_mailing_list()
        
    def __get_mailing_list(self):
        retval = None
        if self.groupId:
            retval = self.__get_mailing_list_by_id(self.groupId)
        else:
            retval = self.__get_mailing_list_by_id(self.groupObj.getId())
        return retval

    def __get_mailing_list_by_id(self):
        retval = None
        
        site_root = self.context.site_root()
        mailingListManager = getattr(site_root, 'ListManager')
        assert mailingListManager, 'No MailingListManager found.'
        retval = mailingListManager.get_list(groupId)

        return retval
        
    @property
    def is_moderated(self):
        retval = self.get_mlist_property('moderated', False)
        assert type(retval)==bool
        return retval

    @property
    def is_moderate_new(self):
        retval = False
        if self.is_moderated:
            retval = self.get_mlist_property('moderate_new_members', False)
        assert type(retval)==bool
        return retval

    @property
    def moderators(self):
        return self.get_moderators()
    def get_moderators(self):
        """ Return the moderators as a list of userInfo objects.
        """
        retval = []
        if self.is_moderated:
            retval = [ IGSUserInfo(u) for u in \
              self.get_mlist_property('moderator_members', []) ]
        assert type(retval)==list
        return retval

    @property
    def moderatees(self):
        return self.get_moderatees()
    def get_moderatees(self):
        """ Return the moderatees as a list of userInfo objects.
        """
        retval = []
        if self.is_moderated:
            moderated_ids = self.get_mlist_property('moderated_members', [])
            if moderated_ids:
                retval = [ IGSUserInfo(u) for u in moderated_ids ]
            elif not(self.is_moderate_new):
                # No user IDs are specified, so we're moderating everyone
                # except special people
                group_members = [ IGSUserInfo(u) for u in \
                  createObject('groupserver.GroupMembers', self.groupObj) ]
                retval = [ u for u in group_members if \
                  (not(user_admin_of_group(u, self.groupInfo)) and \
                  not(user_participation_coach_of_group(u, self.groupInfo) and \
                  (u not in self.moderators) and \
                  (u not in self.blocked_members))) ]
        assert type(retval)==list
        return retval

    @property
    def blocked_members(self):
        return self.get_blocked_members()
    def get_blocked_members(self):
        """ Return the blocked members as a list of userInfo objects.
        """
        retval = [ IGSUserInfo(u) for u in \
              self.get_mlist_property('moderator_members', []) ]
        assert type(retval)==list
        return retval

    @property
    def posting_members(self):
        return self.get_posting_members()
    def get_posting_members(self):
        """ Return the posting members as a list of userInfo objects.
        """
        retval = [ IGSUserInfo(u) for u in \
              self.get_mlist_property('posting_members', []) ]
        assert type(retval)==list
        return retval

    def get_mlist_property(self, prop, default=None):
        assert self.mlist, 'Mailing list does not exist\n'\
          'Context %s\nID %s' % (self.context, self.groupId)
        return self.mlist.getProperty(prop, default)
        
