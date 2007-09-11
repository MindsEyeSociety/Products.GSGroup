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
      >>> from Products.XWFChat.interfaces import IGSGroupFolder
      >>> alsoProvides(groupA, IGSGroupFolder)
      >>> IGSGroupFolder.providedBy(groupA)
      True

    Adapt the group
      >>> from Products.GSGroup.noGroup import NoPostingInfo
      >>> provideAdapter(NoPostingInfo)
      >>> from Products.GSGroup.interfaces import IGSPostingInfo
      >>> postingInfo = IGSPostingInfo(groupA)
      >>> postingInfo.whoCanPost
      'No one can post.'
      >>> postingInfo.can_post(userA)
      False
      >>> postingInfo.status(userA)
      'no one can post to the group'
      
    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

