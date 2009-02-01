# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Id$

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class TODOGramplet(Gramplet):
    def init(self):
        # GUI setup:
        self.set_tooltip(_("Enter text"))
        self.gui.textview.set_editable(True)
        self.append_text(_("Enter your TODO list here."))

    def on_load(self):
        self.load_data_to_text()

    def on_save(self):
        self.gui.data = [] # clear out old data
        self.save_text_to_data()

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="TODO Gramplet", 
         tname=_("TODO Gramplet"), 
         height=300,
         expand=True,
         content = TODOGramplet,
         title=_("TODO List"),
         )

