from zope.interface import implements, implementedBy
from zope.component import adapts, createObject
from zope.app.folder.interfaces import IFolder
from interfaces import IGSGroupInfo
from zope.component.interfaces import IFactory
from gs.groups.interfaces import IGSGroupsInfo
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope

class GSGroupInfoFactory(object):
    implements(IFactory)
    
    title = u'GroupServer Group Info Factory'
    descripton = u'Create a new GroupServer group information instance'
    
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
        groupsInfo = IGSGroupsInfo(context)
        assert hasattr(groupsInfo.groupsObj, groupId), \
          '%s does not exist in %s' % (groupId, context)
        retval = getattr(groupsInfo.groupsObj, groupId)
        assert retval
        return retval

class GSGroupInfo(object):
    implements(IGSGroupInfo)
    adapts(IFolder)
    
    def __init__(self, context, groupId=None):
        ctx = get_the_actual_instance_from_zope(context)
        self.context = ctx
        self.groupId = groupId
        self.siteInfo = createObject('groupserver.SiteInfo', ctx)
        self.groupObj = self.__get_group_object()

    def __get_group_object(self):
        if self.groupId:
            retval = self.__get_group_object_by_id(self.groupId)
        else:
            retval = self.__get_group_object_by_acquisition()
        return retval
        
    def __get_group_object_by_id(self, groupId):
        retval = None
        site_root = self.context.site_root()
        content = getattr(site_root, 'Content')
        site = getattr(content, self.siteInfo.get_id())
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
                    if getattr(group_object.aq_inner.aq_explicit, 'is_group', False):
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
        return (self.groupObj != None)

    @property
    def id(self):
        return self.get_id()
    def get_id(self):
        retval = ''
        if self.group_exists():
            retval = self.groupObj.getId()
        return retval
        
    @property
    def name(self):
        return self.get_name()
    def get_name(self):
        retval = ''
        if self.group_exists():
            retval = self.groupObj.title_or_id()
        return retval

    @property
    def url(self):
        return self.get_url()
    def get_url(self):
        assert(self.group_exists()), 'Group "%s" does not exist' % self.id
        retval = '%s/groups/%s' % (self.siteInfo.url, self.id)
        return retval
        
    @property
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
        assert type(retval) == str
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
        admins = self.groupObj.users_with_local_role('GroupAdmin')
        retval = [ createObject('groupserver.UserFromId',
                      self.context, a) for a in admins ]
        return retval

    @property
    def site_admins(self):
        return self.siteInfo.site_admins

    def get_property(self, prop, default=None):
        assert self.groupObj, 'Group instance does not exist\n'\
          'Context %s\nID %s' % (self.context, self.groupId)
        return self.groupObj.getProperty(prop, default)

def groupInfo_to_anchor(groupInfo):
    assert groupInfo
    assert isinstance(groupInfo, GSGroupInfo), \
        '%s is not a GroupInfo' % groupInfo
    retval = u'<a href="%s" class="group">%s</a>' % \
        (groupInfo.url, groupInfo.name)
    assert retval
    assert type(retval) == unicode
    return retval

