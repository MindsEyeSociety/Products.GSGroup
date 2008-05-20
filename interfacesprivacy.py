#coding: utf-8
'''Basic Security Settings for GroupServer Groups
'''
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import Interface
from zope.schema import *

publicTerm = SimpleTerm(
  'public', 'public',
  u'Public: Everyone can see the group, view the posts, and join the '\
  u'group.')
privateTerm = SimpleTerm(
  'private', 'private',
  u'Private: Everyone can see the group, but only group members can view '\
  u'the posts. Anyone can request to become a member.')
secretTerm  = SimpleTerm(
  'secret', 'secret',
  u'Secret: Only group members can see the group and posts. People must '\
  u'be invited to join the group.'
)
secruityVocab = SimpleVocabulary([publicTerm, privateTerm, secretTerm])
class IGSGroupBasicSecuritySettings(Interface):
    basicSecurity = Choice(
      title=u'Group Security Setting',
      description=u'This setting determines who can see the group, and '\
        u'the posts made to the group. Only members of the group can add '\
        u'posts to the group.',
      required=True,
      vocabulary=secruityVocab,
    )

