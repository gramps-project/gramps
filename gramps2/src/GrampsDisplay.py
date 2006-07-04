#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2005  Donald N. Allingham
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

def help(target):
    try:
        import gnome
        gnome.help_display('gramps-manual',target)
    except:
        url('http://gramps-project.org/gramps-manual/gramps-manual-en/index.html')
        
def url(target):
    try:
        import gnome
        gnome.url_show(target)
    except:
        run_browser(target)
        

def run_browser(url):
    import os

    search = os.environ['PATH'].split(':')

    for browser in ['firefox','konqueror','epiphany','galeon','mozilla']:
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
                          
    

    
        
