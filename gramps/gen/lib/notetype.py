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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Note types.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


class NoteType(GrampsType):
    UNKNOWN = -1
    CUSTOM = 0
    GENERAL = 1
    RESEARCH = 2
    TRANSCRIPT = 3
    # per object with notes a Type to distinguish the notes
    PERSON = 4
    ATTRIBUTE = 5
    ADDRESS = 6
    ASSOCIATION = 7
    LDS = 8
    FAMILY = 9
    EVENT = 10
    EVENTREF = 11
    SOURCE = 12
    SOURCEREF = 13
    PLACE = 14
    REPO = 15
    REPOREF = 16
    MEDIA = 17
    MEDIAREF = 18
    CHILDREF = 19
    PERSONNAME = 20
    # other common types
    SOURCE_TEXT = 21  # this is used for verbatim source text in SourceRef
    CITATION = 22
    REPORT_TEXT = 23  # this is used for notes used for reports
    # indicate a note is html code
    HTML_CODE = 24
    TODO = 25
    # indicate a note used as link in another note
    LINK = 26
    ANALYSIS = 27

    _CUSTOM = CUSTOM
    _DEFAULT = GENERAL

    _DATAMAPREAL = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (GENERAL, _("General"), "General"),
        (RESEARCH, _("Research"), "Research"),
        (ANALYSIS, _("Analysis"), "Analysis"),
        (TRANSCRIPT, _("Transcript"), "Transcript"),
        (SOURCE_TEXT, _("Source text"), "Source text"),
        (CITATION, _("Citation"), "Citation"),
        (REPORT_TEXT, _("Report"), "Report"),
        (HTML_CODE, _("Html code"), "Html code"),
        (TODO, _("To Do", "notetype"), "To Do"),
        (LINK, _("Link", "notetype"), "Link"),
    ]

    _DATAMAPIGNORE = [
        (PERSON, _("Person Note"), "Person Note"),
        (PERSONNAME, _("Name Note"), "Name Note"),
        (ATTRIBUTE, _("Attribute Note"), "Attribute Note"),
        (ADDRESS, _("Address Note"), "Address Note"),
        (ASSOCIATION, _("Association Note"), "Association Note"),
        (LDS, _("LDS Note"), "LDS Note"),
        (FAMILY, _("Family Note"), "Family Note"),
        (EVENT, _("Event Note"), "Event Note"),
        (EVENTREF, _("Event Reference Note"), "Event Reference Note"),
        (SOURCE, _("Source Note"), "Source Note"),
        (SOURCEREF, _("Source Reference Note"), "Source Reference Note"),
        (PLACE, _("Place Note"), "Place Note"),
        (REPO, _("Repository Note"), "Repository Note"),
        (REPOREF, _("Repository Reference Note"), "Repository Reference Note"),
        (MEDIA, _("Media Note"), "Media Note"),
        (MEDIAREF, _("Media Reference Note"), "Media Reference Note"),
        (CHILDREF, _("Child Reference Note"), "Child Reference Note"),
    ]

    _DATAMAP = _DATAMAPREAL + _DATAMAPIGNORE

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def get_ignore_list(self, exception):
        """
        Return a list of the types to ignore and not include in default lists.

        Exception is a sublist of types that may not be ignored

        :param exception: list of integer values corresponding with types that
                          have to be excluded from the ignore list
        :type exception: list
        :returns: list of integers corresponding with the types to ignore when
                  showing a list of different types
        :rtype: list

        """
        ignlist = [x[0] for x in self._DATAMAPIGNORE]
        if exception:
            for type_ in exception:
                try:
                    del ignlist[ignlist.index(type_)]
                except ValueError:
                    pass
        return ignlist
