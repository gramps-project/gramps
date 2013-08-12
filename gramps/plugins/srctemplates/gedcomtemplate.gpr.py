# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Tim G L Lyons
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

"""
Registering srctemplates for GRAMPS.
"""

#
# SrcTemplates distributed with Gramps
#

# GEDCOM
plg = newplugin()
plg.id    = 'GEDCOM styles'
plg.name  = _("GEDCOM Source Templates")
plg.description =  _("Defines source templates corresponding with GEDCOM.")
plg.version = '1.0'
plg.gramps_target_version = '4.1'
plg.status = STABLE
plg.fname = 'gedcomtemplate.py'
plg.ptype = SRCTEMPLATE
