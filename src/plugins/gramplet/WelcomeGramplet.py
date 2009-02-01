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
from DataViews import register
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
def make_welcome_content(gui):
    text = _(
        'Welcome to GRAMPS!\n\n'
        'GRAMPS is a software package designed for genealogical research.'
        ' Although similar to other genealogical programs, GRAMPS offers '
        'some unique and powerful features.\n\n'
        'GRAMPS is an Open Source Software package, which means you are '
        'free to make copies and distribute it to anyone you like. It\'s '
        'developed and maintained by a worldwide team of volunteers whose'
        ' goal is to make GRAMPS powerful, yet easy to use.\n\n'
        'Getting Started\n\n'
        'The first thing you must do is to create a new Family Tree. To '
        'create a new Family Tree (sometimes called a database) select '
        '"Family Trees" from the menu, pick "Manage Family Trees", press '
        '"New" and name your database. For more details, please read the '
        'User Manual, or the on-line manual at http://gramps-project.org.\n\n'
        'You are currently reading from the "Gramplets" page, where you can'
        ' add your own gramplets.\n\n'
        'You can right-click on the background of this page to add additional'
        ' gramplets and change the number of columns. You can also drag the '
        'Properties button to reposition the gramplet on this page, and detach'
        ' the gramplet to float above GRAMPS. If you close GRAMPS with a gramplet'
        ' detached, it will re-open detached the next time you start '
        'GRAMPS.'
            )
    gui.set_text(text)

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Welcome Gramplet", 
         tname=_("Welcome Gramplet"), 
         height=300,
         expand=True,
         content = make_welcome_content,
         title=_("Welcome to GRAMPS!"),
         )
