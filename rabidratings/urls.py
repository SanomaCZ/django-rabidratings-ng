from django.conf.urls import url, patterns
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from rabidratings.views import record_vote

urlpatterns = patterns('',
    url(r'^%s/' % slugify(_("submit")), record_vote, name='record_vote'),
)
