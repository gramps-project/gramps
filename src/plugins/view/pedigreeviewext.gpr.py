# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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
#

# $Id: view.gpr.py 13633 2009-11-19 17:32:11Z ldnp $

#------------------------------------------------------------------------
#
# default views of Gramps
#
#------------------------------------------------------------------------

register(VIEW, 
id    = 'pedigreeviewext',
name  = _("Pedigree View"),
description =  _("The view showing an ancestor pedigree of the selected person"),
version = '1.0',
status = STABLE,
fname = 'pedigreeviewext.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Ancestry", _("Ancestry")),
viewclass = 'PedigreeViewExt',
order = START,
  )
