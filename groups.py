#coding=utf-8
from zope.interface import implements, providedBy
from zope.component import createObject
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary,\
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping 
from Products.XWFCore.XWFUtils import getOption
from Products.GSGroupMember.utils import inform_ptn_coach_of_join, invite_id

from Products.CustomUserFolder.interfaces import IGSUserInfo, ICustomUser
from Products.GSContent.interfaces import IGSGroupInfo
from Products.XWFCore.XWFUtils import sort_by_name

from utils import *

import logging
log = logging.getLogger('GSGroupMember GroupMembership')

class PublicGroupsForSite(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.__groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        
        self.__groups = None
       
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm(g.id, g.id, g.name) for g in self.groups]
        for term in retval:
            assert term
            assert ITitledTokenizedTerm in providedBy(term)
            assert term.token == term.value
        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.groups)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = value in [g.id for g in self.groups]
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)
        
    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for g in self.groups:
            if g.id == token:
                retval = SimpleTerm(g.id, g.id, g.name)
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError, token

    @property
    def groups(self):
        assert self.context
        assert self.__groupsInfo
        
        if self.__groups == None:
            gs = self.__groupsInfo.get_all_groups()
            self.__groups = [createObject('groupserver.GroupInfo', g)
                             for g in gs if is_public(g)]
        assert type(self.__groups) == list
        return self.__groups

class NonPublicGroupsForSite(PublicGroupsForSite):
    '''Get the private and secret groups for the site'''
    def __init__(self, context):
        PublicGroupsForSite.__init__(self, context)
        self.__groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.__groups = None
        
    @property
    def groups(self):
        assert self.context
        assert self.__groupsInfo
        
        if self.__groups == None:
            gs = self.__groupsInfo.get_all_groups()
            self.__groups = [createObject('groupserver.GroupInfo', g)
                             for g in gs if not(is_public(g))]
        assert type(self.__groups) == list
        return self.__groups

