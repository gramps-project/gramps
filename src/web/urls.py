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
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/$', view_detail),
)
