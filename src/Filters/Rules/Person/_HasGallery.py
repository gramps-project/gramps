#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._HasGalleryBase import HasGalleryBase

#-------------------------------------------------------------------------
# "People with media object reference "
#-------------------------------------------------------------------------
class HavePhotos(HasGalleryBase):
    """Rule that checks for person who has media object reference"""

    name        = _('People with <count> media')
    description = _("Matches people with a certain number of items in the gallery")

    def __init__(self, arg):
        # Upgrade from pre 3.1 HasPhotos filter, use defaults that correspond
        # Previous filter had 0 arguments
        if len(arg) == 0:
            HasGalleryBase.__init__(self, ["0", 'greater than'])
        else:
            HasGalleryBase.__init__(self, arg)
