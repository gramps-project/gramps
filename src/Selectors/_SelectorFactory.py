#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

from _SelectorExceptions import SelectorException

def selector_factory(classname):
    if classname == 'Person':
        from _SelectPerson import SelectPerson
        cls = SelectPerson
    elif classname == 'Family':
        from _SelectFamily import SelectFamily
        cls = SelectFamily
    elif classname == 'Event':
        from _SelectEvent import SelectEvent
        cls = SelectEvent
    elif classname == 'Place':
        from _SelectPlace import SelectPlace
        cls = SelectPlace
    elif classname == 'Source':
        from _SelectSource import SelectSource
        cls = SelectSource
    elif classname == 'MediaObject':
        from _SelectObject import SelectObject
        cls = SelectObject
    elif classname == 'Repository':
        from _SelectRepository import SelectRepository
        cls = SelectRepository
    else:
        raise SelectorException("Attempt to create unknown "
                                "selector class: "
                                "classname = %s" % (str(classname),))

    return cls
