import os

import const

from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

from web.grampsdb.views import (main_page, user_page, logout_page,
                                view, view_detail)

urlpatterns = patterns('',
    # Specific matches first:
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('',
    # Static serves! DANGEROUS in production:
     (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': const.DATA_DIR,
       'show_indexes':  True},
      ),
     (r'^images/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': const.IMAGE_DIR,
       'show_indexes':  True},
      ),
)

# The rest will match views:
urlpatterns += patterns('',
    (r'^$', main_page),
    (r'^user/(\w+)/$', user_page),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^(?P<view>(\w+))/$', view),
    url(r'^person/(?P<handle>(\w+))/$', view_detail, 
        {"view": "person"}, name="view-person-detail"),
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/$', view_detail),
)

# In urls:
# urlpatterns = patterns('',
#    url(r'^archive/(\d{4})/$', archive, name="full-archive"),
#    url(r'^archive-summary/(\d{4})/$', archive, {'summary': True}, "arch-summary"),
# )

# In template:
# {% url arch-summary 1945 %}
# {% url full-archive 2007 %}
#{% url path.to.view as the_url %}
#{% if the_url %}
#  <a href="{{ the_url }}">Link to optional stuff</a>
#{% endif %}

# In code:
#from django.core.urlresolvers import reverse
#
#def myview(request):
#    return HttpResponseRedirect(reverse('arch-summary', args=[1945]))
