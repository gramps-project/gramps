#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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

from .selectorexceptions import SelectorException


def SelectorFactory(classname):
    if classname == "Person":
        from .selectperson import SelectPerson

        cls = SelectPerson
    elif classname == "Family":
        from .selectfamily import SelectFamily

        cls = SelectFamily
    elif classname == "Event":
        from .selectevent import SelectEvent

        cls = SelectEvent
    elif classname == "Place":
        from .selectplace import SelectPlace

        cls = SelectPlace
    elif classname == "Source":
        from .selectsource import SelectSource

        cls = SelectSource
    elif classname == "Citation":
        from .selectcitation import SelectCitation

        cls = SelectCitation
    elif classname == "Media":
        from .selectobject import SelectObject

        cls = SelectObject
    elif classname == "Repository":
        from .selectrepository import SelectRepository

        cls = SelectRepository
    elif classname == "Note":
        from .selectnote import SelectNote

        cls = SelectNote
    else:
        raise SelectorException(
            "Attempt to create unknown "
            "selector class: "
            "classname = %s" % (str(classname),)
        )

    return cls
