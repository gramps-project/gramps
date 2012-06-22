# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

# $Id$

#------------------------------------------------------------------------
#
# modules
#
#------------------------------------------------------------------------

import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from gui.widgets.styledtexteditor import StyledTextEditor
from gui.widgets import SimpleButton
from gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gen.ggettext import sgettext as _

#------------------------------------------------------------------------
#
# functions
#
#------------------------------------------------------------------------

def st(text):
    """ Return text as styled text
    """
    return StyledText(text)

def boldst(text):
    """ Return text as bold styled text
    """
    tags = [StyledTextTag(StyledTextTagType.BOLD, True,
                            [(0, len(text))])]
    return StyledText(text, tags)

def linkst(text, url):
    """ Return text as link styled text
    """
    tags = [StyledTextTag(StyledTextTagType.LINK, url,
                            [(0, len(text))])]
    return StyledText(text, tags)

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------

class WelcomeGramplet(Gramplet):
    """
    Displays a welcome note to the user.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = gtk.VBox(False)
        
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.texteditor = StyledTextEditor()
        self.texteditor.set_editable(False)
        self.texteditor.set_wrap_mode(gtk.WRAP_WORD)
        scrolledwindow.add(self.texteditor)

        self.set_text()
        
        top.pack_start(scrolledwindow, True, True)
        top.show_all()
        return top

    def set_text(self):
        """
        Display the welcome text.
        """
        welcome = boldst(_('Intro')) + '\n\n'
        welcome += _(
        'Gramps is a software package designed for genealogical research.'
        ' Although similar to other genealogical programs, Gramps offers '
        'some unique and powerful features.\n\n')
        welcome += boldst(_('Links')) + '\n\n'
        welcome += linkst(_('Home Page'), _('http://gramps-project.org/')) + '\n'
        welcome += linkst(_('Start with Genealogy and Gramps'), 
            _('http://www.gramps-project.org/wiki/index.php?title=Start_with_Genealogy')) + '\n'
        welcome += linkst(_('Gramps online manual'), 
            _('http://www.gramps-project.org/wiki/index.php?title=Gramps_3.3_Wiki_Manual')) + '\n'
        welcome += linkst(_('Ask questions on gramps-users mailing list'),
             _('http://gramps-project.org/contact/')) + '\n\n'
        
        welcome += boldst(_('Who makes Gramps?')) + '\n\n' + _(
        'Gramps is created by genealogists for genealogists, organized in the'
        ' Gramps Project.'
        ' Gramps is an Open Source Software package, which means you are '
        'free to make copies and distribute it to anyone you like. It\'s '
        'developed and maintained by a worldwide team of volunteers whose'
        ' goal is to make Gramps powerful, yet easy to use.\n\n')
        welcome += boldst(_('Getting Started')) + '\n\n' + _(
        'The first thing you must do is to create a new Family Tree. To '
        'create a new Family Tree (sometimes called \'database\') select '
        '"Family Trees" from the menu, pick "Manage Family Trees", press '
        '"New" and name your family tree. For more details, please read the '
        'information at the links above\n\n')
        welcome += boldst(_('Gramplet View')) + '\n\n' + _(
        'You are currently reading from the "Gramplets" page, where you can'
        ' add your own gramplets. You can also add Gramplets to any view by'
        ' adding a sidebar and/or bottombar, and right-clicking to the right'
        ' of the tab.\n\n'
        'You can click the configuration icon in the toolbar to add additional'
        ' columns, while right-click on the background allows to add gramplets.'
        ' You can also drag the Properties button to reposition the gramplet '
        ' on this page, and detach the gramplet to float above Gramps.'
        )

        self.texteditor.set_text(welcome)

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        return True
    
