# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from logging import getLogger
log = getLogger('Products.GSGroup.groupinfo')
from zope.app.folder.interfaces import IFolder
from zope.cachedescriptors.property import Lazy
from zope.component.interfaces import IFactory
from zope.component import adapts, createObject
from zope.interface import implements, implementedBy
from gs.core import to_ascii
from gs.groups.interfaces import IGSGroupsInfo
from .interfaces import IGSGroupInfo
from .joining import GSGroupJoining


class GSGroupInfoFactory(object):
    implements(IFactory)

    title = 'GroupServer Group Info Factory'
    description = 'Create a new GroupServer group information instance'

    def __call__(self, context, groupId=None):
        retval = GSGroupInfo(context, groupId)
        return retval

    def getInterfaces(self):
        retval = implementedBy(GSGroupInfo)
        assert retval
        return retval

    #########################################
    # Non-Standard methods below this point #
    #########################################

    def __get_group_object_by_id(self, context, groupId):
        if not isinstance(groupId, basestring):
            m = 'groupID ("{0}") is not a string'.format(groupId)
            raise TypeError(m)

        groupsInfo = IGSGroupsInfo(context)
        # Converting to ASCII to work around the following issue:
        #   TypeError: getattr(): attribute name must be string
        gid = to_ascii(groupId)

        if not hasattr(groupsInfo.groupsObj, gid):
            m = '{0} ("{1}") does not exist in {2}'
            msg = m.format(gid, groupId, context)
            raise ValueError(msg)

        retval = getattr(groupsInfo.groupsObj, gid)
        assert retval
        return retval


class GSGroupInfo(object):
    implements(IGSGroupInfo)
    adapts(IFolder)

    def __init__(self, context, groupId=None):
        self.context = context
        self.groupId = groupId

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        return retval

    @Lazy
    def groupObj(self):
        if self.groupId:
            retval = self.__get_group_object_by_id(self.groupId)
        else:
            retval = self.__get_group_object_by_acquisition()
        return retval

    def __get_group_object_by_id(self, groupId):
        retval = None
        site_root = self.context.site_root()
        content = getattr(site_root, 'Content')
        site = getattr(content, self.siteInfo.id)
        groups = getattr(site, 'groups')
        if hasattr(groups, groupId):
            retval = getattr(groups, groupId)
        return retval

    def __get_group_object_by_acquisition(self):
        """Get the group object by acquisition

        Walk back up the location-hierarchy looking for the group object,
        which is marked by the "is_group" attribute (set to True). For the
        most part, the code was taken from
          "GroupServer/Scripts/get/group_object.py"

        Returns
          None, if no group can be found, or the Folder object if a
          group is found.
        """
        retval = None

        group_object = self.context
        if getattr(group_object.aq_inner.aq_explicit, 'is_group', False):
            retval = group_object
        else:
            while group_object:
                try:
                    group_object = group_object.aq_parent
                    g = group_object.aq_inner.aq_explicit
                    if getattr(g, 'is_group', False):
                        break
                except:
                    break
        try:
            if getattr(group_object.aq_inner.aq_explicit, 'is_group', False):
                retval = group_object
        except:
            pass
        return retval

    def group_exists(self):
        return (self.groupObj is not None)

    @Lazy
    def id(self):
        return self.get_id()

    def get_id(self):
        retval = ''
        if self.group_exists():
            retval = self.groupObj.getId()
        return retval

    @Lazy
    def name(self):
        return self.get_name()

    def get_name(self):
        retval = ''
        if self.group_exists():
            retval = self.groupObj.title_or_id()
        return retval

    @Lazy
    def description(self):
        return self.get_description()

    def get_description(self):
        desc = ''
        if self.group_exists():
            d = self.groupObj.getProperty('description', None)
            desc = d if d else ''
        retval = to_ascii(desc)
        return retval

    @Lazy
    def url(self):
        return self.get_url()

    def get_url(self):
        assert(self.group_exists()), 'Group "%s" does not exist' % self.id
        retval = '%s/groups/%s' % (self.siteInfo.url, self.id)
        return retval

    @Lazy
    def relativeURL(self):
        return self.relative_url()

    def relative_url(self):
        retval = '/groups/%s' % self.id
        return retval

    @Lazy
    def group_type(self):
        return self.get_group_type()

    def get_group_type(self):
        """ AM: A more robust method of identifying the group type will
              replace this once we have interfaces for the various
              group types. For now, horrible as it is, this method
              reflects how we currently identify the group type.
        """
        retval = ''
        if self.group_exists():
            gsTypes = ['discussion', 'announcement', 'support']
            abelTypes = ['ewg', 'ett', 'esg', 'facilitator']
            groupTypes = gsTypes + abelTypes
            templateType = self.get_property('group_template', '')
            if templateType == 'standard':
                retval = groupTypes[0]
            elif templateType in groupTypes:
                retval = groupTypes[groupTypes.index(templateType)]
            elif templateType:
                retval = 'odd'
        if retval:
            assert (retval in groupTypes) or (retval == 'odd')
        return retval

    @property
    def ptn_coach(self):
        return self.get_ptn_coach()

    def get_ptn_coach(self):
        retval = None
        if self.group_exists():
            ptnCoachId = self.get_property('ptn_coach_id', '')
            if ptnCoachId:
                retval = createObject('groupserver.UserFromId', self.context,
                                      ptnCoachId)
        return retval

    @property
    def group_admins(self):
        return self.get_group_admins()

    def get_group_admins(self):
        aclUsers = getattr(self.groupObj, 'acl_users')
        adminIds = self.groupObj.users_with_local_role('GroupAdmin')
        for aId in adminIds:
            user = aclUsers.getUser(aId)
            if not user:
                adminIds.remove(aId)
                m = 'The user ID %s is specified as having the'\
                  'local role GroupAdmin in the group %s (%s) '\
                  'on the site %s (%s), but no user with that '\
                  'ID exists.' % (aId, self.name, self.id,
                    self.siteInfo.name, self.siteInfo.id)
                log.warn(to_ascii(m))

        admins = [createObject('groupserver.UserFromId',
                      self.context, a) for a in adminIds]
        retval = [a for a in admins if not a.anonymous]
        return retval

    @property
    def group_stats(self):
        # FIXME: OMG WTF DELETE ME
        # importing here to workaround a weird import order problem
        from Products.GSParticipationStats.groupstatscontentprovider import \
             GroupPostingStats

        try:
            groupStats = None
            if hasattr(self, '_group_stats'):
                groupStats = self._group_stats
            else:
                groupStats = GroupPostingStats(self)
                groupStats.update()
                self._group_stats = groupStats
        except:
            log.exception('group_stats')
        return groupStats

    @property
    def site_admins(self):
        return self.siteInfo.site_admins

    def get_property(self, prop, default=None):
        assert self.groupObj, 'Group instance does not exist\n'\
          'Context %s\nID %s' % (self.context, self.groupId)
        return self.groupObj.getProperty(prop, default)

    @property
    def joinability(self):
        return GSGroupJoining(self.groupObj).joinability


def groupInfo_to_anchor(groupInfo):
    assert groupInfo
    if not isinstance(groupInfo, GSGroupInfo):
        m = '{0} is not a GroupInfo'.format(groupInfo)
        raise TypeError(m)
    retval = '<a href="%s" class="group">%s</a>' % \
        (groupInfo.url, groupInfo.name)
    return retval
