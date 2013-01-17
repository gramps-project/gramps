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
from gramps.gen.const import GRAMPS_LOCALE as _gl
_tl = _gl.get_translation()
gettext = _tl.gettext
# When in the 'C' locale, get_translation returns a NULLTranslation
# which doesn't provide sgettext. This traps that case and uses
# gettext instead -- which is fine, because there's no translation
# file involved and it's just going to return the msgid anyeay.
sgettext = None
try:
    _tl.__getattr__(sgettext)
    sgettext = _tl.sgettext
except AttributeError:
    sgettext = _tl.gettext
ngettext = _tl.ngettext
