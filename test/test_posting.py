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
      >>> from zope.component import provideAdapter

      >>> import Products.GSGroup      
      >>> from Products.Five import zcml
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> zcml.load_config('permissions.zcml', Products.Five)
      >>> zcml.load_config('configure.zcml', Products.GSGroup)

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
      >>> from Products.GSGroup.noGroup import INoGroup
      
    Add the No-Group maker interface
      >>> alsoProvides(groupA, INoGroup)
      >>> INoGroup.providedBy(groupA)
      True

    Load the adapters
      >>> from Products.GSGroup.noGroup import *
      
    Load the interfaces
      >>> from Products.GSGroup.interfaces import *
      
    Joining
      >>> joiningInfo = IGSJoiningInfo(groupA)
      >>> joiningInfo.joinability
      u'no one can join the group.'
      >>> joiningInfo.can_join(userA)
      False
      >>> joiningInfo.status(userA)
      u'no one can join the group'
    
    Leaving
      >>> leavingInfo = IGSLeavingInfo(groupA)
      >>> leavingInfo.leavability
      u'no one can ever leave the group.'
      >>> leavingInfo.can_leave(userA)
      False
      >>> leavingInfo.status(userA)
      u'you can \u266fnever leave\u266f'

    Site Administration
      >>> administratorInfo = IGSSiteAdministrationInfo(groupA)
      >>> administratorInfo.siteAdministrators
      ()
      >>> administratorInfo.site_administrator(userA)
      False
      
    Group Administration
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
      >>> participationCoachInfo = IGSParticipationCoachInfo(groupA)
      >>> participationCoachInfo.participationCoach
      >>> participationCoachInfo.coach(userA)
      False
      >>> participationCoachInfo.status(userA)
       u'no one is the participation coach'

    Message posting
      >>> messagePostingInfo = IGSMessagePostingInfo(groupA)
      >>> messagePostingInfo.whoCanPost
      u'No one can post messages.'
      >>> messagePostingInfo.can_post(userA)
      False
      >>> messagePostingInfo.status(userA)
      u'no one can post messages to the group'
      
    Chat message posting
      >>> chatPostingInfo = IGSChatPostingInfo(groupA)
      >>> chatPostingInfo.whoCanPost
      u'No one can post chat messages.'
      >>> chatPostingInfo.can_post(userA)
      False
      >>> chatPostingInfo.status(userA)
      u'no one can post chat messages to the group'
      
    Group viewing
      >>> groupViewingInfo = IGSGroupViewingInfo(groupA)
      >>> groupViewingInfo.whoCanView
      u'No one can view the group.'
      >>> groupViewingInfo.can_view(userA)
      False
      >>> groupViewingInfo.status(userA)
      u'no one can view the group.'
      
    Members viewing
      >>> membersViewingInfo = IGSMembersViewingInfo(groupA)
      >>> membersViewingInfo.whoCanView
      u'No one can view the members list.'
      >>> membersViewingInfo.can_view(userA)
      False
      >>> membersViewingInfo.status(userA)
      u'no one can view the members list.'

    Message viewing
      >>> messageViewingInfo = IGSMessageViewingInfo(groupA)
      >>> messageViewingInfo.whoCanView
      u'No one can view the messages.'
      >>> messageViewingInfo.can_view(userA)
      False
      >>> messageViewingInfo.status(userA)
      u'no one can view the messages.'
      
    Chat viewing
      >>> chatViewingInfo = IGSChatViewingInfo(groupA)
      >>> chatViewingInfo.whoCanView
      u'No one can view chat.'
      >>> chatViewingInfo.can_view(userA)
      False
      >>> chatViewingInfo.status(userA)
      u'no one can view chat.'
      
    Moderation
      >>> moderationInfo = IGSModerationInfo(groupA)
      >>> moderationInfo.moderationOn
      False
      >>> moderationInfo.moderationStatus
      u'There is no moderation.'

    Moderated Members
      >>> moderatedInfo = IGSModeratedInfo(groupA)
      >>> moderatedInfo.moderatedMembers
      ()
      >>> moderatedInfo.moderated(userA)
      False
      >>> moderatedInfo.status(userA)
      u'not moderated'

    Moderators
      >>> moderatorInfo = IGSModeratorInfo(groupA)
      >>> moderatorInfo.moderators
      ()
      >>> moderatorInfo.moderator(userA)
      False
      >>> moderatorInfo.status(userA)
      u'not a moderator'

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

