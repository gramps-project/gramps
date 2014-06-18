# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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

MODULE_VERSION="4.2" 

#------------------------------------------------------------------------
#
# Geoview and HtmlView
#
#------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi import Repository

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("HtmlRenderer")

NOWEB  = 0
WEBKIT = 1
MOZILLA  = 2

TOOLKIT = NOWEB


# Attempting to import webkit gives an error dialog if webkit is not
# available so test first and log just a warning to the console instead.
repository = Repository.get_default()
if repository.enumerate_versions("WebKit"):
    try:
        from gi.repository import WebKit
        TOOLKIT = WEBKIT
    except:
        pass

from gramps.gen.config import config
if TOOLKIT == NOWEB and not config.get('interface.ignore-webkit'):
    from gramps.gen.constfunc import has_display, mac, win
    if win() or mac(): # WebKit is not put into either Windows or Mac bundles
        config.set('interface.ignore-webkit', True)
    if has_display() and not config.get('interface.ignore-webkit'):
        from gramps.gui.dialog import MessageHideDialog
        title = _("Webkit module not loaded.")
        msg = _("Webkit module not loaded. "
                "Embedded web page viewing will not be available. "
                "Use your package manager to install gir1.2-webkit-3.0")
        MessageHideDialog(title, msg, 'interface.ignore-webkit')

#no interfaces present, we do not register these plugins
if not (TOOLKIT == NOWEB):
    register(VIEW, 
    id    = 'htmlview',
    name  = _("Html View"),
    description =  _("A view showing html pages embedded in Gramps"),
    version = '1.0',
    gramps_target_version = MODULE_VERSION,
    status = STABLE,
    fname = 'htmlrenderer.py',
    authors = ["The Gramps project"],
    authors_email = ["http://gramps-project.org"],
    category = ("Web", _("Web")),
    viewclass = 'HtmlView',
      )
