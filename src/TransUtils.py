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

"""
Provides translation assistance
"""

from gettext import gettext

def sgettext(msgid, sep='|'):
    """
    Strip the context used for resolving translation ambiguities.
    
    The translation of msgid is returned unless the translation is
    not available and the msgid contains the separator. In that case,
    the returned value is the portion of msgid following the last
    separator. Default separator is '|'.

    @param msgid: The string to translated.
    @type msgid: unicode
    @param sep: The separator marking the context.
    @type sep: unicode
    @return: Translation or the original with context stripped.
    @rtype: unicode

    """
    msgval = gettext(msgid)
    if msgval == msgid:
        sep_idx = msgid.rfind(sep)
        msgval = msgid[sep_idx+1:]
    return msgval
