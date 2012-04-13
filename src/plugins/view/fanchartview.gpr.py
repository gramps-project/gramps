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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# plugins/view/fanchartview.gpr.py
# $Id$

register(VIEW, 
         id    = 'fanchartview',
         name  = _("Fan Chart View"),
         category = ("Ancestry", _("Ancestry")),
         description =  _("The view showing relations through a fanchart"),
         version = '1.0',
         gramps_target_version = '3.5',
         status = STABLE,
         fname = 'fanchartview.py',
         authors = [u"Douglas S. Blank"],
         authors_email = ["doug.blank@gmail.com"],
         viewclass = 'FanChartView',
         stock_icon = 'gramps-fanchart',
  )
