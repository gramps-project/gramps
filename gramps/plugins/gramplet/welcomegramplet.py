# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2020       Dave Scheipers
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

# ------------------------------------------------------------------------
#
# Gtk modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import URL_WIKISTRING, URL_MANUAL_PAGE, URL_HOMEPAGE
from gramps.gen.const import WIKI_EXTRAPLUGINS
from gramps.gui.display import EXTENSION
from gramps.gen.plug import Gramplet
from gramps.gui.widgets.styledtexteditor import StyledTextEditor
from gramps.gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# Functions
#
# ------------------------------------------------------------------------
def st(text):
    """Return text as styled text"""
    return StyledText(text)


def boldst(text):
    """Return text as bold styled text"""
    tags = [StyledTextTag(StyledTextTagType.BOLD, True, [(0, len(text))])]
    return StyledText(text, tags)


def linkst(text, url):
    """Return text as link styled text"""
    tags = [StyledTextTag(StyledTextTagType.LINK, url, [(0, len(text))])]
    return StyledText("  • ") + StyledText(text, tags)


def wiki(page, manual=False):
    """
    Build a link to a wiki page.
    """
    url = URL_WIKISTRING
    if manual:
        url += URL_MANUAL_PAGE
    url += page + EXTENSION
    return url


# ------------------------------------------------------------------------
#
# Gramplet class
#
# ------------------------------------------------------------------------


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
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.texteditor = StyledTextEditor()
        self.texteditor.set_editable(False)
        self.texteditor.set_wrap_mode(Gtk.WrapMode.WORD)
        self.texteditor.set_left_margin(6)
        self.texteditor.set_right_margin(6)
        scrolledwindow.add(self.texteditor)

        self.display_text()

        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def display_text(self):
        """
        Display the welcome text.
        """
        welcome = boldst(_("Intro")) + "\n\n"
        welcome += _(
            "Gramps is a software package designed for genealogical research."
            " Although similar to other genealogical programs, Gramps offers"
            " some unique and powerful features.\n\n"
        )
        welcome += linkst(_("Home Page"), URL_HOMEPAGE) + "\n\n"

        welcome += (
            boldst(_("Who makes Gramps?"))
            + "\n\n"
            + _(
                "Gramps is created by genealogists for genealogists, organized in"
                " the Gramps Project. "
                "Gramps is an Open Source Software package, which means you are"
                " free to make copies and distribute it to anyone you like. It's"
                " developed and maintained by a worldwide team of volunteers whose"
                " goal is to make Gramps powerful, yet easy to use.\n\n"
            )
        )
        welcome += _(
            "There is an active community of users available on the mailing"
            " lists and Discourse forum to share ideas and techniques.\n\n"
        )
        welcome += linkst(_("Gramps online manual"), wiki("", manual=True)) + "\n\n"
        welcome += (
            linkst(
                _("Ask questions on gramps-users mailing list"),
                "%(gramps_home_url)scontact/" % {"gramps_home_url": URL_HOMEPAGE},
            )
            + "\n\n"
        )
        welcome += (
            linkst(_("Gramps Discourse Forum"), "https://gramps.discourse.group/")
            + "\n\n"
        )
        welcome += (
            boldst(_("Getting Started"))
            + "\n\n"
            + _(
                "The first time Gramps is started all of the Views are blank. There"
                " are very few menu options. A Family Tree is needed for any activity"
                " to happen.\n\n"
                "To create a new Family Tree (sometimes called 'database') select"
                ' "Family Trees" from the menu, pick "Manage Family Trees", press'
                ' "New" and name your Family Tree. "Load Family Tree" to make the'
                " tree active and ready to accept data by entering your first"
                " family, or importing a family tree. For more details, please"
                " read the information at the links below.\n\n"
            )
        )
        welcome += (
            linkst(_("Start with Genealogy and Gramps"), wiki("Start_with_Genealogy"))
            + "\n\n"
        )
        welcome += (
            boldst(_("Enter your first Family"))
            + "\n\n"
            + _(
                "You will now want to start entering your first Family and that"
                " starts with the first Person.\n\n"
                'Switch to the "People" view and from the menu clicking "Add" and then'
                ' clicking "Person" (or using the [+] icon) will bring up the window'
                " to enter a person. Entering the basic information and saving the"
                " record gives you a starting point. Select this Person's record and"
                ' now switch to the "Relationships" view.\n\n'
                "With this first person, all of the menu options and icon functions"
                " have become available. Spend some time moving your mouse over the"
                " icons. As your cursor passes over an icon, a message will appear"
                " telling you the icon's function. The same is true for any of the"
                " edit windows. Moving the mouse cursor over an item will tell you"
                " what it will do.\n\n"
                "You can now create families by adding parents, a spouse and children."
                " Once started, you will be able to add Events to People and Families."
                " You can provide Sources and Citations to provide documentation for"
                " your entries.\n\n"
                "As you start using Gramps, you will find that information can be"
                " entered from all the various Views. There are multiple ways of"
                " doing most activities in Gramps. The flexibility allows you to"
                " choose which fits your work style.\n\n"
            )
        )
        welcome += (
            linkst(
                _("Entering and editing data (brief)"),
                wiki("_-_Entering_and_editing_data:_brief", manual=True),
            )
            + "\n\n"
        )
        welcome += (
            boldst(_("Importing a Family Tree"))
            + "\n\n"
            + _(
                "To import a Family Tree from another program first create"
                " a GEDCOM (or other data) file from the previous program.\n\n"
                'Once you have created a new Gramps database file, use the "Import"'
                ' option under the "Family Trees" menu to import the GEDCOM data.\n\n'
            )
        )
        welcome += (
            linkst(
                _("Import from another genealogy program"),
                wiki("Import_from_another_genealogy_program"),
            )
            + "\n\n"
        )
        welcome += (
            boldst(_("Dashboard View"))
            + "\n\n"
            + _(
                'You are currently reading from the "Dashboard" view, where you can'
                " add your own gramplets. You can also add gramplets to any view by"
                " adding a sidebar and/or bottombar, and right-clicking to the"
                " right of the tab.\n\n"
                "You can click the configuration icon in the toolbar to add"
                " additional columns, while right-click on the background allows to"
                " add gramplets. You can also drag the Properties button to"
                " reposition the gramplet on this page, and detach the gramplet to"
                " float above Gramps."
            )
        )
        welcome += "\n\n"
        welcome += (
            linkst(_("Gramps View Categories"), wiki("_-_Categories", manual=True))
            + "\n\n"
        )
        welcome += (
            boldst(_('Addons and "Gramplets"'))
            + "\n\n"
            + _(
                'There are many Addons or "Gramplets" that are available to assist you'
                " in data entry and visualizing your family tree. Many of these tools"
                " are already available to you. Many more are available to download"
                " and install.\n\n"
            )
        )
        welcome += linkst(_('Addons and "Gramplets"'), wiki(WIKI_EXTRAPLUGINS)) + "\n\n"
        welcome += (
            boldst(_("Example Database"))
            + "\n\n"
            + _(
                "Want to see Gramps in use. Create and Import the Example database.\n\n"
                "Create a new Family Tree as described above. Suggest that you name"
                " the Family Tree “EXAMPLE”.\n\n"
                "Import the Gramps file example.gramps.\n\n"
                "Follow the instructions for the location of the file stored with"
                " the Gramps program.\n\n"
            )
        )
        welcome += linkst(_("Example.gramps"), wiki("Example.gramps")) + "\n\n"

        self.texteditor.set_text(welcome)

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        return True
