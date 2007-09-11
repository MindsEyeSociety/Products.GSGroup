# coding=utf-8
##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Size adapters for testing

$Id: test_size.py 61072 2005-10-31 17:43:51Z philikon $
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_posting():
    """
    Test emailmessage and adapters

    Set up:
      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import md5
      >>> import Products.Five
      >>> from Products.CustomUserFolder.CustomUser import CustomUser
      >>> from Products.CustomUserFolder.CustomUserFolder import CustomUserFolder
      >>> from Products.Five import zcml
      >>> from zope.component import provideAdapter
      
    Create the first test user
      >>> name = password = 'User A'
      >>> roles = ('GroupMember', 'Hippy')
      >>> domains = None
      >>> userA = CustomUser(name, password, roles, domains)
      >>> 'Authenticated' in userA.getRoles()
      True

    Create the first test administrator
      >>> name = password = 'Group Administrator A'
      >>> roles = ('GroupMember', 'GroupAdmin', 'Hippy')
      >>> domains = None
      >>> groupAdminA = CustomUser(name, password, roles, domains)
      >>> 'Authenticated' in groupAdminA.getRoles()
      True
  
    Create a group
      >>> groupA = CustomUserFolder('group_a_member')
      >>> from zope.interface import alsoProvides
      >>> from Products.GSGroup.interfaces import INoGroup
      
    Add the No-Group maker interface
      >>> alsoProvides(groupA, INoGroup)
      >>> INoGroup.providedBy(groupA)
      True

    Load the adapters
      >>> from Products.GSGroup.noGroup import *
      
    Load the interfaces
      >>> from Products.GSGroup.interfaces import *
      
    Joining
      >>> provideAdapter(NoJoiningInfo)
      >>> joiningInfo = IGSJoiningInfo(groupA)
      >>> joiningInfo.joinability
      u'no one can join the group.'
      >>> joiningInfo.can_join(userA)
      False
      >>> joiningInfo.status(userA)
      u'no one can join the group'
    
    Leaving
      >>> provideAdapter(NoLeavingInfo)
      >>> leavingInfo = IGSLeavingInfo(groupA)
      >>> leavingInfo.leavability
      u'no one can ever leave the group.'
      >>> leavingInfo.can_leave(userA)
      False
      >>> leavingInfo.status(userA)
      u'you can \u266fnever leave\u266f'

    Message posting
      >>> provideAdapter(NoMessagePostingInfo)
      >>> messagePostingInfo = IGSMessagePostingInfo(groupA)
      >>> messagePostingInfo.whoCanPost
      u'No one can post messages.'
      >>> messagePostingInfo.can_post(userA)
      False
      >>> messagePostingInfo.status(userA)
      u'no one can post messages to the group'
      
    Chat message posting
      >>> provideAdapter(NoChatPostingInfo)
      >>> chatPostingInfo = IGSChatPostingInfo(groupA)
      >>> chatPostingInfo.whoCanPost
      u'No one can post chat messages.'
      >>> chatPostingInfo.can_post(userA)
      False
      >>> chatPostingInfo.status(userA)
      u'no one can post chat messages to the group'
      
    Group viewing
      >>> provideAdapter(NoGroupViewingInfo)
      >>> groupViewingInfo = IGSGroupViewingInfo(groupA)
      >>> groupViewingInfo.whoCanView
      u'No one can view the group.'
      >>> groupViewingInfo.can_view(userA)
      False
      >>> groupViewingInfo.status(userA)
      u'no one can view the group.'
      
    Members viewing
      >>> provideAdapter(NoMembersViewingInfo)
      >>> membersViewingInfo = IGSMembersViewingInfo(groupA)
      >>> membersViewingInfo.whoCanView
      u'No one can view the members list.'
      >>> membersViewingInfo.can_view(userA)
      False
      >>> membersViewingInfo.status(userA)
      u'no one can view the members list.'

    Message viewing
      >>> provideAdapter(NoMessageViewingInfo)
      >>> messageViewingInfo = IGSMessageViewingInfo(groupA)
      >>> messageViewingInfo.whoCanView
      u'No one can view the messages.'
      >>> messageViewingInfo.can_view(userA)
      False
      >>> messageViewingInfo.status(userA)
      u'no one can view the messages.'
      
    Chat viewing
      >>> provideAdapter(NoChatViewingInfo)
      >>> chatViewingInfo = IGSChatViewingInfo(groupA)
      >>> chatViewingInfo.whoCanView
      u'No one can view chat.'
      >>> chatViewingInfo.can_view(userA)
      False
      >>> chatViewingInfo.status(userA)
      u'no one can view chat.'
      
    Moderation
      >>> provideAdapter(NoModerationInfo)
      >>> moderationInfo = IGSModerationInfo(groupA)
      >>> moderationInfo.moderationOn
      False
      >>> moderationInfo.moderationStatus
      u'There is no moderation.'

    Moderated Members
      >>> provideAdapter(NoModeratedInfo)
      >>> moderatedInfo = IGSModeratedInfo(groupA)
      >>> moderatedInfo.moderatedMembers
      ()
      >>> moderatedInfo.moderated(userA)
      False
      >>> moderatedInfo.status(userA)
      u'not moderated'

    Moderators
      >>> provideAdapter(NoModeratorInfo)
      >>> moderatorInfo = IGSModeratorInfo(groupA)
      >>> moderatorInfo.moderators
      ()
      >>> moderatorInfo.moderator(userA)
      False
      >>> moderatorInfo.status(userA)
      u'not a moderator'

    Site Administration
      >>> provideAdapter(NoSiteAdministrationInfo)
      >>> administratorInfo = IGSSiteAdministrationInfo(groupA)
      >>> administratorInfo.siteAdministrators
      ()
      >>> administratorInfo.site_administrator(userA)
      False
      
    Group Administration
      >>> provideAdapter(NoGroupAdministrationInfo)
      >>> groupAdministratorInfo = IGSGroupAdmistrationInfo(groupA)
      >>> groupAdministratorInfo.groupAdministrators
      ()
      >>> groupAdministratorInfo.group_administrator(userA)
      False
      >>> groupAdministratorInfo.administrator(userA)
      False
      >>> groupAdministratorInfo.status(userA)
      u'no one is an administrator'

    Participation Coach
      >>> provideAdapter(NoParticipationCoach)
      >>> participationCoachInfo = IGSParticipationCoachInfo(groupA)
      >>> participationCoachInfo.participationCoach
      >>> participationCoachInfo.coach(userA)
      False
      >>> participationCoachInfo.status(userA)
       u'no one is the participation coach'

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

