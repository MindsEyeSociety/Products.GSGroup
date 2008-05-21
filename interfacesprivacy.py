#coding: utf-8
'''Basic Privacy Settings for GroupServer Groups
'''
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import Interface
from zope.schema import *

publicTerm = SimpleTerm(
  'public', 'public',
  u'Public: Everyone can view the group, view the posts, and join the '\
  u'group.')
privateTerm = SimpleTerm(
  'private', 'private',
  u'Private: Everyone can view the group, but only group members can view '\
  u'the posts. Anyone can request to become a member.')
secretTerm  = SimpleTerm(
  'secret', 'secret',
  u'Secret: Only group members can view the group and posts. People must '\
  u'be invited to join the group.'
)
secruityVocab = SimpleVocabulary([publicTerm, privateTerm, secretTerm])
class IGSGroupBasicPrivacySettings(Interface):
    basicPrivacy = Choice(
      title=u'Group Privacy Setting',
      description=u'This setting determines who can view the group, view '\
        u'the posts made to the group, and join the group. Only members '\
        u'of the group can add posts to the group.',
      required=True,
      vocabulary=secruityVocab,
    )

