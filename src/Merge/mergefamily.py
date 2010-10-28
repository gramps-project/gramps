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
        self.dbstate = dbstate
        database = dbstate.db
        self.fy1 = database.get_family_from_handle(handle1)
        self.fy2 = database.get_family_from_handle(handle2)

        self.define_glade('mergefamily', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget("family_title"),
                        _("Merge Families"))

        # Detailed selection widgets
        father1 = self.fy1.get_father_handle()
        father2 = self.fy2.get_father_handle()
        father1 = database.get_person_from_handle(father1)
        father2 = database.get_person_from_handle(father2)
        father_id1 = father1.get_gramps_id()
        father_id2 = father2.get_gramps_id()
        father1 = name_displayer.display(father1) if father1 else ""
        father2 = name_displayer.display(father2) if father2 else ""
        entry1 = self.get_widget("father1")
        entry2 = self.get_widget("father2")
        entry1.set_text("%s [%s]" % (father1, father_id1))
        entry2.set_text("%s [%s]" % (father2, father_id2))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('father1', 'father2', 'father_btn1',
                    'father_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        mother1 = self.fy1.get_mother_handle()
        mother2 = self.fy2.get_mother_handle()
        mother1 = database.get_person_from_handle(mother1)
        mother2 = database.get_person_from_handle(mother2)
        mother_id1 = mother1.get_gramps_id()
        mother_id2 = mother2.get_gramps_id()
        mother1 = name_displayer.display(mother1) if mother1 else ""
        mother2 = name_displayer.display(mother2) if mother2 else ""
        entry1 = self.get_widget("mother1")
        entry2 = self.get_widget("mother2")
        entry1.set_text("%s [%s]" % (mother1, mother_id1))
        entry2.set_text("%s [%s]" % (mother2, mother_id2))
        if entry1.get_text() == entry2.get_text():
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
            self.get_widget("father_btn1").set_active(True)
            self.get_widget("mother_btn1").set_active(True)
            self.get_widget("rel_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("father_btn2").set_active(True)
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
        need_commit = False
        database = self.dbstate.db
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.fy1
            titanic = self.fy2
            unselect_path = (1,)
        else:
            phoenix = self.fy2
            titanic = self.fy1
            unselect_path = (0,)

        phoenix_father = database.get_person_from_handle(
                phoenix.get_father_handle())
        phoenix_mother = database.get_person_from_handle(
                phoenix.get_mother_handle())
        titanic_father = database.get_person_from_handle(
                titanic.get_father_handle())
        titanic_mother = database.get_person_from_handle(
                titanic.get_mother_handle())

        trans = database.transaction_begin("", True)

        # Use merge persons on father and mother to merge a family; The merge
        # person routine also merges families if necessary. Merging is not
        # an equal operation, there is one preferred family over the other.
        # The preferred family is the first listed in a persons
        # family_handle_list. Since the GUI allows users to chose the
        # preferred father, mother and family independent of each other, while
        # the merge person routine fixes preferred family with respect to
        # father and mother, the father and mother need first to be swapped
        # into the right family, before the merge person routines can be called.
        if self.get_widget("father_btn1").get_active() ^ use_handle1:
            father_handle = phoenix.get_father_handle()
            phoenix.set_father_handle(titanic.get_father_handle())
            titanic.set_father_handle(father_handle)
            phoenix_father.replace_handle_reference('Family',
                    phoenix.get_handle(), titanic.get_handle())
            titanic_father.replace_handle_reference('Family',
                    titanic.get_handle(), phoenix.get_handle())
            phoenix_father, titanic_father = titanic_father, phoenix_father
            database.commit_person(phoenix_father, trans)
            database.commit_person(titanic_father, trans)
            database.commit_family(phoenix, trans)
            database.commit_family(titanic, trans)
        if self.get_widget("mother_btn1").get_active() ^ use_handle1:
            mother_handle = phoenix.get_mother_handle()
            phoenix.set_mother_handle(titanic.get_mother_handle())
            titanic.set_mother_handle(mother_handle)
            phoenix_mother.replace_handle_reference('Family',
                    phoenix.get_handle(), titanic.get_handle())
            titanic_mother.replace_handle_reference('Family',
                    titanic.get_handle(), phoenix.get_handle())
            phoenix_mother, titanic_mother = titanic_mother, phoenix_mother
            database.commit_person(phoenix_mother, trans)
            database.commit_person(titanic_mother, trans)
            database.commit_family(phoenix, trans)
            database.commit_family(titanic, trans)

        if self.get_widget("rel_btn1").get_active() ^ use_handle1:
            phoenix.set_relationship(titanic.get_relationship())
            need_commit = True
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())
            need_commit = True
        if need_commit:
            database.commit_family(phoenix, trans)

        try:
            if phoenix_father != titanic_father:
                query = MergePersonQuery(self.dbstate, phoenix_father,
                        titanic_father)
                query.execute(trans)
            if phoenix_mother != titanic_mother:
                query = MergePersonQuery(self.dbstate, phoenix_mother,
                        titanic_mother)
                query.execute(trans)
        except MergeError, e:
            ErrorDialog( _("Cannot merge people"), str(e))
            # TODO: rollback
        else:
            database.transaction_commit(trans, _('Merge family'))
        self.database.emit('family-rebuild')
        self.uistate.viewmanager.active_page.selection.unselect_path(
                unselect_path)
        self.uistate.set_busy_cursor(False)
        self.close()
