#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# webapp/grampsdb/admin.py

from gramps.webapp.grampsdb.models import *
from django.contrib import admin

## FIXME: this no longer works in Django 1.5
class MyAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_context=None):
        result = super(MyAdmin, self).change_view(request, object_id, extra_context)
        if '_addanother' not in request.POST and '_continue' not in request.POST:
            result['Location'] = "/"
        return result

for type_name in get_tables("all"):
    admin.site.register(type_name[1], admin.ModelAdmin)
admin.site.register(Profile, admin.ModelAdmin)

