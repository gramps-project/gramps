#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Michiel D. Nauta
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

"""
Provide merge capabilities for families.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.db import DbTxn
from gen.ggettext import sgettext as _
from gen.display.name import displayer as name_displayer
import const
import GrampsDisplay
from QuestionDialog import ErrorDialog
from Errors import MergeError
import ManagedWindow
from Merge.mergeperson import MergePersonQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Entering_and_Editing_Data:_Detailed_-_part_3' % \
    const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Merge_Families')
_GLADE_FILE = 'mergefamily.glade'

#-------------------------------------------------------------------------
#
# Merge Families
#
#-------------------------------------------------------------------------
class MergeFamilies(ManagedWindow.ManagedWindow):
    """
    Merges two families into a single family. Displays a dialog box that allows
    the families to be combined into one.
    """
    def __init__(self, dbstate, uistate, handle1, handle2):
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.database = dbstate.db
        self.fy1 = self.database.get_family_from_handle(handle1)
        self.fy2 = self.database.get_family_from_handle(handle2)

        self.define_glade('mergefamily', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget("family_title"),
                        _("Merge Families"))

        # Detailed selection widgets
        father1 = self.fy1.get_father_handle()
        father2 = self.fy2.get_father_handle()
        father1 = self.database.get_person_from_handle(father1)
        father2 = self.database.get_person_from_handle(father2)
        father_id1 = father1.get_gramps_id() if father1 else ""
        father_id2 = father2.get_gramps_id() if father2 else ""
        father1 = name_displayer.display(father1) if father1 else ""
        father2 = name_displayer.display(father2) if father2 else ""
        entry1 = self.get_widget("father1")
        entry2 = self.get_widget("father2")
        entry1.set_text("%s [%s]" % (father1, father_id1))
        entry2.set_text("%s [%s]" % (father2, father_id2))
        deactivate = False
        if father_id1 == "" and father_id2 == "":
            deactivate = True
        elif father_id2 == "":
            self.get_widget("father_btn1").set_active(True)
            deactivate = True
        elif father_id1 == "":
            self.get_widget("father_btn2").set_active(True)
            deactivate = True
        elif entry1.get_text() == entry2.get_text():
            deactivate = True
        if deactivate:
            for widget_name in ('father1', 'father2', 'father_btn1',
                    'father_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        mother1 = self.fy1.get_mother_handle()
        mother2 = self.fy2.get_mother_handle()
        mother1 = self.database.get_person_from_handle(mother1)
        mother2 = self.database.get_person_from_handle(mother2)
        mother_id1 = mother1.get_gramps_id() if mother1 else ""
        mother_id2 = mother2.get_gramps_id() if mother2 else ""
        mother1 = name_displayer.display(mother1) if mother1 else ""
        mother2 = name_displayer.display(mother2) if mother2 else ""
        entry1 = self.get_widget("mother1")
        entry2 = self.get_widget("mother2")
        entry1.set_text("%s [%s]" % (mother1, mother_id1))
        entry2.set_text("%s [%s]" % (mother2, mother_id2))
        deactivate = False
        if mother_id1 == "" and mother_id2 == "":
            deactivate = True
        elif mother_id1 == "":
            self.get_widget("mother_btn2").set_active(True)
            deactivate = True
        elif mother_id2 == "":
            self.get_widget("mother_btn1").set_active(True)
            deactivate = True
        elif entry1.get_text() == entry2.get_text():
            deactivate = True
        if deactivate:
            for widget_name in ('mother1', 'mother2', 'mother_btn1',
                    'mother_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("rel1")
        entry2 = self.get_widget("rel2")
        entry1.set_text(str(self.fy1.get_relationship()))
        entry2.set_text(str(self.fy2.get_relationship()))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('rel1', 'rel2', 'rel_btn1', 'rel_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.fy1.get_gramps_id()
        gramps2 = self.fy2.get_gramps_id()
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
        rbutton_label1.set_label("%s and %s [%s]" %(father1, mother1, gramps1))
        rbutton_label2.set_label("%s and %s [%s]" %(father2, mother2, gramps2))
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("family_help", self.cb_help)
        self.connect_button("family_ok", self.cb_merge)
        self.connect_button("family_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """Preferred family changes"""
        if obj.get_active():
            father1_text = self.get_widget("father1").get_text()
            if (father1_text != " []" or 
                self.get_widget("father2").get_text() == " []"):
                    self.get_widget("father_btn1").set_active(True)
            mother1_text = self.get_widget("mother1").get_text()
            if (mother1_text != " []" or
                self.get_widget("mother2").get_text() == " []"):
                    self.get_widget("mother_btn1").set_active(True)
            self.get_widget("rel_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            father2_text = self.get_widget("father2").get_text()
            if (father2_text != " []" or
                self.get_widget("father1").get_text() == " []"):
                    self.get_widget("father_btn2").set_active(True)
            mother2_text = self.get_widget("mother2").get_text()
            if (mother2_text != " []" or
                self.get_widget("mother1").get_text() == " []"):
                    self.get_widget("mother_btn2").set_active(True)
            self.get_widget("rel_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        GrampsDisplay.help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the families when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.fy1
            titanic = self.fy2
        else:
            phoenix = self.fy2
            titanic = self.fy1
            # Add second handle to history so that when merge is complete, 
            # phoenix is the selected row.
            self.uistate.viewmanager.active_page.get_history().push(
                    phoenix.get_handle())

        phoenix_fh = phoenix.get_father_handle()
        phoenix_mh = phoenix.get_mother_handle()

        if self.get_widget("father_btn1").get_active() ^ use_handle1:
            phoenix_fh = titanic.get_father_handle()
        if self.get_widget("mother_btn1").get_active() ^ use_handle1:
            phoenix_mh = titanic.get_mother_handle()
        if self.get_widget("rel_btn1").get_active() ^ use_handle1:
            phoenix.set_relationship(titanic.get_relationship())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        try:
            query = MergeFamilyQuery(self.database, phoenix, titanic,
                                     phoenix_fh, phoenix_mh)
            query.execute()
        except MergeError, err:
            ErrorDialog( _("Cannot merge people"), str(err))
        self.uistate.set_busy_cursor(False)
        self.close()

class MergeFamilyQuery(object):
    """
    Create database query to merge two families.
    """
    def __init__(self, database, phoenix, titanic, phoenix_fh=None,
                 phoenix_mh=None):
        self.database = database
        self.phoenix = phoenix
        self.titanic = titanic
        if phoenix_fh is None:
            self.phoenix_fh = self.phoenix.get_father_handle()
        else:
            self.phoenix_fh = phoenix_fh
        if phoenix_mh is None:
            self.phoenix_mh = self.phoenix.get_mother_handle()
        else:
            self.phoenix_mh = phoenix_mh

        if self.phoenix.get_father_handle() == self.phoenix_fh:
            self.titanic_fh = self.titanic.get_father_handle()
            self.father_swapped = False
        else:
            assert self.phoenix_fh == self.titanic.get_father_handle()
            self.titanic_fh = self.phoenix.get_father_handle()
            self.father_swapped = True
        if self.phoenix.get_mother_handle() == self.phoenix_mh:
            self.titanic_mh = self.titanic.get_mother_handle()
            self.mother_swapped = False
        else:
            assert self.phoenix_mh == self.titanic.get_mother_handle()
            self.titanic_mh = self.phoenix.get_mother_handle()
            self.mother_swapped = True

    def merge_person(self, phoenix_person, titanic_person, parent, trans):
        """
        Merge two persons even if they are None; no families are merged!
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        if parent == 'father':
            swapped = self.father_swapped
            family_add_person_handle = (
                (self.phoenix if swapped else self.titanic).set_father_handle)
        elif parent == 'mother':
            swapped = self.mother_swapped
            family_add_person_handle = (
                (self.phoenix if swapped else self.titanic).set_mother_handle)
        else:
            raise ValueError(_("A parent should be a father or mother."))

        if phoenix_person is None:
            if titanic_person is not None:
                raise MergeError("""When merging people where one person """
                    """doesn't exist, that "person" must be the person that """
                    """will be deleted from the database.""")
            return
        elif titanic_person is None:
            if swapped:
                if any(childref.get_reference_handle() == phoenix_person.get_handle()
                        for childref in self.phoenix.get_child_ref_list()):

                    raise MergeError(_("A parent and child cannot be merged. "
                        "To merge these people, you must first break the "
                        "relationship between them."))

                phoenix_person.add_family_handle(new_handle)
                family_add_person_handle(phoenix_person.get_handle())
                self.database.commit_family(self.phoenix, trans)
            else:
                if any(childref.get_reference_handle() == phoenix_person.get_handle()
                        for childref in self.titanic.get_child_ref_list()):

                    raise MergeError(_("A parent and child cannot be merged. "
                        "To merge these people, you must first break the "
                        "relationship between them."))

                phoenix_person.add_family_handle(old_handle)
                family_add_person_handle(phoenix_person.get_handle())
                self.database.commit_family(self.titanic, trans)

            self.database.commit_person(phoenix_person, trans)
        else:
            query = MergePersonQuery(self.database, phoenix_person,
                                     titanic_person)
            query.execute(family_merger=False, trans=trans)

    def execute(self):
        """
        Merges two families into a single family.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        with DbTxn(_('Merge Family'), self.database) as trans:

            phoenix_father = self.database.get_person_from_handle(self.phoenix_fh)
            titanic_father = self.database.get_person_from_handle(self.titanic_fh)
            self.merge_person(phoenix_father, titanic_father, 'father', trans)

            phoenix_mother = self.database.get_person_from_handle(self.phoenix_mh)
            titanic_mother = self.database.get_person_from_handle(self.titanic_mh)
            self.phoenix = self.database.get_family_from_handle(new_handle)
            self.titanic = self.database.get_family_from_handle(old_handle)
            self.merge_person(phoenix_mother, titanic_mother, 'mother', trans)

            phoenix_father = self.database.get_person_from_handle(self.phoenix_fh)
            phoenix_mother = self.database.get_person_from_handle(self.phoenix_mh)
            self.phoenix = self.database.get_family_from_handle(new_handle)
            self.titanic = self.database.get_family_from_handle(old_handle)
            self.phoenix.merge(self.titanic)
            self.database.commit_family(self.phoenix, trans)
            for childref in self.titanic.get_child_ref_list():
                child = self.database.get_person_from_handle(
                        childref.get_reference_handle())
                if new_handle in child.parent_family_list:
                    child.remove_handle_references('Family', [old_handle])
                else:
                    child.replace_handle_reference('Family', old_handle,
                                                   new_handle)
                self.database.commit_person(child, trans)
            if phoenix_father:
                phoenix_father.remove_family_handle(old_handle)
                self.database.commit_person(phoenix_father, trans)
            if phoenix_mother:
                phoenix_mother.remove_family_handle(old_handle)
                self.database.commit_person(phoenix_mother, trans)
            # replace the family in lds ordinances
            for (dummy, person_handle) in self.database.find_backlink_handles(
                    old_handle, ['Person']):
                person = self.database.get_person_from_handle(person_handle)
                person.replace_handle_reference('Family', old_handle,new_handle)
                self.database.commit_person(person, trans)
            self.database.remove_family(old_handle, trans)
