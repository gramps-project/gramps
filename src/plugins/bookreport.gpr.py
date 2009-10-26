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

# $Id: $

#------------------------------------------------------------------------
#
# Book plugin
#
#------------------------------------------------------------------------

register(REPORT, 
id    = 'book',
name  = _("Book Report"),
description =  _("Produces a book containing several reports."),
version = '1.0',
status = STABLE,
fname = 'BookReport.py',
authors = ["Alex Roitman"],
authors_email = ["shura@gramps-project.org"],
category = CATEGORY_BOOK,
reportclass = 'BookReportSelector',
optionclass = 'cl_report',
report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
  )
