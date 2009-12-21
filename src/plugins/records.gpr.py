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

# $Id$

#------------------------------------------------------------------------
#
# records gramplet and text report
#
#------------------------------------------------------------------------

register(REPORT, 
id    = 'records',
name  = _("Records Report"),
description =  _("Shows some interesting records about people and families"),
version = '1.0',
status = STABLE,
fname = 'Records.py',
authors = [u"Reinhard Müller"],
authors_email = ["reinhard.mueller@bytewise.at"],
category = CATEGORY_TEXT,
reportclass = 'RecordsReport',
optionclass = 'RecordsReportOptions',
report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI, REPORT_MODE_BKI]
  )

register(GRAMPLET, 
id    = 'Records Gramplet',
name  = _("Records Gramplet"),
description =  _("Shows some interesting records about people and families"),
version = '1.0',
status = STABLE,
fname = 'Records.py',
authors = [u"Reinhard Müller"],
authors_email = ["reinhard.mueller@bytewise.at"],
gramplet = 'RecordsGramplet',
height = 230,
expand = True,
gramplet_title = _("Records")
  )
