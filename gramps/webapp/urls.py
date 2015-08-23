# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Url handler """

#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# Django and Gramps Modules
#
#------------------------------------------------------------------------
from gramps.gen.const import IMAGE_DIR, ROOT_DIR, DATA_DIR
from django.conf.urls import patterns, url, include
from django.contrib import admin

admin.autodiscover()

from gramps.webapp.grampsdb.views import *

urlpatterns = patterns('',
    # Specific matches first:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    # Static serves! DANGEROUS in production:
     (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': DATA_DIR,
#       os.path.join(ROOT_DIR, "plugins", "webstuff"),
       'show_indexes':  True},
      ),
     (r'^images/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root':  IMAGE_DIR,
       'show_indexes':  True},
      ),
    # Django 1.5.4
     (r'^static/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root':  '/usr/share/pyshared/django/contrib/admin/static/',
       'show_indexes':  True},
     ),
    # Django 1.5.4
)

# The rest will match views:
urlpatterns += patterns('',
    (r'^$', main_page),
    ## Prior to django 1.5, use this:
    ##(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to',
    ##{'url': '/styles/images/favicon.ico'}),
    # Django 1.5.4:
    (r'^favicon\.ico$', 'django.shortcuts.redirect',
     {'url': '/styles/images/favicon.ico'}),
    (r'^user/$', user_page),
    (r'^json/$', process_json_request),
    (r'^user/(\w+)/$', user_page),
    (r'^browse/$', browse_page),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^(?P<view>(\w+))/$',
     view_list),                    # /view/
    (r'^(?P<view>(\w+))/add$',
     action,
     {"handle": None, "act": "add"}),                   # /view/add
    (r'^(?P<view>(\w+))/add/(?P<item>(\w+))/(?P<handle>(\w+))$',
     add_to),             # /view/add/item/handle
    (r'^(?P<view>(\w+))/share/(?P<item>(\w+))/(?P<handle>(\w+))$',
     add_share),          # /view/share/item/handle
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/$', action,
     {"act": "view"}),    # /view/handle/
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/(?P<act>(\w+))$',
     action),             # /view/handle/action
    (r'^(?P<ref_by>(\w+))/(?P<handle>(\w+))/reference/(?P<ref_to>(\w+))/(?P<order>(\w+))$',
     process_reference),  # /view/handle/reference/item/order
    (r'^person/(?P<handle>(\w+))/name/(?P<order>(\w+))$', process_name),
    (r'^person/(?P<handle>(\w+))/name/(?P<order>(\w+))/(?P<act>(\w+))$',
     process_name),

    (r'^person/(?P<handle>(\w+))/name/(?P<order>(\w+))/surname/(?P<sorder>(\w+))$',
     process_surname),
    (r'^person/(?P<handle>(\w+))/name/(?P<order>(\w+))/surname/(?P<sorder>(\w+))/(?P<act>(\w+))$',
     process_surname),
    (r'^family/(?P<handle>(\w+))/(?P<act>(\w+))/child/(?P<child>(\w+))$', process_child),
##    (r'^profile/(?P<position>(\w+)/)$', ),
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/(?P<act>(\w+))/(?P<item>(\w+))/(?P<index>(\w+))$',
     process_list_item),
    (r'^note/(?P<action>(\w+))/person/(?P<handle>(\w+))/name/(?P<order>(\w+))$',
     process_note_on_name),
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
