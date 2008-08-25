#coding: utf-8
'''Change the Basic Privacy Settings of a GroupServer Group
'''

from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import RadioWidget
from zope.app.form.browser.widget import renderElement

from interfacesprivacy import IGSGroupBasicPrivacySettings
from Products.CustomUserFolder.interfaces import IGSUserInfo

import logging
log = logging.getLogger('GSGroup')

class NotBrokenRadioWidget(RadioWidget):
    _joinButtonToMessageTemplate = u'%s&nbsp;%s\n'
    def renderItem(self, index, text, value, name, cssClass):
        widgetId = '%s.%s' % (name, index)
        elem = renderElement(u'input',
                             type="radio",
                             cssClass=cssClass,
                             name=name,
                             id=widgetId,
                             value=value)
        label = '<label class="radioLabel" for="%s">%s</label>' % \
          (widgetId, text)
        return self._joinButtonToMessageTemplate %(elem, label)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        """Render a selected item of the list."""
        widgetId = '%s.%s' % (name, index)
        elem = renderElement(u'input',
                             value=value,
                             name=name,
                             id=widgetId,
                             cssClass=cssClass,
                             checked="checked",
                             type='radio')
        label = '<label class="radioLabel" for="%s">%s</label>' % \
          (widgetId, text)
        return self._joinButtonToMessageTemplate %(elem, label)

def radio_widget(field, request):
    return NotBrokenRadioWidget(field, 
                                field.vocabulary, 
                                request)

class GSGroupChangeBasicPrivacyForm(PageForm):
    form_fields = form.Fields(IGSGroupBasicPrivacySettings,
      render_context=False)
    label = u'Change Group Privacy'
    pageTemplateFileName = 'browser/templates/change_basic_privacy.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    everyone = ['Anonymous', 'Authenticated', 'DivisionMember',
      'DivisionAdmin','GroupAdmin','GroupMember','Manager', 'Owner']
    
    group = ['DivisionAdmin','GroupAdmin','GroupMember','Manager', 'Owner']

    PERM_ODD = 0
    PERM_ANN = 1
    PERM_GRP = 2
    
    PUBLIC = 1
    PRIVATE = 2
    SECRET = 3
    ODD = 0

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        groupInfo = self.groupInfo = \
          createObject('groupserver.GroupInfo', context)
        groupsInfo = self.groupsInfo = \
          createObject('groupserver.GroupsInfo', context)

        # Look, a hack!
        grp = groupInfo.groupObj
        if not(request.form.get('form.basicPrivacy', None)):
            request.form['form.basicPrivacy'] = self.group_visibility(grp)
        self.form_fields['basicPrivacy'].custom_widget = radio_widget

        self.__admin = None

    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        assert self.context
        assert self.form_fields
        
        m = u'Changing privacy of the group %s (%s) on %s (%s) from "%s" '\
          u'to "%s" for the administrator %s (%s)'%\
           (self.groupInfo.name, self.groupInfo.id, 
            self.siteInfo.name, self.siteInfo.id, 
            self.group_visibility(self.groupInfo.groupObj), 
            data['basicPrivacy'],
            self.admin.name, self.admin.id)
        log.info(m)
        
        self.status = {
          'public':  self.set_group_public,
          'private': self.set_group_private,
          'secret':  self.set_group_secret}[data['basicPrivacy']]()
        
        self.groupsInfo.clear_groups_cache()
        
        assert self.status
        assert type(self.status) == unicode

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def group_visibility(self, grp):
        # TODO: Move to a utility
        assert grp
        msgs = getattr(grp, 'messages', None)
        msgsVis = self.__get_visibility(msgs)
        files = getattr(grp, 'files', None)
        filesVis = self.__get_visibility(files)
        grpVis = self.__get_visibility(grp)

        v = self.ODD
        if ((msgsVis == self.PERM_ANN) 
            and (filesVis == self.PERM_ANN)
            and (grpVis == self.PERM_ANN)):
            v = self.PUBLIC
        elif ((msgsVis == self.PERM_GRP) 
            and (filesVis == self.PERM_GRP)
            and (grpVis == self.PERM_ANN)):
            v = self.PRIVATE
        elif ((msgsVis == self.PERM_GRP) 
            and (filesVis == self.PERM_GRP)
            and (grpVis == self.PERM_GRP)):
            v = self.SECRET
        
        vals = ['odd', 'public', 'private', 'secret']
        retval = vals[v]
        assert type(retval) == str
        assert retval in vals
        return retval

    def __get_visibility(self, instance):
        # TODO: Move to a utility
        retval = self.PERM_ANN
        if instance:
            roles = [r['name'] for r in instance.rolesOfPermission('View')
                     if r and (r['selected'] and r['name']) ]
            if ('Anonymous' in roles and 'Authenticated') in roles:
                retval = self.PERM_ANN
            elif 'GroupMember' in roles:
                retval = self.PERM_GRP
        assert type(retval) == int
        assert retval in (self.PERM_ODD, self.PERM_ANN, self.PERM_GRP)
        return retval
        
    @property
    def admin(self):
        if not(self.__admin):
            loggedInUser = self.request.AUTHENTICATED_USER
            assert loggedInUser
            roles = loggedInUser.getRolesInContext(self.groupInfo.groupObj)
            assert ('GroupAdmin' in roles) or ('DivisionAdmin' in roles), \
              '%s is not a group admin' % loggedInUser
            self.__admin = IGSUserInfo(loggedInUser)
        assert self.__admin
        return self.__admin

    def set_group_public(self):
        '''Set the Group Visibility to Public
        
        SIDE EFFECTS
          * The group is visible to the anonymous user
          * The messages are visible to the anonymous user [acquire]
          * The files are visible to the anonymous user [acquire]
          * The members-list is visible to the anonymous user [acquire]
        '''
        self.set_group_visibility(self.everyone)
        self.set_messages_visibility(self.everyone)
        self.set_files_visibility(self.everyone)
        self.set_joinability_anyone()

        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'public', 'Visibility of %s (%s) is %s, not public'%\
          (self.groupInfo.name, self.groupInfo.id, vis)

        retval = u'%s is now a <strong>public</strong> group. Everyone, '\
          u'can see %s, and the messages posted to %s, including users '\
          u'who are not logged in.' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        assert type(retval) == unicode
        return retval
        
    def set_group_private(self):
        self.set_group_visibility(self.everyone)
        self.set_messages_visibility(self.group)
        self.set_files_visibility(self.group)
        self.set_joinability_request()

        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'private', 'Visibility of %s (%s) is %s, not private'%\
          (self.groupInfo.name, self.groupInfo.id, vis)

        retval = u'%s is now a <strong>private</strong> group. Everyone, '\
          u'can see %s, including people who are not logged in. '\
          u'However, only group members can see the messages posted '\
          u'to %s.' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        assert type(retval) == unicode
        return retval

    def set_group_secret(self):
        self.set_group_visibility(self.group)
        self.set_messages_visibility(self.group)
        self.set_files_visibility(self.group)
        self.set_joinability_invite()
        
        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'secret', 'Visibility of %s (%s) is %s, not secret'%\
          (self.groupInfo.name, self.groupInfo.id, vis)

        retval = u'%s is now a <strong>secret</strong> group. Only  '\
          u'group members can see %s and the messages posted to %s.' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        assert type(retval) == unicode
        return retval

    def set_group_visibility(self, roles):
        assert type(roles) == list
        assert self.groupInfo
        assert self.groupInfo.groupObj

        m = u'set_group_visibility: Giving the roles %s "View" and '\
          u'"Access contents information" permission in the group '\
          u'%s (%s) on %s (%s) for the administrator %s (%s)' %\
          (roles, self.groupInfo.name, self.groupInfo.id,
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)

        group = self.groupInfo.groupObj
        group.manage_permission('View', roles)
        group.manage_permission('Access contents information', roles)
    
    def set_messages_visibility(self, roles):
        assert type(roles) == list
        assert self.groupInfo
        assert self.groupInfo.groupObj
        assert self.groupInfo.groupObj.messages

        m = u'set_messages_visibility: Giving the roles %s "View" and '\
          u'"Access contents information" permission in the group '\
          u'%s (%s) on %s (%s) for the administrator %s (%s).' %\
          (roles, self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)

        messages = self.groupInfo.groupObj.messages
        messages.manage_permission('View', roles)
        messages.manage_permission('Access contents information', roles)

    def set_files_visibility(self, roles):
        assert self.groupInfo
        assert self.groupInfo.groupObj
        assert self.groupInfo.groupObj.files

        m = u'set_files_visibility: Giving the roles %s "View" and '\
          u'"Access contents information" permission in the group '\
          u'%s (%s) on %s (%s) for the administrator %s (%s)' %\
          (roles, self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)

        files = self.groupInfo.groupObj.files
        files.manage_permission('View', roles)
        files.manage_permission('Access contents information', roles)

    @property
    def joinability(self):
        retval = GSGroupJoining(self.groupInfo.groupObj).joinability()
        return retval

    def set_joinability_anyone(self):
        self.__set_list_subscribe('subscribe')
        self.__set_grp_invite('')
        assert self.joinability == 'anyone', 'Joinability not set to anyone'

        m = u'Set joinability of the group %s (%s) on %s (%s) to "anyone" '\
          u'for the administrator %s (%s)' % \
          (self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)
        
    def set_joinability_request(self):
        self.__set_list_subscribe('')
        self.__set_grp_invite('apply')
        assert self.joinability == 'request', 'Joinability not set to request'

        m = u'Set joinability of the group %s (%s) on %s (%s) to "request" '\
          u'for the administrator %s (%s)' % \
          (self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)

    def set_joinability_invite(self):
        self.__set_list_subscribe('')
        self.__set_grp_invite('invite')
        assert self.joinability == 'invite', 'Joinability not set to invite'

        m = u'Set joinability of the group %s (%s) on %s (%s) to "invite" '\
          u'for the administrator %s (%s)' % \
          (self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           self.admin.name, self.admin.id)
        log.info(m)

    def __set_list_subscribe(self, val):
        mailingList = getattr(self.context.ListManager, self.groupInfo.id)
        if mailingList.hasProperty('subscribe'):
            mailingList.manage_changeProperties(subscribe=val)
        else:
            mailingList.manage_addProperty('subscribe', val, 'string')
        
        assert mailingList.getProperty('subscribe') == val,\
          'Subscribe property of the mailing list not set'

        m = u'Set the subscribe property of the mailing-list %s (%s) to '\
          u'"%s" for the administrator %s (%s)'%\
          (self.groupInfo.name, self.groupInfo.id, val,
           self.admin.name, self.admin.id)
        log.info(m)

    def __set_grp_invite(self, val):
        grp = self.groupInfo.groupObj
        if grp.hasProperty('join_condition'):
            grp.manage_changeProperties(join_condition=val)
        else:
            grp.manage_addProperty('join_condition', val, 'string')

        assert grp.getProperty('join_condition') == val,\
          'Join condition of the group not set'
          
        m = u'Set the join condition of the group %s (%s) on %s (%s) to '\
          u'"%s" for the administrator %s (%s)'%\
          (self.groupInfo.name, self.groupInfo.id, 
           self.siteInfo.name, self.siteInfo.id,
           val,
           self.admin.name, self.admin.id)
        log.info(m)

