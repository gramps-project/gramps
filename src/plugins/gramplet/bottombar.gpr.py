#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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
# Register Gramplet
#
#------------------------------------------------------------------------
register(GRAMPLET, 
         id="Person Details Gramplet", 
         name=_("Person Details Gramplet"), 
         description = _("Gramplet showing details of a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="PersonDetails.py",
         height=200,
         gramplet = 'PersonDetails',
         gramplet_title=_("Details"),
         )

register(GRAMPLET, 
         id="Person Gallery Gramplet", 
         name=_("Person Gallery Gramplet"), 
         description = _("Gramplet showing media objects for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="PersonGallery.py",
         height=200,
         gramplet = 'PersonGallery',
         gramplet_title=_("Gallery"),
         )

register(GRAMPLET, 
         id="Person Residence Gramplet", 
         name=_("Person Residence Gramplet"), 
         description = _("Gramplet showing residence events for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="PersonResidence.py",
         height=200,
         gramplet = 'PersonResidence',
         gramplet_title=_("Residence"),
         )

register(GRAMPLET, 
         id="Person Attributes Gramplet", 
         name=_("Person Attributes Gramplet"), 
         description = _("Gramplet showing the attributes of a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="PersonAttributes.py",
         height=200,
         gramplet = 'PersonAttributes',
         gramplet_title=_("Attributes"),
         )
