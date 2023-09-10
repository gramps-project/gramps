# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2011 Tim G L Lyons
# Copyright (C) 2020 Matthias Kemmer
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from gramps.gen.plug._pluginreg import register, STABLE, UNSTABLE, GRAMPLET
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.2"
GRAMPLET_HELP = _("Gramps_5.2_Wiki_Manual_-_Gramplets#Gramplet_List")
DEBUG_HELP = _("Gramps_5.2_Wiki_Manual_-_Tools#Debug")

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# ------------------------------------------------------------------------
#
# Register Gramplet
#
# ------------------------------------------------------------------------
register(
    GRAMPLET,
    id="Age on Date",
    name=_("Age on Date"),
    description=_("Gramplet showing ages of living people on a specific date"),
    version="2.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="ageondategramplet.py",
    height=200,
    gramplet="AgeOnDateGramplet",
    gramplet_title=_("Age on Date"),
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Age Stats",
    name=_("Age Stats"),
    description=_("Gramplet showing graphs of various ages"),
    status=STABLE,
    fname="agestats.py",
    height=100,
    expand=True,
    gramplet="AgeStatsGramplet",
    gramplet_title=_("Age Stats"),
    detached_width=600,
    detached_height=450,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Calendar",
    name=_("Calendar"),
    description=_("Gramplet showing calendar and events on specific dates in history"),
    status=STABLE,
    fname="calendargramplet.py",
    height=200,
    gramplet="CalendarGramplet",
    gramplet_title=_("Calendar"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Descendant",
    name=_("Descendants"),
    description=_("Gramplet showing active person's descendants"),
    status=STABLE,
    fname="descendant.py",
    height=100,
    expand=True,
    gramplet="Descendant",
    gramplet_title=_("Descendants"),
    detached_width=500,
    detached_height=500,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Ancestor",
    name=_("Ancestors"),
    description=_("Gramplet showing active person's ancestors"),
    status=STABLE,
    fname="ancestor.py",
    height=100,
    expand=True,
    gramplet="Ancestor",
    gramplet_title=_("Ancestors"),
    detached_width=500,
    detached_height=500,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Fan Chart",
    name=_("Fan Chart"),
    description=_("Gramplet showing active person's direct ancestors as a fanchart"),
    status=STABLE,
    fname="fanchartgramplet.py",
    height=430,
    expand=True,
    gramplet="FanChartGramplet",
    detached_height=550,
    detached_width=475,
    gramplet_title=_("Fan Chart"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Descendant Fan Chart",
    name=_("Descendant Fan Chart"),
    description=_("Gramplet showing active person's direct descendants as a fanchart"),
    status=STABLE,
    fname="fanchartdescgramplet.py",
    height=430,
    expand=True,
    gramplet="FanChartDescGramplet",
    detached_height=550,
    detached_width=475,
    gramplet_title=_("Descendant Fan"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="2-Way Fan Chart",
    name=_("2-Way Fan Chart"),
    description=_(
        "Gramplet showing active person's direct ancestors and descendants as a fanchart"
    ),
    status=STABLE,
    fname="fanchart2waygramplet.py",
    height=300,
    expand=True,
    gramplet="FanChart2WayGramplet",
    detached_height=300,
    detached_width=300,
    gramplet_title=_("2-Way Fan"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="FAQ",
    name=_("FAQ"),
    description=_("Gramplet showing frequently asked questions"),
    status=STABLE,
    fname="faqgramplet.py",
    height=300,
    gramplet="FAQGramplet",
    gramplet_title=_("FAQ"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Given Name Cloud",
    name=_("Given Name Cloud"),
    description=_("Gramplet showing all given names as a text cloud"),
    status=STABLE,
    fname="givennamegramplet.py",
    height=300,
    expand=True,
    gramplet="GivenNameCloudGramplet",
    gramplet_title=_("Given Name Cloud"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Pedigree",
    name=_("Pedigree"),
    description=_("Gramplet showing active person's ancestors"),
    status=STABLE,
    fname="pedigreegramplet.py",
    height=300,
    gramplet="PedigreeGramplet",
    gramplet_title=_("Pedigree"),
    expand=True,
    detached_width=600,
    detached_height=400,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Quick View",
    name=_("Quick View"),
    description=_("Gramplet showing an active item Quick View"),
    status=STABLE,
    fname="quickviewgramplet.py",
    height=300,
    expand=True,
    gramplet="QuickViewGramplet",
    gramplet_title=_("Quick View"),
    detached_width=600,
    detached_height=400,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Relatives",
    name=_("Relatives"),
    description=_("Gramplet showing active person's relatives"),
    status=STABLE,
    fname="relativegramplet.py",
    height=200,
    gramplet="RelativesGramplet",
    gramplet_title=_("Relatives"),
    detached_width=250,
    detached_height=300,
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Session Log",
    name=_("Session Log"),
    description=_("Gramplet showing all activity for this session"),
    status=STABLE,
    fname="sessionloggramplet.py",
    height=230,
    # data=['no'],
    gramplet="LogGramplet",
    gramplet_title=_("Session Log"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Statistics",
    name=_("Statistics"),
    description=_("Gramplet showing summary data of the Family Tree"),
    status=STABLE,
    fname="statsgramplet.py",
    height=230,
    expand=True,
    gramplet="StatsGramplet",
    gramplet_title=_("Statistics"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Surname Cloud",
    name=_("Surname Cloud"),
    description=_("Gramplet showing all surnames as a text cloud"),
    status=STABLE,
    fname="surnamecloudgramplet.py",
    height=300,
    expand=True,
    gramplet="SurnameCloudGramplet",
    gramplet_title=_("Surname Cloud"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="To Do",
    name=_("To Do", "gramplet"),
    description=_("Gramplet for displaying a To Do list"),
    status=STABLE,
    fname="todogramplet.py",
    height=300,
    expand=True,
    gramplet="ToDoGramplet",
    gramplet_title=_("To Do", "gramplet"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    navtypes=["Dashboard"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Top Surnames",
    name=_("Top Surnames"),
    description=_("Gramplet showing most frequent surnames in this tree"),
    status=STABLE,
    fname="topsurnamesgramplet.py",
    height=230,
    gramplet="TopSurnamesGramplet",
    gramplet_title=_("Top Surnames"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Welcome",
    name=_("Welcome"),
    description=_("Gramplet showing a welcome message"),
    status=STABLE,
    fname="welcomegramplet.py",
    height=300,
    expand=True,
    gramplet="WelcomeGramplet",
    gramplet_title=_("Welcome to Gramps!"),
    version="1.0.1",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="What's Next",
    name=_("What's Next"),
    description=_("Gramplet suggesting items to research"),
    status=STABLE,
    fname="whatsnext.py",
    height=230,
    expand=True,
    gramplet="WhatNextGramplet",
    gramplet_title=_("What's Next?"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    help_url=GRAMPLET_HELP,
)

# ------------------------------------------------------------------------
# Bottombar
# ------------------------------------------------------------------------
register(
    GRAMPLET,
    id="Person Details",
    name=_("Person Details"),
    description=_("Gramplet showing details of a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="persondetails.py",
    height=200,
    gramplet="PersonDetails",
    gramplet_title=_("Details"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Repository Details",
    name=_("Repository Details"),
    description=_("Gramplet showing details of a repository"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="repositorydetails.py",
    height=200,
    gramplet="RepositoryDetails",
    gramplet_title=_("Details"),
    navtypes=["Repository"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Details",
    name=_("Place Details"),
    description=_("Gramplet showing details of a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="placedetails.py",
    height=200,
    gramplet="PlaceDetails",
    gramplet_title=_("Details"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Preview",
    name=_("Media Preview"),
    description=_("Gramplet showing a preview of a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="mediapreview.py",
    height=200,
    gramplet="MediaPreview",
    gramplet_title=_("Media Preview"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

try:
    from gi import Repository

    repository = Repository.get_default()
    if repository.enumerate_versions("GExiv2"):
        import gi

        gi.require_version("GExiv2", "0.10")
        from gi.repository import GExiv2

        available = True
    else:
        available = False
except (ImportError, ValueError):
    available = False

if available:
    register(
        GRAMPLET,
        id="Metadata Viewer",
        name=_("Image Metadata"),
        description=_("Gramplet showing metadata for a media object"),
        version="1.0.0",
        gramps_target_version=MODULE_VERSION,
        status=STABLE,
        fname="metadataviewer.py",
        height=200,
        gramplet="MetadataViewer",
        gramplet_title=_("Image Metadata"),
        navtypes=["Media"],
        help_url=GRAMPLET_HELP,
    )
else:
    from gramps.gen.config import config

    if not config.get("interface.ignore-gexiv2"):
        from gramps.gen.constfunc import has_display

        if has_display():
            from gramps.gui.dialog import MessageHideDialog
            from gramps.gen.const import URL_WIKISTRING

            gexiv2_dict = {
                "gramps_wiki_build_gexiv2_url": URL_WIKISTRING
                + "GEPS_029:_GTK3-GObject_introspection"
                "_Conversion#GExiv2_for_Image_metadata"
            }
            title = _("GExiv2 module not loaded.")
            message = _(
                "Image metadata functionality will not be available.\n"
                "To build it for Gramps see "
                "%(gramps_wiki_build_gexiv2_url)s" % gexiv2_dict
            )
            if uistate:
                MessageHideDialog(
                    title, message, "interface.ignore-gexiv2", parent=uistate.window
                )
            else:
                MessageHideDialog(title, message, "interface.ignore-gexiv2")

register(
    GRAMPLET,
    id="Person Residence",
    name=_("Person Residence"),
    description=_("Gramplet showing residence events for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="personresidence.py",
    height=200,
    gramplet="PersonResidence",
    gramplet_title=_("Residence"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Events",
    name=_("Person Events"),
    description=_("Gramplet showing the events for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="events.py",
    height=200,
    gramplet="PersonEvents",
    gramplet_title=_("Events"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Events",
    name=_("Family Events"),
    description=_("Gramplet showing the events for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="events.py",
    height=200,
    gramplet="FamilyEvents",
    gramplet_title=_("Events"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Gallery",
    name=_("Person Gallery"),
    description=_("Gramplet showing media objects for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="PersonGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Gallery",
    name=_("Family Gallery"),
    description=_("Gramplet showing media objects for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="FamilyGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Gallery",
    name=_("Event Gallery"),
    description=_("Gramplet showing media objects for an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="EventGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Gallery",
    name=_("Place Gallery"),
    description=_("Gramplet showing media objects for a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="PlaceGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source Gallery",
    name=_("Source Gallery"),
    description=_("Gramplet showing media objects for a source"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="SourceGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation Gallery",
    name=_("Citation Gallery"),
    description=_("Gramplet showing media objects for a citation"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gallery.py",
    height=200,
    gramplet="CitationGallery",
    gramplet_title=_("Gallery"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Attributes",
    name=_("Person Attributes"),
    description=_("Gramplet showing the attributes of a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="PersonAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Attributes",
    name=_("Event Attributes"),
    description=_("Gramplet showing the attributes of an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="EventAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Attributes",
    name=_("Family Attributes"),
    description=_("Gramplet showing the attributes of a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="FamilyAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Attributes",
    name=_("Media Attributes"),
    description=_("Gramplet showing the attributes of a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="MediaAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source Attributes",
    name=_("Source Attributes"),
    description=_("Gramplet showing the attributes of a source object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="SourceAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation Attributes",
    name=_("Citation Attributes"),
    description=_("Gramplet showing the attributes of a citation object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="attributes.py",
    height=200,
    gramplet="CitationAttributes",
    gramplet_title=_("Attributes"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Notes",
    name=_("Person Notes"),
    description=_("Gramplet showing the notes for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="PersonNotes",
    gramplet_title=_("Notes"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Notes",
    name=_("Event Notes"),
    description=_("Gramplet showing the notes for an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="EventNotes",
    gramplet_title=_("Notes"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Notes",
    name=_("Family Notes"),
    description=_("Gramplet showing the notes for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="FamilyNotes",
    gramplet_title=_("Notes"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Notes",
    name=_("Place Notes"),
    description=_("Gramplet showing the notes for a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="PlaceNotes",
    gramplet_title=_("Notes"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source Notes",
    name=_("Source Notes"),
    description=_("Gramplet showing the notes for a source"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="SourceNotes",
    gramplet_title=_("Notes"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation Notes",
    name=_("Citation Notes"),
    description=_("Gramplet showing the notes for a citation"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="CitationNotes",
    gramplet_title=_("Notes"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Repository Notes",
    name=_("Repository Notes"),
    description=_("Gramplet showing the notes for a repository"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="RepositoryNotes",
    gramplet_title=_("Notes"),
    navtypes=["Repository"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Notes",
    name=_("Media Notes"),
    description=_("Gramplet showing the notes for a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="MediaNotes",
    gramplet_title=_("Notes"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Note Notes",
    name=_("Notes"),
    description=_("Gramplet showing the selected note"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="notes.py",
    height=200,
    gramplet="NoteNotes",
    gramplet_title=_("Notes"),
    navtypes=["Note"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Citations",
    name=_("Person Citations"),
    description=_("Gramplet showing the citations for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="citations.py",
    height=200,
    gramplet="PersonCitations",
    gramplet_title=_("Citations"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Citations",
    name=_("Event Citations"),
    description=_("Gramplet showing the citations for an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="citations.py",
    height=200,
    gramplet="EventCitations",
    gramplet_title=_("Citations"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Citations",
    name=_("Family Citations"),
    description=_("Gramplet showing the citations for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="citations.py",
    height=200,
    gramplet="FamilyCitations",
    gramplet_title=_("Citations"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Citations",
    name=_("Place Citations"),
    description=_("Gramplet showing the citations for a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="citations.py",
    height=200,
    gramplet="PlaceCitations",
    gramplet_title=_("Citations"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Citations",
    name=_("Media Citations"),
    description=_("Gramplet showing the citations for a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="citations.py",
    height=200,
    gramplet="MediaCitations",
    gramplet_title=_("Citations"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Children",
    name=_("Person Children"),
    description=_("Gramplet showing the children of a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="children.py",
    height=200,
    gramplet="PersonChildren",
    gramplet_title=_("Children"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Children",
    name=_("Family Children"),
    description=_("Gramplet showing the children of a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="children.py",
    height=200,
    gramplet="FamilyChildren",
    gramplet_title=_("Children"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Backlinks",
    name=_("Person References"),
    description=_("Gramplet showing the backlink references for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="PersonBacklinks",
    gramplet_title=_("References"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Backlinks",
    name=_("Event References"),
    description=_("Gramplet showing the backlink references for an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="EventBacklinks",
    gramplet_title=_("References"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Backlinks",
    name=_("Family References"),
    description=_("Gramplet showing the backlink references for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="FamilyBacklinks",
    gramplet_title=_("References"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Backlinks",
    name=_("Place References"),
    description=_("Gramplet showing the backlink references for a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="PlaceBacklinks",
    gramplet_title=_("References"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source Backlinks",
    name=_("Source References"),
    description=_("Gramplet showing the backlink references for a source"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="SourceBacklinks",
    gramplet_title=_("References"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation Backlinks",
    name=_("Citation References"),
    description=_("Gramplet showing the backlink references for a citation"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="CitationBacklinks",
    gramplet_title=_("References"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Repository Backlinks",
    name=_("Repository References"),
    description=_("Gramplet showing the backlink references for a repository"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="RepositoryBacklinks",
    gramplet_title=_("References"),
    navtypes=["Repository"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Backlinks",
    name=_("Media References"),
    description=_("Gramplet showing the backlink references for a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="MediaBacklinks",
    gramplet_title=_("References"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Note Backlinks",
    name=_("Note References"),
    description=_("Gramplet showing the backlink references for a note"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="backlinks.py",
    height=200,
    gramplet="NoteBacklinks",
    gramplet_title=_("References"),
    navtypes=["Note"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person Filter",
    name=_("Person Filter"),
    description=_("Gramplet providing a person filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="PersonFilter",
    gramplet_title=_("Filter"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family Filter",
    name=_("Family Filter"),
    description=_("Gramplet providing a family filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="FamilyFilter",
    gramplet_title=_("Filter"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event Filter",
    name=_("Event Filter"),
    description=_("Gramplet providing an event filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="EventFilter",
    gramplet_title=_("Filter"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source Filter",
    name=_("Source Filter"),
    description=_("Gramplet providing a source filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="SourceFilter",
    gramplet_title=_("Filter"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation Filter",
    name=_("Citation Filter"),
    description=_("Gramplet providing a citation filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="CitationFilter",
    gramplet_title=_("Filter"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Filter",
    name=_("Place Filter"),
    description=_("Gramplet providing a place filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="PlaceFilter",
    gramplet_title=_("Filter"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media Filter",
    name=_("Media Filter"),
    description=_("Gramplet providing a media filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="MediaFilter",
    gramplet_title=_("Filter"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Repository Filter",
    name=_("Repository Filter"),
    description=_("Gramplet providing a repository filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="RepositoryFilter",
    gramplet_title=_("Filter"),
    navtypes=["Repository"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Note Filter",
    name=_("Note Filter"),
    description=_("Gramplet providing a note filter"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="filter.py",
    height=200,
    gramplet="NoteFilter",
    gramplet_title=_("Filter"),
    navtypes=["Note"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Records Gramplet",
    name=_("Records"),
    description=_("Shows some interesting records about people and families"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="recordsgramplet.py",
    authors=["Reinhard Müller"],
    authors_email=["reinhard.mueller@bytewise.at"],
    gramplet="RecordsGramplet",
    height=230,
    expand=True,
    gramplet_title=_("Records"),
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Person To Do",
    name=_("Person To Do"),
    description=_("Gramplet showing the To Do notes for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="PersonToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Event To Do",
    name=_("Event To Do"),
    description=_("Gramplet showing the To Do notes for an event"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="EventToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Event"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Family To Do",
    name=_("Family To Do"),
    description=_("Gramplet showing the To Do notes for a family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="FamilyToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place To Do",
    name=_("Place To Do"),
    description=_("Gramplet showing the To Do notes for a place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="PlaceToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Source To Do",
    name=_("Source To Do"),
    description=_("Gramplet showing the To Do notes for a source"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="SourceToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Source"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Citation To Do",
    name=_("Citation To Do"),
    description=_("Gramplet showing the To Do notes for a citation"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="CitationToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Citation"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Repository To Do",
    name=_("Repository To Do"),
    description=_("Gramplet showing the To Do notes for a repository"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="RepositoryToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Repository"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Media To Do",
    name=_("Media To Do"),
    description=_("Gramplet showing the To Do notes for a media object"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="todo.py",
    height=200,
    gramplet="MediaToDo",
    gramplet_title=_("To Do", "gramplet"),
    navtypes=["Media"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Python Evaluation",
    name="Python Evaluation",
    description="Gramplet allowing the evaluation of python code",
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=UNSTABLE,
    fname="eval.py",
    height=200,
    gramplet="PythonEvaluation",
    gramplet_title="Python Evaluation",
    help_url=DEBUG_HELP,
)

register(
    GRAMPLET,
    id="Uncollected Objects",
    name="Uncollected Objects",
    description="Gramplet showing uncollected objects",
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=UNSTABLE,
    fname="leak.py",
    height=400,
    gramplet="Leak",
    gramplet_title="Uncollected Objects",
    help_url=DEBUG_HELP,
)

register(
    GRAMPLET,
    id="SoundEx Generator",
    name=_("SoundEx"),
    description=_("Gramplet to generate SoundEx codes"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="soundgen.py",
    height=80,
    gramplet="SoundGen",
    gramplet_title=_("SoundEx"),
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Enclosed By",
    name=_("Place Enclosed By"),
    description=_("Gramplet showing the places enclosed by the active place"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="locations.py",
    height=200,
    gramplet="EnclosedBy",
    gramplet_title=_("Enclosed By"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Place Encloses",
    name=_("Place Encloses"),
    description=_("Gramplet showing the places that the active place encloses"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="locations.py",
    height=200,
    gramplet="Encloses",
    gramplet_title=_("Encloses"),
    navtypes=["Place"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Geography coordinates for Person Events",
    name=_("Geography coordinates for Person Events"),
    description=_("Gramplet showing the events for a person"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="coordinates.py",
    height=200,
    gramplet="GeoPersonEvents",
    gramplet_title=_("Events Coordinates"),
    navtypes=["Person"],
    help_url=GRAMPLET_HELP,
)

register(
    GRAMPLET,
    id="Geography coordinates for Family Events",
    name=_("Geography coordinates for Family Events"),
    description=_("Gramplet showing the events for all the family"),
    version="1.0.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="coordinates.py",
    height=200,
    gramplet="GeoFamilyEvents",
    gramplet_title=_("Events Coordinates"),
    navtypes=["Family"],
    help_url=GRAMPLET_HELP,
)
