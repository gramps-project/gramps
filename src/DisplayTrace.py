#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import cStringIO
import traceback
import sys

#-------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
# DisplayTrace
#
#-------------------------------------------------------------------------
class DisplayTrace:

    def __init__(self):
        data = sys.exc_info()
        msg = cStringIO.StringIO()
        msg.write(_('GRAMPS %s has encountered an internal error.\n'
                    'Please copy the message below and post a bug report '
                    'at http://sourceforge.net/projects/gramps or send an '
                    'email message to gramps-users@lists.sourceforge.net\n\n'
                    'Please include the distribution you are running, along '
                    'with an email address so more information can be '
                    'gathered if necessary\n' % const.version))
                    
        traceback.print_exception(data[0],data[1],data[2],None,msg)

        self.glade = libglade.GladeXML(const.pluginsFile,"plugstat")
        self.top = self.glade.get_widget("plugstat")
        window = self.glade.get_widget("text")
        self.top.set_title(_('Internal Error - GRAMPS'))

        window.show_string(msg.getvalue())
        self.top.run_and_close()


        
