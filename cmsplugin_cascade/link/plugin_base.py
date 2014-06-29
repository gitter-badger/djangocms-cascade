# -*- coding: utf-8 -*-
import six
from django.contrib.sites.models import Site
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import PartialFormField
from cms.models import Page
try:
    from .fields import PageSearchField as PageSelectFormField
except ImportError:
    from cms.forms.fields import PageSelectFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class LinkPluginBase(CascadePluginBase):
    require_parent = True
    LINK_TARGET = PartialFormField('target',
        RadioSelect(choices=(('', _("Same Window")), ('_blank', _("New Window")),
                             ('_parent', _("Parent Window")), ('_top', _("Topmost Frame")),)),
        initial='',
        label=_('Link Target'),
        help_text=_("Open Link in other target.")
    )

    class Media:
        js = ['cms/js/libs/jquery.min.js']

    def get_site(self):
        try:
            return self.cms_plugin_instance.page.site
        except AttributeError:
            pass
        try:
            return self.page.site
        except AttributeError:
            return Site.objects.get_current()

    def get_form(self, request, obj=None, **kwargs):
        # create a Form class on the fly, containing our page_link field
        page_link_field = self.model.page_link.field
        page_link = PageSelectFormField(queryset=Page.objects.drafts().on_site(self.get_site()),
            label='', help_text=page_link_field.help_text, required=False)
        form = kwargs.pop('form', self.form)
        kwargs.update(form=type('PageLinkForm', (form,), {'page_link': page_link}))
        return super(LinkPluginBase, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        # TODO: return the line name
        return six.u('')

    def save_model(self, request, obj, form, change):
        # depending on the 'link_type', save the form's data into page_link or text_link
        link_type = form.cleaned_data.get('link_type')
        if link_type == 'int':
            obj.text_link = ''
        elif link_type == 'ext':
            obj.page_link = None
            obj.text_link = form.cleaned_data.get('url')
        elif link_type == 'email':
            obj.page_link = None
            obj.text_link = 'mailto: ' + form.cleaned_data.get('email')
        else:
            obj.page_link = None
            obj.text_link = ''
        # transfer link_content from our LinkForm to glossary
        obj.glossary.update(link_content=form.cleaned_data.get('link_content', ''))
        super(LinkPluginBase, self).save_model(request, obj, form, change)
