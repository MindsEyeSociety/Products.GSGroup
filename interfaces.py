"""Interfaces for GroupServer Groups.

Most of the interfaces define the information relating to a particular
group activity. The are of the same rough form, with two main methods
  * Ability: Does the user have the ability to carry out a particular 
    activity?
  * Status: Describe the user's ability to carry out a particular
    activity.
The exceptions to this basic idiom are the administration interfaces, and 
the "IGSModerationInfo", interface. The latter does not have any methods,
and supplies information about the entire group; the former also proides
methods for determining the type of administrator the user is.
"""
import zope.component
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from zope.schema import *
from zope.interface import Interface

# Membership

class IGSJoiningInfo(Interface):
    """Joining information for a group."""

    context = Field(title=u'Context',
      description=u'Group-context for the joining information')
    
    joinability = Text(title=u'Joinability',
      description = u'The joining-status for the group.',
      readonly=True)
    
    def can_join(user):
      """Can the user can leave the group?
        
        ARGUMENTS
          "user"" A user.
        
        RETURNS
          "True" if the user is not a group member and can join the group;
          "False" otherwise.
            
        SIDE EFFECTS
          None.
        """
    def status(user):
        """Can the user can leave the group?
        
        ARGUMENTS
          "user"" A user.
        
        RETURNS
          A string stating whether the user is in the group, if the user
          can join the group, and how to join.
            
        SIDE EFFECTS
          None.
        """

class IGSLeavingInfo(Interface):
    """Leaving information for a group."""
    
    context = Field(title=u'Context',
      description=u'Group-context for the leaving information')
    
    leavability = Text(title=u'Leavability',
      description = u'The leaving-status for the group.',
      readonly=True)
        
    def can_leave(user):
        """Can the user can leave the group?
        
        ARGUMENTS
          "user"" A user.
        
        RETURNS
          "True" if the user is a group member and can leave the group;
          "False" otherwise.
            
        SIDE EFFECTS
          None.
        """
    
    def status(user):
        """The leaving-status for a user
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string stating that the user can leave the group, or describing
          why the user cannot leave the group.
        
        SIDE EFFECTS
          None
        """

# Administration

# --=mpj17=-- Should the participation coach information be separated out?

class IGSSiteAdministrationInfo(Interface):
    """Site administration information"""

    context = Field(title=u'Context',
      description=u'Context for the site administration information')

    siteAdministrators = Tuple(title=u'Site Administrators',
      description=u'All the administrators for the site.',
      readonly=True)

    def site_administrator(user):
        """Whether the user a site administrator.
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user is a site administrator; "False" otherwise.
        
        SIDE EFFECTS
          None
        """

class IGSParticipationCoachInfo(Interface):
    """Participation Coach Information"""
    
    participationCoach = Field(title=u'Participation Coach',
      description=u'The participation coach for the group',
      readonly=True)    

    def coach(user):
        """Is the user a participation coach?
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user is a participation coach; "False" otherwise.
        
        SIDE EFFECTS
          None
        """
    
    def status(user):
        """Paricipation coach status of the user
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string describing the participation-coach status of the user.
          
        SIDE EFFECTS
          None.
        """

class IGSGroupAdmistrationInfo(Interface):
    """Group administration information"""
    
    groupAdministrators = Tuple(title=u'Group Administrators',
      description=u'All users that have the group administrator role',
      readonly=True)
      
    def administrator(user):
        """Can the user administer the group?
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user is a site administrator, or a group
          administrator; "False" otherwise.
        
        SIDE EFFECTS
          None
        """

    def group_administrator(user):
        """Is the user a group administrator?
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user is a site administrator; "False" otherwise.
        
        SIDE EFFECTS
          None
        """

    def status(user):
        """Administration status of the user.
        
        ARGUMENTS
          "user": A user.
          
        RETURNS
          A string describing the administration status of the user.

        SIDE EFFECTS
          None."""

# Moderation

class IGSModerationInfo(Interface):
    """The moderation information for the group as a whole, rather than
    information about any particular user."""
    
    context = Field(title=u'Context',
      description=u'Context for the site moderation information')
      
    moderationOn = Bool(title=u'Moderation On',
      description=u'True if moderation on for the group',
      readonly=True)

    moderationStatus = Text(title=u'Moderation Status',
      description=u'The moderation status for the group',
      readonly=True)

class IGSModeratedInfo(Interface):
    """Information about the users who are moderated in the group"""

    context = Field(title=u'Context',
      description=u'Context for the moderated-user information')
      
    moderatedMembers = Tuple(title=u'Moderated Members',
      description=u'The moderated members in the group.')
    
    def moderated(user):
        """Is the user moderated?
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if posts from the user are moderated; "False" otherwise.
        
        SIDE EFFECTS
          None
        """

    def status(user):
        """The moderation status for the user in the group.
        
        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string describing the moderation status of the user in the 
          group.
        
        SIDE EFFECTS
          None
        """

class IGSModeratorInfo(Interface):
    """Information about the users who are moderators in the group"""

    context = Field(title=u'Context',
      description=u'Context for the moderator information')

    moderators = Tuple(title=u'Moderators',
      description=u'The members who are moderators in the group',
      readonly=True)
      
    def moderator(user):
        """Is the user a moderator?
        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user is a moderator in the group; "False" 
          otherwise.
        
        SIDE EFFECTS
          None
        """

    def status(user):
        """The moderator status for the user in the group.

        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string describing the moderation status for the user in the
          group.
        
        SIDE EFFECTS
          None
        """

# Viewing

class IGSViewingInfo(Interface):
    """Information about viewing areas of a group.
    
    There are three areas that can have viewing privilages seperate to
    those specified for the entire group:
      * Messages,
      * Chat, and
      * The list of members.
    Information about the visibility of each of the areas, and the entire
    group, is provided by the methods defined here.
    """
    
    context = Field(title=u'Context',
      description=u'Context for the viewing information')

    whoCanView = Text(title=u'Who Can View the Area of the Group',
      description=u'A description of the users who can view the '
        u'particular area of the group',
      readonly=True)

    def can_view(user):
        """Can the user view the area?

        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user can view the group and the area; "False"
          otherwise.
        
        SIDE EFFECTS
          None
        """
        
    def status(user):
        """The status of the user, with respect to viewing the area of the
        group.

        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string describing the status of the user, with respect to
          viewing the area of the group.
          
        SIDE EFFECTS
          None
        """

class IGSGroupViewingInfo(IGSViewingInfo):
    """Information about who can view the group"""
        
class IGSMembersViewingInfo(IGSViewingInfo):
    """Group-Membership Viewing Information"""

class IGSMessageViewingInfo(IGSViewingInfo):
    """Information about who can view the posts that are added to the 
    group."""

class IGSChatViewingInfo(IGSViewingInfo):
    """Information about who can view the chat-messages that are added to 
    the group."""
    
# Posting

class IGSPostingInfo(Interface):
    """Information about posting to a group."""
    
    context = Field(title=u'Context',
      description=u'Context for the posting information')

    whoCanPost = Text(title=u'Who Can Post to the Group',
      description=u'A description of who can post messages to the group',
      readonly=True)

    def can_post(user):
        """Can the user post messages to the group?

        ARGUMENTS
          "user": A user.
        
        RETURNS
          "True" if the user can post messages and files to the
          group; "False" otherwise.
          
        SIDE EFFECTS
          None
        """

    def status(user):
        """The posting-status of the user.

        ARGUMENTS
          "user": A user.
        
        RETURNS
          A string describing the posting-status of the user.
          
        SIDE EFFECTS
          None
        """

class IGSMessagePostingInfo(IGSPostingInfo):
    """Information about posting messages to the group"""

class IGSChatPostingInfo(IGSPostingInfo):
    """Information about posting chat messages to the group"""

