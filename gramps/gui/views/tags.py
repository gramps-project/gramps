# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010    Nick Hall
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
Provide tagging functionality.
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from bisect import insort_left
from xml.sax.saxutils import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.lib import Tag
from gramps.gen.db import DbTxn
from ..dbguielement import DbGUIElement
from ..listmodel import ListModel, NOSORT, COLOR, INTEGER
from gramps.gen.const import URL_MANUAL_PAGE
from ..display import display_help
from ..dialog import ErrorDialog, QuestionDialog2
import gramps.gui.widgets.progressdialog as progressdlg
from ..actiongroup import ActionGroup

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
TAG_1 = '''<ui>
  <menubar name="MenuBar">
    <menu action="EditMenu">
      <placeholder name="TagMenu">
        <menu action="Tag">
'''

TAG_2 = '''
        </menu>
      </placeholder>
    </menu>
  </menubar>
  <toolbar name="ToolBar">
    <placeholder name="TagTool">
      <toolitem action="TagButton"/>
    </placeholder>
  </toolbar>
  <popup name="TagPopup">
'''

TAG_3 = '''
  </popup>
</ui>'''

WIKI_HELP_PAGE = '%s_-_Filters' % \
                                URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Tagging')

#-------------------------------------------------------------------------
#
# Tags
#
#-------------------------------------------------------------------------
class Tags(DbGUIElement):
    """
    Provide tagging functionality.
    """
    def __init__(self, uistate, dbstate):
        self.signal_map = {
            'tag-add'     : self._tag_add,
            'tag-delete'  : self._tag_delete,
            'tag-update'  : self._tag_update,
            'tag-rebuild' : self._tag_rebuild
            }
        DbGUIElement.__init__(self, dbstate.db)

        self.db = dbstate.db
        self.uistate = uistate

        self.tag_id = None
        self.tag_ui = None
        self.tag_action = None
        self.__tag_list = []

        dbstate.connect('database-changed', self._db_changed)

        self._build_tag_menu()

    def tag_enable(self):
        """
        Enables the UI and action groups for the tag menu.
        """
        self.uistate.uimanager.insert_action_group(self.tag_action, 1)
        self.tag_id = self.uistate.uimanager.add_ui_from_string(self.tag_ui)
        self.uistate.uimanager.ensure_update()

    def tag_disable(self):
        """
        Remove the UI and action groups for the tag menu.
        """
        self.uistate.uimanager.remove_ui(self.tag_id)
        self.uistate.uimanager.remove_action_group(self.tag_action)
        self.uistate.uimanager.ensure_update()
        self.tag_id = None

    def _db_changed(self, db):
        """
        Called when the database is changed.
        """
        self.db = db
        self._change_db(db)
        self._tag_rebuild()

    def _connect_db_signals(self):
        """
        Connect database signals defined in the signal map.
        """
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])

    def _tag_add(self, handle_list):
        """
        Called when tags are added.
        """
        for handle in handle_list:
            tag = self.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.update_tag_menu()

    def _tag_update(self, handle_list):
        """
        Called when tags are updated.
        """
        for handle in handle_list:
            item = [item for item in self.__tag_list if item[1] == handle][0]
            self.__tag_list.remove(item)
            tag = self.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.update_tag_menu()

    def _tag_delete(self, handle_list):
        """
        Called when tags are deleted.
        """
        self.__tag_list = [item for item in self.__tag_list
                           if item[1] not in handle_list]
        self.update_tag_menu()

    def _tag_rebuild(self):
        """
        Called when the tag list needs to be rebuilt.
        """
        self.__tag_list = []
        for handle in self.db.get_tag_handles(sort_handles=True):
            tag = self.db.get_tag_from_handle(handle)
            self.__tag_list.append((tag.get_name(), tag.get_handle()))
        self.update_tag_menu()

    def update_tag_menu(self):
        """
        Re-build the menu when a tag is added or removed.
        """
        enabled = self.tag_id is not None
        if enabled:
            self.tag_disable()
        self._build_tag_menu()
        if enabled:
            self.tag_enable()

    def _build_tag_menu(self):
        """
        Builds the UI and action group for the tag menu.
        """
        actions = []

        if self.db is None:
            self.tag_ui = ''
            self.tag_action = ActionGroup(name='Tag')
            return

        tag_menu = '<menuitem action="NewTag"/>'
        tag_menu += '<menuitem action="OrganizeTags"/>'
        tag_menu += '<separator/>'
        for tag_name, handle in self.__tag_list:
            tag_menu += '<menuitem action="TAG_%s"/>' % handle
            actions.append(('TAG_%s' % handle, None, tag_name, None, None,
                         make_callback(self.tag_selected_rows, handle)))
        
        self.tag_ui = TAG_1 + tag_menu + TAG_2 + tag_menu + TAG_3

        actions.append(('Tag', 'gramps-tag', _('Tag'), None, None, None))
        actions.append(('NewTag', 'gramps-tag-new', _('New Tag...'), None, None,
                        self.cb_new_tag))
        actions.append(('OrganizeTags', None, _('Organize Tags...'), None, None,
                        self.cb_organize_tags))
        actions.append(('TagButton', 'gramps-tag', _('Tag'), None,
                        _('Tag selected rows'), self.cb_tag_button))
 
        self.tag_action = ActionGroup(name='Tag')
        self.tag_action.add_actions(actions)
        
    def cb_tag_button(self, action):
        """
        Display the popup menu when the toolbar button is clicked.
        """
        menu = self.uistate.uimanager.get_widget('/TagPopup')
        button = self.uistate.uimanager.get_widget('/ToolBar/TagTool/TagButton')
        menu.popup(None, None, cb_menu_position, button, 0, 0)
        
    def cb_organize_tags(self, action):
        """
        Display the Organize Tags dialog.
        """
        organize_dialog = OrganizeTagsDialog(self.db, self.uistate.window)
        organize_dialog.run()

    def cb_new_tag(self, action):
        """
        Create a new tag and tag the selected objects.
        """
        tag = Tag()
        tag.set_priority(self.db.get_number_of_tags())
        new_dialog = EditTag(self.db, self.uistate.window, tag)
        new_dialog.run()

        if tag.get_handle():
            self.tag_selected_rows(tag.get_handle())

    def tag_selected_rows(self, tag_handle):
        """
        Tag the selected rows with the given tag.
        """
        view = self.uistate.viewmanager.active_page
        selected = view.selected_handles()
        # Make the dialog modal so that the user can't start another
        # database transaction while the one setting tags is still running.
        pmon = progressdlg.ProgressMonitor(progressdlg.GtkProgressDialog, 
                ("", self.uistate.window, Gtk.DialogFlags.MODAL), popup_time=2)
        status = progressdlg.LongOpStatus(msg=_("Adding Tags"),
                                          total_steps=len(selected),
                                          interval=len(selected)//20)
        pmon.add_op(status)
        tag = self.db.get_tag_from_handle(tag_handle)
        msg = _('Tag Selection (%s)') % tag.get_name()
        with DbTxn(msg, self.db) as trans:
            for object_handle in selected:
                status.heartbeat()
                view.add_tag(trans, object_handle, tag_handle)
        status.end()

def cb_menu_position(*args):
    """
    Determine the position of the popup menu.
    """
    # takes two argument: menu, button
    if len(args) == 2:
        menu = args[0]
        button = args[1]
    # broken introspection can't handle MenuPositionFunc annotations corectly
    else:
        menu = args[0]
        button = args[3]

    ret_val, x_pos, y_pos = button.get_window().get_origin()
    x_pos += button.get_allocation().x
    y_pos += button.get_allocation().y + button.get_allocation().height
    
    return (x_pos, y_pos, False)

def make_callback(func, tag_handle):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x: func(tag_handle)

#-------------------------------------------------------------------------
#
# Organize Tags Dialog
#
#-------------------------------------------------------------------------
class OrganizeTagsDialog(object):
    """
    A dialog to enable the user to organize tags.
    """
    def __init__(self, db, parent_window):
        self.db = db
        self.parent_window = parent_window
        self.namelist = None
        self.namemodel = None
        self.top = self._create_dialog()

    def run(self):
        """
        Run the dialog and return the result.
        """
        self._populate_model()
        while True:
            response = self.top.run()
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE,
                                   section=WIKI_HELP_SEC)
            else:
                break

        # Save changed priority values
        if self.__priorities_changed():
            with DbTxn(_('Change Tag Priority'), self.db) as trans:
                self.__change_tag_priority(trans)

        self.top.destroy()

    def __priorities_changed(self):
        """
        Return True if the tag priorities have changed else return False.
        """
        priorities = [row[0] for row in self.namemodel.model]
        return priorities != list(range(len(self.namemodel.model)))

    def __change_tag_priority(self, trans):
        """
        Change the priority of the tags.  The order of the list corresponds to
        the priority of the tags.  The top tag in the list is the highest
        priority tag.
        """
        for new_priority, row in enumerate(self.namemodel.model):
            if row[0] != new_priority:
                tag = self.db.get_tag_from_handle(row[1])
                if tag:
                    tag.set_priority(new_priority)
                    self.db.commit_tag(tag, trans)

    def _populate_model(self):
        """
        Populate the model.
        """
        self.namemodel.clear()
        tags = []
        for tag in self.db.iter_tags():
            tags.append((tag.get_priority(),
                         tag.get_handle(),
                         tag.get_name(),
                         tag.get_color()))

        for row in sorted(tags):
            self.namemodel.add(row)
        
    def _create_dialog(self):
        """
        Create a dialog box to organize tags.
        """
        # pylint: disable-msg=E1101
        title = _("%(title)s - Gramps") % {'title': _("Organize Tags")}
        top = Gtk.Dialog(title)
        top.set_default_size(400, 350)
        top.set_modal(True)
        top.set_transient_for(self.parent_window)
        top.vbox.set_spacing(5)
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>'
                          % _("Organize Tags"))
        label.set_use_markup(True)
        top.vbox.pack_start(label, 0, 0, 5)
        box = Gtk.Box()
        top.vbox.pack_start(box, 1, 1, 5)
        
        name_titles = [('', NOSORT, 20, INTEGER), # Priority
                       ('', NOSORT, 100), # Handle
                       (_('Name'), NOSORT, 200),
                       (_('Color'), NOSORT, 50, COLOR)]
        self.namelist = Gtk.TreeView()
        self.namemodel = ListModel(self.namelist, name_titles)

        slist = Gtk.ScrolledWindow()
        slist.add(self.namelist)
        slist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(slist, 1, 1, 5)
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.START)
        bbox.set_spacing(6)
        up = Gtk.Button.new_with_mnemonic(_('_Up'))
        down = Gtk.Button.new_with_mnemonic(_('_Down'))
        add = Gtk.Button.new_with_mnemonic(_('_Add'))
        edit = Gtk.Button.new_with_mnemonic(_('_Edit'))
        remove = Gtk.Button.new_with_mnemonic(_('_Remove'))
        up.connect('clicked', self.cb_up_clicked)
        down.connect('clicked', self.cb_down_clicked)
        add.connect('clicked', self.cb_add_clicked, top)
        edit.connect('clicked', self.cb_edit_clicked, top)
        remove.connect('clicked', self.cb_remove_clicked, top)
        top.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        top.add_button(_('_Help'), Gtk.ResponseType.HELP)
        bbox.add(up)
        bbox.add(down)
        bbox.add(add)
        bbox.add(edit)
        bbox.add(remove)
        box.pack_start(bbox, 0, 0, 5)
        top.show_all()
        return top

    def cb_up_clicked(self, obj):
        """
        Move the current selection up one row.
        """
        row = self.namemodel.get_selected_row()
        self.namemodel.move_up(row)

    def cb_down_clicked(self, obj):
        """
        Move the current selection down one row.
        """
        row = self.namemodel.get_selected_row()
        self.namemodel.move_down(row)

    def cb_add_clicked(self, button, top):
        """
        Create a new tag.
        """
        tag = Tag()
        tag.set_priority(self.db.get_number_of_tags())
        edit_dialog = EditTag(self.db, top, tag)
        edit_dialog.run()

        if tag.get_handle():
            self.namemodel.add((tag.get_priority(),
                                tag.get_handle(),
                                tag.get_name(),
                                tag.get_color()))

    def cb_edit_clicked(self, button, top):
        """
        Edit the color of an existing tag.
        """
        store, iter_ = self.namemodel.get_selected()
        if iter_ is None:
            return

        tag = self.db.get_tag_from_handle(store.get_value(iter_, 1))
        edit_dialog = EditTag(self.db, top, tag)
        edit_dialog.run()
        
        store.set_value(iter_, 2, tag.get_name())
        store.set_value(iter_, 3, tag.get_color())
        
    def cb_remove_clicked(self, button, top):
        """
        Remove the selected tag.
        """
        store, iter_ = self.namemodel.get_selected()
        if iter_ is None:
            return
        tag_handle = store.get_value(iter_, 1)
        tag_name = store.get_value(iter_, 2)
    
        yes_no = QuestionDialog2(
            _("Remove tag '%s'?") % tag_name,
            _("The tag definition will be removed.  "
              "The tag will be also removed from all objects in the database."),
            _("Yes"),
            _("No"),
            parent=top)

        prompt = yes_no.run()
        if prompt:

            fnc = {'Person': (self.db.get_person_from_handle,
                              self.db.commit_person),
                   'Family': (self.db.get_family_from_handle,
                              self.db.commit_family),
                   'Event': (self.db.get_event_from_handle,
                             self.db.commit_event),
                   'Place': (self.db.get_place_from_handle,
                             self.db.commit_place),
                   'Source': (self.db.get_source_from_handle,
                              self.db.commit_source),
                   'Citation': (self.db.get_citation_from_handle,
                                self.db.commit_citation),
                   'Repository': (self.db.get_repository_from_handle,
                                  self.db.commit_repository),
                   'MediaObject': (self.db.get_object_from_handle,
                                   self.db.commit_media_object),
                   'Note': (self.db.get_note_from_handle,
                            self.db.commit_note)}

            links = [link for link in self.db.find_backlink_handles(tag_handle)]
            # Make the dialog modal so that the user can't start another
            # database transaction while the one removing tags is still running.
            pmon = progressdlg.ProgressMonitor(progressdlg.GtkProgressDialog, 
                       ("", self.parent_window, Gtk.DialogFlags.MODAL), popup_time=2)
            status = progressdlg.LongOpStatus(msg=_("Removing Tags"),
                                              total_steps=len(links),
                                              interval=len(links)//20)
            pmon.add_op(status)

            msg = _('Delete Tag (%s)') % tag_name
            with DbTxn(msg, self.db) as trans:
                for classname, handle in links:
                    status.heartbeat()
                    obj = fnc[classname][0](handle) # get from handle
                    obj.remove_tag(tag_handle)
                    fnc[classname][1](obj, trans) # commit

                self.db.remove_tag(tag_handle, trans)
                self.__change_tag_priority(trans)
            self.namemodel.remove(iter_)
            status.end()

#-------------------------------------------------------------------------
#
# Tag editor
#
#-------------------------------------------------------------------------
class EditTag(object):
    """
    A dialog to enable the user to create a new tag.
    """
    def __init__(self, db, parent_window, tag):
        self.parent_window = parent_window
        self.db = db
        self.tag = tag
        self.entry = None
        self.color = None
        self.top = self._create_dialog()

    def run(self):
        """
        Run the dialog and return the result.
        """
        response = self.top.run()
        if response == Gtk.ResponseType.OK:
            self._save()
        self.top.destroy()

    def _save(self):
        """
        Save the changes made to the tag.
        """
        self.tag.set_name(str(self.entry.get_text()))
        rgba = self.color.get_rgba()
        hexval = "#%02x%02x%02x" % (int(rgba.red * 255),
                                    int(rgba.green * 255),
                                    int(rgba.blue * 255))
        self.tag.set_color(hexval)

        if not self.tag.get_name():
            ErrorDialog(
                _("Cannot save tag"),
                _("The tag name cannot be empty"),
                parent=self.top)
            return

        if not self.tag.get_handle():
            msg = _("Add Tag (%s)") % self.tag.get_name()
            with DbTxn(msg, self.db) as trans:
                self.db.add_tag(self.tag, trans)
        else:
            orig = self.db.get_tag_from_handle(self.tag.get_handle())
            if self.tag.serialize() != orig.serialize():
                msg = _("Edit Tag (%s)") % self.tag.get_name()
                with DbTxn(msg, self.db) as trans:
                    self.db.commit_tag(self.tag, trans)

    def _create_dialog(self):
        """
        Create a dialog box to enter a new tag.
        """
        # pylint: disable-msg=E1101
        if self.tag.get_handle():
            title = _('Tag: %s')  % self.tag.get_name()
        else:
            title = _('New Tag')
        top = Gtk.Dialog(_("%(title)s - Gramps") % {'title': title})
        top.set_default_size(300, 100)
        top.set_modal(True)
        top.set_transient_for(self.parent_window)
        top.vbox.set_spacing(5)

        hbox = Gtk.Box()
        top.vbox.pack_start(hbox, False, False, 10)

        label = Gtk.Label(label=_('Tag Name:'))
        self.entry = Gtk.Entry()
        self.entry.set_text(self.tag.get_name())
        self.color = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.tag.get_color())
        self.color.set_rgba(rgba)
        title = _("%(title)s - Gramps") % {'title': _("Pick a Color")}
        self.color.set_title(title)
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(self.entry, True, True, 5)
        hbox.pack_start(self.color, False, False, 5)
        
        top.add_button(_('_OK'), Gtk.ResponseType.OK)
        top.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        top.show_all()
        return top
