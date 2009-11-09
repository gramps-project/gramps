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

# $Id$

#------------------------------------------------------------------------
#
# Geoview and HtmlView
#
#------------------------------------------------------------------------

NOWEB  = 0
WEBKIT = 1
MOZIL  = 2

TOOLKIT = NOWEB

try:
    import webkit
    TOOLKIT = WEBKIT
except:
    try:
        import gtkmozembed
        TOOLKIT = MOZILLA
    except:
        pass

#no interfaces present, we do not register these plugins
if not (TOOLKIT == NOWEB):
    register(VIEW, 
    id    = 'geoview',
    name  = _("Geographic View"),
    description =  _("The view showing events on an interactive internet map "
                     "(internet connection needed"),
    version = '1.0',
    status = STABLE,
    fname = 'geoview.py',
    authors = [u"The GRAMPS project"],
    authors_email = ["http://gramps-project.org"],
    category = VIEW_GEO,
    viewclass = 'GeoView',
      )

    register(VIEW, 
    id    = 'htmlview',
    name  = _("Html View"),
    description =  _("A view allowing to see html pages embedded in GRAMPS"),
    version = '1.0',
    status = UNSTABLE,
    fname = 'htmlrenderer.py',
    authors = [u"The GRAMPS project"],
    authors_email = ["http://gramps-project.org"],
    category = VIEW_MISC,
    viewclass = 'HtmlView',
      )
