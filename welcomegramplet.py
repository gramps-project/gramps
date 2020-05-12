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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#------------------------------------------------------------------------
#
# Gtk modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import URL_WIKISTRING, URL_MANUAL_PAGE, URL_HOMEPAGE
from gramps.gen.plug import Gramplet
from gramps.gui.widgets.styledtexteditor import StyledTextEditor
from gramps.gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------
def st(text):
    """ Return text as styled text
    """
    return StyledText(text)

def boldst(text):
    """ Return text as bold styled text
    """
    tags = [StyledTextTag(StyledTextTagType.BOLD, True, [(0, len(text))])]
    return StyledText(text, tags)

def linkst(text, url):
    """ Return text as link styled text
    """
    tags = [StyledTextTag(StyledTextTagType.LINK, url, [(0, len(text))])]
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
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        self.texteditor = StyledTextEditor()
        self.texteditor.set_editable(False)
        self.texteditor.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolledwindow.add(self.texteditor)

        self.display_text()

        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def display_text(self):
        """
        Display the welcome text.
        """
        welcome = boldst(_('Intro')) + '\n\n'
        welcome += _(
            'Gramps is a software package designed for genealogical research.'
            ' Although similar to other genealogical programs, Gramps offers '
            'some unique and powerful features.\n\n')
        welcome += boldst(_('Links')) + '\n\n'
        welcome += linkst(_('Home Page'), URL_HOMEPAGE) + '\n'
        welcome += linkst(_('Start with Genealogy and Gramps'),
                          '%(gramps_wiki_url)sStart_with_Genealogy' %
                          {'gramps_wiki_url': URL_WIKISTRING}) + '\n'
        welcome += linkst(_('Gramps online manual'),
                          URL_WIKISTRING + URL_MANUAL_PAGE +
                          _('locale_suffix|')) + '\n'
        welcome += linkst(_('Ask questions on gramps-users mailing list'),
                          '%(gramps_home_url)scontact/' %
                          {'gramps_home_url': URL_HOMEPAGE}) + '\n\n'

        welcome += boldst(_('Who makes Gramps?')) + '\n\n' + _(
            'Gramps is created by genealogists for genealogists, organized in'
            ' the Gramps Project.'
            ' Gramps is an Open Source Software package, which means you are '
            'free to make copies and distribute it to anyone you like. It\'s '
            'developed and maintained by a worldwide team of volunteers whose'
            ' goal is to make Gramps powerful, yet easy to use.\n\n')
        welcome += boldst(_('Getting Started')) + '\n\n' + _(
            'To create a new Family Tree (sometimes called \'database\') select '
            '"Family Trees" from the menu, pick "Manage Family Trees", press '
            '"New" and name your Family Tree. "Load Family Tree" to make the '
			'tree active and ready to accept data by entering your first '
            'family, or importing a family tree. For more details, please '
            'read the information at the links above.\n\n')
        welcome += boldst(_('Enter your first Family')) + '\n\n' + _(
            'You will now want to start entering your first Family and that '
			'starts with the first Person. '
			'You will learn that information can be entered in the various '
			'Views within Gramps.\n\n'
			'Switch to the "Relationships" view and then from the menu "Add" '
			'and "Person". Entering the basic information and saving the record '
			'gives you a starting point. With this first person you can now '
			'add parents, spouse and children, creating families.\n\n'
			'Once started you will be able to provide Sources and Citations '
			'to provide documentation for your entries.\n\n')
        welcome += boldst(_('Importing a Family Tree')) + '\n\n' + _(
            'To import a Family Tree from another program first create '
			'a GEDCOM (or other data) file from the previous program.\n\n'
			'Once you have created a new Gramps database file, use the "Import" '
			'option under the "Family Trees" menu to import the GEDCOM data.\n\n')
        welcome += boldst(_('Dashboard View')) + '\n\n' + _(
            'You are currently reading from the "Dashboard" view, where you can'
            ' add your own gramplets. You can also add gramplets to any view by'
            ' adding a sidebar and/or bottombar, and right-clicking to the'
            ' right of the tab.\n\n'
            'You can click the configuration icon in the toolbar to add'
            ' additional columns, while right-click on the background allows to'
            ' add gramplets. You can also drag the Properties button to'
            ' reposition the gramplet on this page, and detach the gramplet to'
            ' float above Gramps.'
        )

        self.texteditor.set_text(welcome)

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        return True

