# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008 - 2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2009         B. Malengier <benny.malengier@gmail.com>
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
#

register(EXPORT,
         id                   = "export_django",
         name                 = _('Django Export'),
         description          = _('Django is a web framework working on a '
                                  'configured database'),
         version              = '1.0',
         gramps_target_version= '3.2',
         status               = UNSTABLE,
         export_options_title = _('Django options'), 
         export_options       = 'NoFilenameOptions',
         export_function      = 'export_all',
         extension            = "django",
         fname                = "ExportDjango.py",
         )

