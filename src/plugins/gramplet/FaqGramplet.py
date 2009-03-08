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
# Register Gramplet
#
#------------------------------------------------------------------------
class FAQGramplet(Gramplet):
    def init(self):
        self.set_use_markup(True)
        self.clear_text()
        self.render_text("Draft of a <a wiki='FAQ'>Frequently Asked Questions</a> Gramplet\n\n")
        self.render_text("  1. <a href='http://bugs.gramps-project.org/'>Test 1</a>\n")
        self.render_text("  2. <a href='http://gramps-project.org//'>Test 2</a>\n")

register(type="gramplet", 
         name="FAQ Gramplet", 
         tname=_("FAQ Gramplet"), 
         height=300,
         content = FAQGramplet,
         title=_("FAQ"),
         gramps="3.1.0",
         version="1.0.0",
         )

