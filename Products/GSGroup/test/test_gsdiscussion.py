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

    Create the Second test user
      >>> name = password = 'User B'
      >>> roles = ('Hippy')
      >>> domains = None
      >>> userB = CustomUser(name, password, roles, domains)
      >>> 'Authenticated' in userB.getRoles()
      True

    Create the first test administrator
      >>> name = password = 'Group Administrator A'
      >>> roles = ('GroupMember', 'GroupAdmin', 'Hippy')
      >>> domains = None
      >>> groupAdminA = CustomUser(name, password, roles, domains)
      >>> 'Authenticated' in groupAdminA.getRoles()
      True
  
    Create a group
      >>> from zope.app.folder import Folder
      >>> from zope.interface import alsoProvides
      >>> groupA = Folder()
      
    Add the GroupServer Discussion Group maker interface
      >>> from Products.GSGroup.gsDiscussion import IGSDiscussionGroup
      >>> alsoProvides(groupA, IGSDiscussionGroup)
      >>> IGSDiscussionGroup.providedBy(groupA)
      True

    Load the adapters
      >>> from Products.GSGroup.gsDiscussion import *
      
    Load the interfaces
      >>> from Products.GSGroup.interfaces import *
      
    Joining. User A should not be able to join, as it is already a group
    member, while User B is not a group member and should be able to join.
      >>> joiningInfo = IGSJoiningInfo(groupA)
      >>> joiningInfo.can_join(userA)
      False
    
    Leaving
      >>> leavingInfo = IGSLeavingInfo(groupA)
      >>> leavingInfo.leavability
      u'anyone'
      >>> leavingInfo.can_leave(userA)
      True
      >>> leavingInfo.status(userA)
      u'a member'
      >>> leavingInfo.can_leave(userB)
      False
      >>> leavingInfo.status(userB)
      u'not a member'

    Message posting
      >>> messagePostingInfo = IGSMessagePostingInfo(groupA)
      >>> messagePostingInfo.whoCanPost
      u'all group members'
      
    Chat message posting
      >>> chatPostingInfo = IGSChatPostingInfo(groupA)
      >>> chatPostingInfo.whoCanPost
      u'all group members'
      >>> chatPostingInfo.can_post(userA)
      True
      >>> chatPostingInfo.status(userA)
      u'a member'
      >>> chatPostingInfo.can_post(userB)
      False
      >>> chatPostingInfo.status(userB)
      u'not a member'

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

