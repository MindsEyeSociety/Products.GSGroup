#coding: utf-8
'''Change the Basic Security Settings of a GroupServer Group
'''

from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import RadioWidget
from zope.app.form.browser.widget import renderElement

from interfacessecurity import IGSGroupBasicSecuritySettings
from Products.CustomUserFolder.interfaces import IGSUserInfo

import logging
log = logging.getLogger('GSGroup')

class NotBrokenRadioWidget(RadioWidget):
    _joinButtonToMessageTemplate = u'%s&nbsp;%s\n'
    def renderItem(self, index, text, value, name, cssClass):
        widgetId = '%s.%s' % (name, index)
        elem = renderElement('input',
                             type="radio",
                             cssClass=cssClass,
                             name=name,
                             id=widgetId,
                             value=value)
        label = '<label class="radioLabel" for="%s">%s</label>' % \
          (widgetId, text)
        return self._joinButtonToMessageTemplate %(elem, label)


def radio_widget(field, request):
    return NotBrokenRadioWidget(field, 
                                field.vocabulary, 
                                request)

class GSGroupChangeBasicSecurityForm(PageForm):
    form_fields = form.Fields(IGSGroupBasicSecuritySettings,
      render_context=False)
    label = u'Change Group Security'
    pageTemplateFileName = 'browser/templates/change_basic_security.pt'
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

        # Look, a hack!
        grp = groupInfo.groupObj
        if not(request.form.get('form.basicSecurity', None)):
            request.form['form.basicSecurity'] = self.group_visibility(grp)
        self.form_fields['basicSecurity'].custom_widget = radio_widget

        self.__admin = None

    def group_visibility(self, grp):
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
        
        retval = ['odd', 'public', 'private', 'secret'][v]
        assert type(retval) == str
        return retval

    def __get_visibility(self, instance):
        retval = self.PERM_ANN
        if instance:
            roles = [r['name'] for r in instance.rolesOfPermission('View')
                     if r and (r['selected'] and r['name']) ]
            if ('Anonymous' in roles and 'Authenticated') in roles:
                retval = self.PERM_ANN
            elif 'GroupMember' in roles:
                retval = self.PERM_GRP
        assert type(retval) == int
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
        
    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        assert self.context
        assert self.form_fields
        
        self.status = {
          'public':  self.set_group_public,
          'private': self.set_group_private,
          'secret':  self.set_group_secret}[data['basicSecurity']]()
                
        assert self.status
        assert type(self.status) == unicode

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_group_public(self):
        '''Set the Group Visibility to Public
        
        SIDE EFFECTS
          * The group is visible to the anonymous user
          * The messages are visible to the anonymous user [acquire]
          * The files are visible to the anonymous user [acquire]
          * The members-list is visible to the anonymous user [acquire]
        '''
        
        m = u'set_group_public: Setting the visibility of the group '\
          u'%s (%s) to "public" for the administrator %s (%s)' %\
          (self.groupInfo.name, self.groupInfo.id, self.admin.name, self.admin.id)
        log.info(m)
        self.set_group_visibility(self.everyone)
        self.set_messages_visibility(self.everyone)
        self.set_files_visibility(self.everyone)
        
        retval = u'%s is now a <strong>public</strong> group: everyone, '\
          u'including userswho are not logged in, can see %s, and the '\
          u'messages posted to %s' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        assert type(retval) == unicode
        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'public', 'Visibility of %s (%s) is %s, not public'%\
          (self.groupInfo.name, self.groupInfo.id, vis)
        return retval
        
    def set_group_private(self):
        m = u'set_group_public: Setting the visibility of the group '\
          u'%s (%s) to "private" for the administrator %s (%s)' %\
          (self.groupInfo.name, self.groupInfo.id, self.admin.name, self.admin.id)
        log.info(m)
        self.set_group_visibility(self.everyone)
        self.set_messages_visibility(self.group)
        self.set_files_visibility(self.group)

        retval = u'%s is now a <strong>private</strong> group. Everyone, '\
          u'including people who are not logged in, can see %s, but only '\
          u'group members can see the messages posted to %s' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        assert type(retval) == unicode
        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'private', 'Visibility of %s (%s) is %s, not private'%\
          (self.groupInfo.name, self.groupInfo.id, vis)
        return retval

    def set_group_secret(self):
        m = u'set_group_public: Setting the visibility of the group '\
          u'%s (%s) to "private" for the administrator %s (%s)' %\
          (self.groupInfo.name, self.groupInfo.id, self.admin.name, self.admin.id)
        log.info(m)
        self.set_group_visibility(self.group)
        self.set_messages_visibility(self.group)
        self.set_files_visibility(self.group)

        retval = u'%s is now a <strong>secret</strong> group. Only  '\
          u'group members can see %s and the messages posted to %s' % \
          (self.groupInfo.name, self.groupInfo.name, self.groupInfo.name)
        vis = self.group_visibility(self.groupInfo.groupObj)
        assert vis == 'secret', 'Visibility of %s (%s) is %s, not secret'%\
          (self.groupInfo.name, self.groupInfo.id, vis)
        assert type(retval) == unicode
        return retval


    def set_group_visibility(self, roles):
        assert type(roles) == list
        assert self.groupInfo
        assert self.groupInfo.groupObj

        m = u'set_group_visibility: Giving the roles %s "View" and '\
          u'"Access contents information" permission in the group '\
          u'%s (%s) for the administrator %s (%s)' %\
          (roles, self.groupInfo.name, self.groupInfo.id, self.admin.name,
           self.admin.id)
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
          u'%s (%s) for the administrator %s (%s)' %\
          (roles, self.groupInfo.name, self.groupInfo.id, self.admin.name,
           self.admin.id)
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
          u'%s (%s) for the administrator %s (%s)' %\
          (roles, self.groupInfo.name, self.groupInfo.id, self.admin.name,
           self.admin.id)
        log.info(m)

        files = self.groupInfo.groupObj.files
        files.manage_permission('View', roles)
        files.manage_permission('Access contents information', roles)
