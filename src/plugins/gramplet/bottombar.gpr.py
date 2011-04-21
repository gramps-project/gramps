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
         id="Repository Details Gramplet", 
         name=_("Repository Details Gramplet"), 
         description = _("Gramplet showing details of a repository"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="RepositoryDetails.py",
         height=200,
         gramplet = 'RepositoryDetails',
         gramplet_title=_("Details"),
         )

register(GRAMPLET, 
         id="Place Details Gramplet", 
         name=_("Place Details Gramplet"), 
         description = _("Gramplet showing details of a place"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="PlaceDetails.py",
         height=200,
         gramplet = 'PlaceDetails',
         gramplet_title=_("Details"),
         )

register(GRAMPLET, 
         id="Media Preview Gramplet", 
         name=_("Media Preview Gramplet"), 
         description = _("Gramplet showing a preview of a media object"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="MediaPreview.py",
         height=200,
         gramplet = 'MediaPreview',
         gramplet_title=_("Preview"),
         )

try:
    import pyexiv2
    available = True
except:
    print _("WARNING: pyexiv2 module not loaded.  "
            "Image metadata functionality will not be available.")
    available = False

if available:
    register(GRAMPLET, 
            id = "Metadata Viewer Gramplet", 
            name = _("Metadata Viewer Gramplet"), 
            description = _("Gramplet showing metadata for a media object"),
            version = "1.0.0",
            gramps_target_version = "3.3",
            status = STABLE,
            fname = "MetadataViewer.py",
            height = 200,
            gramplet = 'MetadataViewer',
            gramplet_title = _("Image Metadata"),
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
         id="Person Events Gramplet", 
         name=_("Person Events Gramplet"), 
         description = _("Gramplet showing the events for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Events.py",
         height=200,
         gramplet = 'PersonEvents',
         gramplet_title=_("Events"),
         )

register(GRAMPLET, 
         id="Family Events Gramplet", 
         name=_("Family Events Gramplet"), 
         description = _("Gramplet showing the events for a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Events.py",
         height=200,
         gramplet = 'FamilyEvents',
         gramplet_title=_("Events"),
         )

register(GRAMPLET, 
         id="Person Gallery Gramplet", 
         name=_("Person Gallery Gramplet"), 
         description = _("Gramplet showing media objects for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Gallery.py",
         height=200,
         gramplet = 'PersonGallery',
         gramplet_title=_("Gallery"),
         )

register(GRAMPLET, 
         id="Event Gallery Gramplet", 
         name=_("Event Gallery Gramplet"), 
         description = _("Gramplet showing media objects for an event"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Gallery.py",
         height=200,
         gramplet = 'EventGallery',
         gramplet_title=_("Gallery"),
         )

register(GRAMPLET, 
         id="Place Gallery Gramplet", 
         name=_("Place Gallery Gramplet"), 
         description = _("Gramplet showing media objects for a place"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Gallery.py",
         height=200,
         gramplet = 'PlaceGallery',
         gramplet_title=_("Gallery"),
         )

register(GRAMPLET, 
         id="Source Gallery Gramplet", 
         name=_("Source Gallery Gramplet"), 
         description = _("Gramplet showing media objects for a source"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Gallery.py",
         height=200,
         gramplet = 'SourceGallery',
         gramplet_title=_("Gallery"),
         )

register(GRAMPLET, 
         id="Person Attributes Gramplet", 
         name=_("Person Attributes Gramplet"), 
         description = _("Gramplet showing the attributes of a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Attributes.py",
         height=200,
         gramplet = 'PersonAttributes',
         gramplet_title=_("Attributes"),
         )

register(GRAMPLET, 
         id="Event Attributes Gramplet", 
         name=_("Event Attributes Gramplet"), 
         description = _("Gramplet showing the attributes of an event"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Attributes.py",
         height=200,
         gramplet = 'EventAttributes',
         gramplet_title=_("Attributes"),
         )

register(GRAMPLET, 
         id="Family Attributes Gramplet", 
         name=_("Family Attributes Gramplet"), 
         description = _("Gramplet showing the attributes of a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Attributes.py",
         height=200,
         gramplet = 'FamilyAttributes',
         gramplet_title=_("Attributes"),
         )

register(GRAMPLET, 
         id="Media Attributes Gramplet", 
         name=_("Media Attributes Gramplet"), 
         description = _("Gramplet showing the attributes of a media object"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Attributes.py",
         height=200,
         gramplet = 'MediaAttributes',
         gramplet_title=_("Attributes"),
         )

register(GRAMPLET, 
         id="Person Notes Gramplet", 
         name=_("Person Notes Gramplet"), 
         description = _("Gramplet showing the notes for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'PersonNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Event Notes Gramplet", 
         name=_("Event Notes Gramplet"), 
         description = _("Gramplet showing the notes for an event"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'EventNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Family Notes Gramplet", 
         name=_("Family Notes Gramplet"), 
         description = _("Gramplet showing the notes for a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'FamilyNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Place Notes Gramplet", 
         name=_("Place Notes Gramplet"), 
         description = _("Gramplet showing the notes for a place"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'PlaceNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Source Notes Gramplet", 
         name=_("Source Notes Gramplet"), 
         description = _("Gramplet showing the notes for a source"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'SourceNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Repository Notes Gramplet", 
         name=_("Repository Notes Gramplet"), 
         description = _("Gramplet showing the notes for a repository"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'RepositoryNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Media Notes Gramplet", 
         name=_("Media Notes Gramplet"), 
         description = _("Gramplet showing the notes for a media object"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Notes.py",
         height=200,
         gramplet = 'MediaNotes',
         gramplet_title=_("Notes"),
         )

register(GRAMPLET, 
         id="Person Sources Gramplet", 
         name=_("Person Sources Gramplet"), 
         description = _("Gramplet showing the sources for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Sources.py",
         height=200,
         gramplet = 'PersonSources',
         gramplet_title=_("Sources"),
         )

register(GRAMPLET, 
         id="Event Sources Gramplet", 
         name=_("Event Sources Gramplet"), 
         description = _("Gramplet showing the sources for an event"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Sources.py",
         height=200,
         gramplet = 'EventSources',
         gramplet_title=_("Sources"),
         )

register(GRAMPLET, 
         id="Family Sources Gramplet", 
         name=_("Family Sources Gramplet"), 
         description = _("Gramplet showing the sources for a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Sources.py",
         height=200,
         gramplet = 'FamilySources',
         gramplet_title=_("Sources"),
         )

register(GRAMPLET, 
         id="Place Sources Gramplet", 
         name=_("Place Sources Gramplet"), 
         description = _("Gramplet showing the sources for a place"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Sources.py",
         height=200,
         gramplet = 'PlaceSources',
         gramplet_title=_("Sources"),
         )

register(GRAMPLET, 
         id="Media Sources Gramplet", 
         name=_("Media Sources Gramplet"), 
         description = _("Gramplet showing the sources for a media object"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Sources.py",
         height=200,
         gramplet = 'MediaSources',
         gramplet_title=_("Sources"),
         )

register(GRAMPLET, 
         id="Person Children Gramplet", 
         name=_("Person Children Gramplet"), 
         description = _("Gramplet showing the children of a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Children.py",
         height=200,
         gramplet = 'PersonChildren',
         gramplet_title=_("Children"),
         )

register(GRAMPLET, 
         id="Family Children Gramplet", 
         name=_("Family Children Gramplet"), 
         description = _("Gramplet showing the children of a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Children.py",
         height=200,
         gramplet = 'FamilyChildren',
         gramplet_title=_("Children"),
         )

register(GRAMPLET, 
         id="Person Backlinks Gramplet", 
         name=_("Person Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a person"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'PersonBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Event Backlinks Gramplet", 
         name=_("Event Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for an event"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'EventBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Family Backlinks Gramplet", 
         name=_("Family Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a family"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'FamilyBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Place Backlinks Gramplet", 
         name=_("Place Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a place"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'PlaceBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Source Backlinks Gramplet", 
         name=_("Source Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a source"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'SourceBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Repository Backlinks Gramplet", 
         name=_("Repository Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a repository"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'RepositoryBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Media Backlinks Gramplet", 
         name=_("Media Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a media object"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'MediaBacklinks',
         gramplet_title=_("References"),
         )

register(GRAMPLET, 
         id="Note Backlinks Gramplet", 
         name=_("Note Backlinks Gramplet"), 
         description = _("Gramplet showing the backlinks for a note"),
         version="1.0.0",
         gramps_target_version="3.3",
         status = STABLE,
         fname="Backlinks.py",
         height=200,
         gramplet = 'NoteBacklinks',
         gramplet_title=_("References"),
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
