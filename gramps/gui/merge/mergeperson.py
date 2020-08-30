#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010       Jakim Friant
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

"""
Provide merge capabilities for persons.
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.plug.report import utils
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.const import URL_MANUAL_SECT3
from ..display import display_help
from gramps.gen.datehandler import get_date
from gramps.gen.errors import MergeError
from ..dialog import ErrorDialog, WarningDialog
from ..managedwindow import ManagedWindow
from gramps.gen.merge import MergePersonQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Merge_People", "manual")
_GLADE_FILE = "mergeperson.glade"

# translators: needed for French, ignore otherwise
KEYVAL = _("%(key)s:\t%(value)s")

sex = ( _("female"), _("male"), _("unknown") )

def name_of(person):
    """Return string with name and ID of a person."""
    if not person:
        return ""
    return "%s [%s]" % (name_displayer.display(person), person.get_gramps_id())

#-------------------------------------------------------------------------
#
# MergePerson
#
#-------------------------------------------------------------------------
class MergePerson(ManagedWindow):
    """
    Displays a dialog box that allows the persons to be combined into one.
    """
    def __init__(self, dbstate, uistate, track, handle1, handle2,
                 cb_update=None, expand_context_info=True):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.database = dbstate.db
        self.pr1 = self.database.get_person_from_handle(handle1)
        self.pr2 = self.database.get_person_from_handle(handle2)
        self.update = cb_update

        self.define_glade('mergeperson', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget("person_title"),
                        _("Merge People"))
        self.setup_configs('interface.merge-person', 700, 400)

        # Detailed selection widgets
        name1 = name_displayer.display_name(self.pr1.get_primary_name())
        name2 = name_displayer.display_name(self.pr2.get_primary_name())
        entry1 = self.get_widget("name1")
        entry2 = self.get_widget("name2")
        entry1.set_text(name1)
        entry2.set_text(name2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('name1', 'name2', 'name_btn1', 'name_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("gender1")
        entry2 = self.get_widget("gender2")
        entry1.set_text(sex[self.pr1.get_gender()])
        entry2.set_text(sex[self.pr2.get_gender()])
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('gender1', 'gender2', 'gender_btn1',
                    'gender_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.pr1.get_gramps_id()
        gramps2 = self.pr2.get_gramps_id()
        entry1 = self.get_widget("gramps1")
        entry2 = self.get_widget("gramps2")
        entry1.set_text(gramps1)
        entry2.set_text(gramps2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('gramps1', 'gramps2', 'gramps_btn1',
                    'gramps_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        # Main window widgets that determine which handle survives
        rbutton1 = self.get_widget("handle_btn1")
        rbutton_label1 = self.get_widget("label_handle_btn1")
        rbutton_label2 = self.get_widget("label_handle_btn2")
        rbutton_label1.set_label(name1 + " [" + gramps1 + "]")
        rbutton_label2.set_label(name2 + " [" + gramps2 + "]")
        rbutton1.connect("toggled", self.on_handle1_toggled)
        expander2 = self.get_widget("expander2")
        self.expander_handler = expander2.connect("notify::expanded",
                                                  self.cb_expander2_activated)
        expander2.set_expanded(expand_context_info)

        self.connect_button("person_help", self.cb_help)
        self.connect_button("person_ok", self.cb_merge)
        self.connect_button("person_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """Preferred person changes"""
        if obj.get_active():
            self.get_widget("name_btn1").set_active(True)
            self.get_widget("gender_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("name_btn2").set_active(True)
            self.get_widget("gender_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_expander2_activated(self, obj, param_spec):
        """Context Information expander is activated"""
        if obj.get_expanded():
            text1 = self.get_widget('text1')
            text2 = self.get_widget('text2')
            self.display(text1.get_buffer(), self.pr1)
            self.display(text2.get_buffer(), self.pr2)
            obj.disconnect(self.expander_handler)

    def add(self, tobj, tag, text):
        """Add text text to text buffer tobj with formatting tag."""
        text += "\n"
        tobj.insert_with_tags(tobj.get_end_iter(), text, tag)

    def display(self, tobj, person):
        """Fill text buffer tobj with detailed info on person person."""
        normal = tobj.create_tag()
        normal.set_property('indent', 10)
        normal.set_property('pixels-above-lines', 1)
        normal.set_property('pixels-below-lines', 1)
        indent = tobj.create_tag()
        indent.set_property('indent', 30)
        indent.set_property('pixels-above-lines', 1)
        indent.set_property('pixels-below-lines', 1)
        title = tobj.create_tag()
        title.set_property('weight', Pango.Weight.BOLD)
        title.set_property('scale', 1.2)
        self.add(tobj, title, name_displayer.display(person))
        self.add(tobj, normal, KEYVAL % {'key': _('ID'),
                                         'value': person.get_gramps_id()})
        self.add(tobj, normal, KEYVAL % {'key': _('Gender'),
                                         'value': sex[person.get_gender()]})
        bref = person.get_birth_ref()
        if bref:
            self.add(tobj, normal,
                     KEYVAL % {'key': _('Birth'),
                               'value': self.get_event_info(bref.ref)})
        dref = person.get_death_ref()
        if dref:
            self.add(tobj, normal,
                     KEYVAL % {'key': _('Death'),
                               'value': self.get_event_info(dref.ref)})

        nlist = person.get_alternate_names()
        if len(nlist) > 0:
            self.add(tobj, title, _("Alternate Names"))
            for name in nlist:
                self.add(tobj, normal,
                         name_displayer.display_name(name))

        elist = person.get_event_ref_list()
        if len(elist) > 0:
            self.add(tobj, title, _("Events"))
            for event_ref in person.get_event_ref_list():
                event_handle = event_ref.ref
                role = event_ref.get_role()
                name = str(
                    self.database.get_event_from_handle(event_handle).get_type())
                ev_info = self.get_event_info(event_handle)
                if role.is_primary():
                    self.add(tobj, normal,
                             KEYVAL % {'key': name, 'value': ev_info})
                else:
                    self.add(tobj, normal, # translators: needed for French
                             "%(name)s (%(role)s):\t%(info)s"
                                 % {'name': name, 'role': role,
                                    'info': ev_info})
        plist = person.get_parent_family_handle_list()

        if len(plist) > 0:
            self.add(tobj, title, _("Parents"))
            for fid in person.get_parent_family_handle_list():
                (fname, mname, gid) = self.get_parent_info(fid)
                self.add(tobj, normal,
                         KEYVAL % {'key': _('Family ID'), 'value': gid})
                if fname:
                    self.add(tobj, indent,
                             KEYVAL % {'key': _('Father'), 'value': fname})
                if mname:
                    self.add(tobj, indent,
                             KEYVAL % {'key': _('Mother'), 'value': mname})
        else:
            self.add(tobj, normal, _("No parents found"))

        self.add(tobj, title, _("Spouses"))
        slist = person.get_family_handle_list()
        if len(slist) > 0:
            for fid in slist:
                (fname, mname, pid) = self.get_parent_info(fid)
                family = self.database.get_family_from_handle(fid)
                self.add(tobj, normal,
                         KEYVAL % {'key': _('Family ID'), 'value': pid})
                spouse_id = utils.find_spouse(person, family)
                if spouse_id:
                    spouse = self.database.get_person_from_handle(spouse_id)
                    self.add(tobj, indent, KEYVAL % {'key': _('Spouse'),
                                                     'value': name_of(spouse)})
                relstr = str(family.get_relationship())
                self.add(tobj, indent,
                         KEYVAL % {'key': _('Type'), 'value': relstr})
                event = utils.find_marriage(self.database, family)
                if event:
                    m_info = self.get_event_info(event.get_handle())
                    self.add(tobj, indent,
                             KEYVAL % {'key': _('Marriage'), 'value': m_info})
                for child_ref in family.get_child_ref_list():
                    child = self.database.get_person_from_handle(child_ref.ref)
                    self.add(tobj, indent, KEYVAL % {'key': _('Child'),
                                                     'value': name_of(child)})
        else:
            self.add(tobj, normal, _("No spouses or children found"))

        alist = person.get_address_list()
        if len(alist) > 0:
            self.add(tobj, title, _("Addresses"))
            for addr in alist:
                # TODO for Arabic, should the next line's comma be translated?
                location = ", ".join([addr.get_street(), addr.get_city(),
                                     addr.get_state(), addr.get_country(),
                                     addr.get_postal_code(), addr.get_phone()])
                self.add(tobj, normal, location.strip())

    def get_parent_info(self, fid):
        """Return tuple of father name, mother name and family ID"""
        family = self.database.get_family_from_handle(fid)
        father_id = family.get_father_handle()
        mother_id = family.get_mother_handle()
        if father_id:
            father = self.database.get_person_from_handle(father_id)
            fname = name_of(father)
        else:
            fname = ""
        if mother_id:
            mother = self.database.get_person_from_handle(mother_id)
            mname = name_of(mother)
        else:
            mname = ""
        return (fname, mname, family.get_gramps_id())

    def get_event_info(self, handle):
        """Return date and place of an event as string."""
        date = ""
        place = ""
        if handle:
            event = self.database.get_event_from_handle(handle)
            date = get_date(event)
            place = place_displayer.display_event(self.database, event)
            if date:
                return ("%s, %s" % (date, place)) if place else date
            else:
                return place or ""
        else:
            return ""

    def cb_help(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the persons when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.pr1
            titanic = self.pr2
        else:
            phoenix = self.pr2
            titanic = self.pr1

        if self.get_widget("name_btn1").get_active() ^ use_handle1:
            swapname = phoenix.get_primary_name()
            phoenix.set_primary_name(titanic.get_primary_name())
            titanic.set_primary_name(swapname)
        if self.get_widget("gender_btn1").get_active() ^ use_handle1:
            phoenix.set_gender(titanic.get_gender())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            swapid = phoenix.get_gramps_id()
            phoenix.set_gramps_id(titanic.get_gramps_id())
            titanic.set_gramps_id(swapid)

        try:
            query = MergePersonQuery(self.database, phoenix, titanic)
            family_merge_ok = query.execute()
            if not family_merge_ok:
                WarningDialog(
                    _("Warning"),
                    _("The persons have been merged.\nHowever, the families "
                      "for this merge were too complex to automatically "
                      "handle.  We recommend that you go to Relationships "
                      "view and see if additional manual merging of families "
                      "is necessary."), parent=self.window)
            # Add the selected handle to history so that when merge is complete,
            # phoenix is the selected row.
            self.uistate.set_active(phoenix.get_handle(), 'Person')
        except MergeError as err:
            ErrorDialog(_("Cannot merge people"), str(err),
                        parent=self.window)
        self.uistate.set_busy_cursor(False)
        self.close()
        if self.update:
            self.update()
