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
import locale
import os

#list of manuals on wiki, map locale code to wiki extension, add language codes
#completely, or first part, so pt_BR if Brazilian portugeze wiki manual, and 
#nl for Dutch (nl_BE, nl_NL language code)
MANUALS = {
    'nl' : '/nl',
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

def help(target, webpage='', section=''):
    """
    Display the specified target in a help window. If this fails,
    open the manual on the web site.
    """
    #try:
    #    import gnome
    #    gnome.help_display('gramps',target)
    #except:
    #    url(const.URL_MANUAL+'en/')
    
    # 3.0 Beta, direct to the wiki 3.0 Manual

    if not webpage:
        link = const.URL_WIKISTRING + const.URL_MANUAL_PAGE + EXTENSION
    else:
        link = const.URL_WIKISTRING + webpage + EXTENSION
        if section:
            link = link + '#' + section
    url(link)
        
def url(link):
    """
    Open the specified URL in a browser. 
    """
    if not run_file(link):
        run_browser(link)

def run_file(file):
    """
    Open a file or url with the default application. This should work
    on GNOME, KDE, XFCE, ... as we use a freedesktop application
    """
    import os
    
    search = os.environ['PATH'].split(':')
    
    xdgopen = 'xdg-open'
    for path in search:
        prog = os.path.join(path, xdgopen)
        if os.path.isfile(prog):
            os.spawnvpe(os.P_NOWAIT, prog, [prog, file], os.environ)
            return True
    
    return False

def run_browser(url):
    """
    Attempt of find a browswer, and launch with the browser with the
    specified URL
    Use run_file first!
    """
    try:
        import webbrowser
        webbrowser.open_new_tab(url)
    except ImportError:
        import os

        search = os.environ['PATH'].split(':')

        for browser in ['firefox', 'konqueror', 'epiphany',
                        'galeon', 'mozilla']:
            for path in search:
                prog = os.path.join(path,browser)
                if os.path.isfile(prog):
                    os.spawnvpe(os.P_NOWAIT, prog, [prog, url], os.environ)
                    return

        # If we did not find a browser in the path, try this
        try:
            os.startfile(url)
        except:
            pass
