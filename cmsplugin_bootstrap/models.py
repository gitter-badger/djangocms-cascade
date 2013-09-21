from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from cms.models import CMSPlugin


class BootstrapElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    tag_type = models.CharField(verbose_name=_('tag Type'), max_length=50)
    class_name = models.CharField(_("class name"), max_length=50, blank=True, null=True)
    extra_classes = JSONField(null=True, blank=True, verbose_name=_('A list of extra css classes'))
    extra_styles = JSONField(null=True, blank=True, verbose_name=_('A dictionary of extra css styles'))

    def __unicode__(self):
        return unicode(self.class_name or '')

    @property
    def css_classes(self):
        css_classes = self.class_name and [self.class_name] or []
        if isinstance(self.extra_classes, list):
            css_classes += self.extra_classes
        return ' '.join(css_classes)

    @property
    def css_styles(self):
        if isinstance(self.extra_styles, dict):
            return ' '.join(['{0}: {1};'.format(*s) for s in self.extra_styles.items()])
        return ''