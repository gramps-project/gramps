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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import const
import constfunc
import config
import locale
import os
import webbrowser

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
}

#first, determine language code, so nl_BE --> wiki /nl
LANG = locale.getlocale()[0]
if not LANG:
    LANG = 'C'
#support environment overrule:
try: 
    if not os.environ['LANGUAGE'] or \
            os.environ['LANGUAGE'].split(':')[0] == LANG:
        pass
    else:
        LANG = os.environ['LANGUAGE'].split(':')[0]
except:
    pass
EXTENSION = ''
try:
    EXTENSION = MANUALS[LANG]
except KeyError:
    pass
try:
    if not EXTENSION :
        EXTENSION = MANUALS[LANG.split('_')[0]]
except KeyError:
    pass

def help(webpage='', section=''):
    """
    Display the specified webpage and section from the Gramps 3.0 wiki.
    """
    if not webpage:
        link = const.URL_WIKISTRING + const.URL_MANUAL_PAGE + EXTENSION
    else:
        link = const.URL_WIKISTRING + webpage + EXTENSION
        if section:
            link = link + '#' + section
    url(link)

def url(link, uistate=None):
    """
    Open the specified URL in a browser.
    """
    from gui.utils import open_file_with_default_application
    if uistate and config.get('htmlview.url-handler'):
        cat_num = uistate.viewmanager.get_category('Web')
        if cat_num is not None:
            page = uistate.viewmanager.goto_page(cat_num, None)
            page.open(link)
            return

    webbrowser.open_new_tab(link)
