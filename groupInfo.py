from zope.interface import implements, implementedBy
from zope.component import adapts, createObject
from zope.app.folder.interfaces import IFolder
from interfaces import IGSGroupInfo
from Products.GSContent.interfaces import IGSGroupsInfo
from zope.component.interfaces import IFactory

class GSGroupInfoFactory(object):
    implements(IFactory)
    
    title = u'GroupServer Group Info Factory'
    descripton = u'Create a new GroupServer group information instance'
    
    def __call__(self, context, groupId=None):
        retval = None
        if groupId:
            group = self.__get_group_object_by_id(context, groupId)
            retval = GSGroupInfo(group)
        else:
            retval = GSGroupInfo(context)
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
        assert hasattr(groupsInfo.groupsObj, groupId)
        retval = getattr(groupsInfo.groupsObj, groupId)
        assert retval
        return retval

class GSGroupInfo(object):
    implements( IGSGroupInfo )
    adapts( IFolder )
    
    def __init__(self, context, groupId=None):
        self.context = context
        self.groupId = groupId
        self.siteInfo = createObject('groupserver.SiteInfo', self.context)
        self.groupObj = self.__get_group_object()

    def __get_group_object(self):
        retval = None
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
        retval = '%s/groups' % self.siteInfo.get_url()
        if self.group_exists():
            retval = '%s/%s' % (retval, self.groupObj.getId())
        return retval
        
    def get_property(self, prop, default=None):
        assert self.groupObj, 'Group instance does not exist\n'\
          'Context %s\nID %s' % (self.context, self.groupId)
        return self.groupObj.getProperty(prop, default)
        
