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

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        #if not(hasattr(context, '')):
        #    context.manage_addProperty('showImage', True, 'boolean')
        self.form_fields['basicSecurity'].custom_widget = radio_widget

    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        assert self.context
        assert self.form_fields
        self.status = u'All good. All fine.'
        assert self.status
        assert type(self.status) == unicode

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'


