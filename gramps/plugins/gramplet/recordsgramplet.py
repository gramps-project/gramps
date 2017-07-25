# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2008-2011 Reinhard Müller
# Copyright (C) 2010 Jakim Friant
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

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.plugins.lib.librecords import find_records, CALLNAME_DONTUSE
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# RecordsGramplet
#
#------------------------------------------------------------------------
class RecordsGramplet(Gramplet):

    def init(self):
        self.set_use_markup(True)
        self.set_tooltip(_("Double-click name for details"))
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.connect(self.dbstate.db, 'person-rebuild', self.update)
        self.connect(self.dbstate.db, 'family-rebuild', self.update)

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        records = find_records(self.dbstate.db, None, 3, CALLNAME_DONTUSE)
        self.set_text("")
        for (text, varname, top) in records:
            yield True
            self.render_text("<b>%s</b>" % text)
            last_value = None
            rank = 0
            for (number, (sort, value, name, handletype, handle)) in enumerate(top):
                if value != last_value:
                    last_value = value
                    rank = number
                self.append_text("\n  %s. " % (rank+1))
                self.link(str(name), handletype, handle)
                self.append_text(" (%s)" % value)
            self.append_text("\n")
        self.append_text("", scroll_to='begin')
        yield False
