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

register(GRAMPLET, 
         id="Person Filter Gramplet", 
         name=_("Person Filter Gramplet"), 
         description = _("Gramplet providing a person filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'PersonFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Family Filter Gramplet", 
         name=_("Family Filter Gramplet"), 
         description = _("Gramplet providing a family filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'FamilyFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Event Filter Gramplet", 
         name=_("Event Filter Gramplet"), 
         description = _("Gramplet providing an event filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'EventFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Source Filter Gramplet", 
         name=_("Source Filter Gramplet"), 
         description = _("Gramplet providing a source filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'SourceFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Place Filter Gramplet", 
         name=_("Place Filter Gramplet"), 
         description = _("Gramplet providing a place filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'PlaceFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Media Filter Gramplet", 
         name=_("Media Filter Gramplet"), 
         description = _("Gramplet providing a media filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'MediaFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Repository Filter Gramplet", 
         name=_("Repository Filter Gramplet"), 
         description = _("Gramplet providing a repository filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'RepositoryFilter',
         gramplet_title=_("Filter"),
         )

register(GRAMPLET, 
         id="Note Filter Gramplet", 
         name=_("Note Filter Gramplet"), 
         description = _("Gramplet providing a note filter"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Filter.py",
         height=200,
         gramplet = 'NoteFilter',
         gramplet_title=_("Filter"),
         )
