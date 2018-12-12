#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import webbrowser
import sys
from urllib.parse import quote
#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import URL_MANUAL_PAGE, URL_WIKISTRING
from gramps.gen.constfunc import is_quartz, mac
from gramps.gen.config import config
from .utils import open_file_with_default_application as run_file

#list of manuals on wiki, map locale code to wiki extension, add language codes
#completely, or first part, so pt_BR if Brazilian portugeze wiki manual, and
#nl for Dutch (nl_BE, nl_NL language code)
MANUALS = {
    'nl' : '/nl',
    'fr' : '/fr',
    'sq' : '/sq',
    'mk' : '/mk',
    'de' : '/de',
    'fi' : '/fi',
    'ru' : '/ru',
    'sk' : '/sk',
}

#first, determine language code, so nl_BE --> wiki /nl
lang = glocale.language[0]
if lang in MANUALS:
    EXTENSION = MANUALS[lang]
else:
    EXTENSION = ''

def display_help(webpage='', section=''):
    """
    Display the specified webpage and section from the Gramps wiki.
    """
    if not webpage:
        link = URL_WIKISTRING + URL_MANUAL_PAGE + EXTENSION
    else:
        link = URL_WIKISTRING + quote(webpage) + EXTENSION
        if section:
            link += '#' + quote(section.replace(' ', '_')).replace('%', '.')
    display_url(link)

def display_url(link, uistate=None):
    """
    Open the specified URL in a browser.
    """
    if (mac() and sys.version_info.major == 3 and sys.version_info.minor < 5):
        import subprocess
        proc = subprocess.call(['/usr/bin/open', link],
                               stderr=subprocess.STDOUT)
    else:
        webbrowser.open_new_tab(link)
