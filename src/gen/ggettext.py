#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2010  Brian G. Matherly
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
This module ("Gramps Gettext") is an extension to the Python gettext module.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext as pgettext


def gettext(msgid):
    """
    Obtain translation of gettext, return a unicode object
    :param msgid: The string to translated.
    :type msgid: unicode
    :returns: Translation or the original.
    :rtype: unicode
    """
    return unicode(pgettext.gettext(msgid))

def ngettext(singular, plural, n):
    """
    The translation of singular/plural is returned unless the translation is
    not available and the singular contains the separator. In that case,
    the returned value is the singular.

    :param singular: The singular form of the string to be translated.
                      may contain a context seperator
    :type singular: unicode
    :param plural: The plural form of the string to be translated.
    :type plural: unicode
    :param n: the amount for which to decide the translation
    :type n: int
    :returns: Translation or the original.
    :rtype: unicode
    """
    return unicode(pgettext.ngettext(singular, plural, n))
    
def sgettext(msgid, sep='|'):
    """
    Strip the context used for resolving translation ambiguities.
    
    The translation of msgid is returned unless the translation is
    not available and the msgid contains the separator. In that case,
    the returned value is the portion of msgid following the last
    separator. Default separator is '|'.

    :param msgid: The string to translated.
    :type msgid: unicode
    :param sep: The separator marking the context.
    :type sep: unicode
    :returns: Translation or the original with context stripped.
    :rtype: unicode

    """
    msgval = pgettext.gettext(msgid)
    if msgval == msgid:
        sep_idx = msgid.rfind(sep)
        msgval = msgid[sep_idx+1:]
    return unicode(msgval)