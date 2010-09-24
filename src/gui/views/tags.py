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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  021111307  USA
#

# $Id$
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
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _
from gen.lib import Tag
from gui.dbguielement import DbGUIElement
from ListModel import ListModel, NOSORT, COLOR, INTEGER
import const
import GrampsDisplay
from QuestionDialog import QuestionDialog2
import gui.widgets.progressdialog as progressdlg

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

WIKI_HELP_PAGE = '%s_-_Entering_and_Editing_Data:_Detailed_-_part_3' % \
                                                        const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Tags')

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

    def _tag_delete(self, handle_list):
        """
        Called when tags are deleted.
        """
        for handle in handle_list:
            tag = self.db.get_tag_from_handle(handle)
            self.__tag_list.remove((tag.get_name(), handle))
        self.update_tag_menu()

    def _tag_rebuild(self):
        """
        Called when the tag list needs to be rebuilt.
        """
        self.__tag_list = []
        for handle in self.db.get_tag_handles():
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
            self.tag_action = gtk.ActionGroup('Tag')
            return

        tag_menu = '<menuitem action="NewTag"/>'
        tag_menu += '<menuitem action="OrganizeTags"/>'
        tag_menu += '<separator/>'
        for tag_name, handle in self.__tag_list:
            tag_menu += '<menuitem action="TAG_%s"/>' % escape(tag_name)
            actions.append(('TAG_%s' % tag_name, None, tag_name, None, None,
                         make_callback(self.tag_selected_rows, handle)))
        
        self.tag_ui = TAG_1 + tag_menu + TAG_2 + tag_menu + TAG_3

        actions.append(('Tag', 'gramps-tag', _('Tag'), None, None, None))
        actions.append(('NewTag', 'gramps-tag-new', _('New Tag...'), None, None,
                        self.cb_new_tag))
        actions.append(('OrganizeTags', None, _('Organize Tags...'), None, None,
                        self.cb_organize_tags))
        actions.append(('TagButton', 'gramps-tag', _('Tag'), None,
                        _('Tag selected rows'), self.cb_tag_button))
 
        self.tag_action = gtk.ActionGroup('Tag')
        self.tag_action.add_actions(actions)
        
    def cb_tag_button(self, action):
        """
        Display the popup menu when the toolbar button is clicked.
        """
        menu = self.uistate.uimanager.get_widget('/TagPopup')
        button = self.uistate.uimanager.get_widget('/ToolBar/TagTool/TagButton')
        menu.popup(None, None, cb_menu_position, 0, 0, button)
        
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
        new_dialog = NewTagDialog(self.uistate.window)
        tag_name, color_str = new_dialog.run()
        if tag_name and not self.db.get_tag_from_name(tag_name):
            trans = self.db.transaction_begin()
            tag = Tag()
            tag.set_name(tag_name)
            tag.set_color(color_str)
            tag.set_priority(self.db.get_number_of_tags())
            self.db.add_tag(tag, trans)
            self.db.transaction_commit(trans, _('Add Tag (%s)') % tag_name)
            self.tag_selected_rows(tag.get_handle())

    def tag_selected_rows(self, tag_handle):
        """
        Tag the selected rows with the given tag.
        """
        view = self.uistate.viewmanager.active_page
        selected = view.selected_handles()
        pmon = progressdlg.ProgressMonitor(progressdlg.GtkProgressDialog, 
                                            popup_time=2)
        status = progressdlg.LongOpStatus(msg=_("Adding Tags"),
                                          total_steps=len(selected),
                                          interval=len(selected)//20, 
                                          can_cancel=True)
        pmon.add_op(status)
        trans = self.db.transaction_begin()
        for object_handle in selected:
            status.heartbeat()
            if status.should_cancel():
                break
            view.add_tag(trans, object_handle, tag_handle)
        if not status.was_cancelled():
            tag = self.db.get_tag_from_handle(tag_handle)
            msg = _('Tag Selection (%s)') % tag.get_name()
            self.db.transaction_commit(trans, msg)
            status.end()

def cb_menu_position(menu, button):
    """
    Determine the position of the popup menu.
    """
    x_pos, y_pos = button.window.get_origin()
    x_pos += button.allocation.x
    y_pos += button.allocation.y + button.allocation.height
    
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
            if response == gtk.RESPONSE_HELP:
                GrampsDisplay.help(webpage=WIKI_HELP_PAGE,
                                   section=WIKI_HELP_SEC)
            else:
                break

        # Save changed priority values
        trans = self.db.transaction_begin()
        if self.__change_tag_priority(trans):
            self.db.transaction_commit(trans, _('Change Tag Priority'))

        self.top.destroy()

    def __change_tag_priority(self, trans):
        """
        Change the priority of the tags.  The order of the list corresponds to
        the priority of the tags.  The top tag in the list is the highest
        priority tag.
        """
        changed = False
        for new_priority, row in enumerate(self.namemodel.model):
            if row[0] != new_priority:
                changed = True
                tag = self.db.get_tag_from_handle(row[1])
                tag.set_priority(new_priority)
                self.db.commit_tag(tag, trans)
        return changed

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
        top = gtk.Dialog(title)
        top.set_default_size(400, 350)
        top.set_modal(True)
        top.set_transient_for(self.parent_window)
        top.set_has_separator(False)
        top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % _("Organize Tags"))
        label.set_use_markup(True)
        top.vbox.pack_start(label, 0, 0, 5)
        box = gtk.HBox()
        top.vbox.pack_start(box, 1, 1, 5)
        
        name_titles = [('', NOSORT, 20, INTEGER), # Priority
                       ('', NOSORT, 100), # Handle
                       (_('Name'), NOSORT, 200),
                       (_('Color'), NOSORT, 50, COLOR)]
        self.namelist = gtk.TreeView()
        self.namemodel = ListModel(self.namelist, name_titles)

        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(self.namelist)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        box.pack_start(slist, 1, 1, 5)
        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        bbox.set_spacing(6)
        up = gtk.Button(stock=gtk.STOCK_GO_UP)
        down = gtk.Button(stock=gtk.STOCK_GO_DOWN)
        add = gtk.Button(stock=gtk.STOCK_ADD)
        edit = gtk.Button(stock=gtk.STOCK_EDIT)
        remove = gtk.Button(stock=gtk.STOCK_REMOVE)
        up.connect('clicked', self.cb_up_clicked)
        down.connect('clicked', self.cb_down_clicked)
        add.connect('clicked', self.cb_add_clicked, top)
        edit.connect('clicked', self.cb_edit_clicked)
        remove.connect('clicked', self.cb_remove_clicked, top)
        top.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        top.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
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
        new_dialog = NewTagDialog(top)
        tag_name, color_str = new_dialog.run()
        if tag_name and not self.db.get_tag_from_name(tag_name):
            trans = self.db.transaction_begin()
            tag = Tag()
            tag.set_name(tag_name)
            tag.set_color(color_str)
            priority = self.db.get_number_of_tags() # Lowest
            tag.set_priority(priority)
            handle = self.db.add_tag(tag, trans)
            self.db.transaction_commit(trans, _('Add Tag (%s)') % tag_name)
            self.namemodel.add((priority, handle, tag_name, color_str))

    def cb_edit_clicked(self, button):
        """
        Edit the color of an existing tag.
        """
        # pylint: disable-msg=E1101
        store, iter_ = self.namemodel.get_selected()
        if iter_ is None:
            return
        handle = store.get_value(iter_, 1)
        tag_name = store.get_value(iter_, 2)
        old_color = gtk.gdk.Color(store.get_value(iter_, 3))
        
        title = _("%(title)s - Gramps") % {'title': _("Pick a Color")}
        colorseldlg = gtk.ColorSelectionDialog(title)
        colorseldlg.set_transient_for(self.top)
        colorseldlg.colorsel.set_current_color(old_color)
        colorseldlg.colorsel.set_previous_color(old_color)
        response = colorseldlg.run()
        if response == gtk.RESPONSE_OK:
            color_str = colorseldlg.colorsel.get_current_color().to_string()
            trans = self.db.transaction_begin()
            tag = self.db.get_tag_from_handle(handle)
            tag.set_color(color_str)
            self.db.commit_tag(tag, trans)
            self.db.transaction_commit(trans, _('Edit Tag (%s)') % tag_name)
            store.set_value(iter_, 3, color_str)
        colorseldlg.destroy()

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
            _("No"))
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
                   'Repository': (self.db.get_repository_from_handle,
                                  self.db.commit_repository),
                   'MediaObject': (self.db.get_object_from_handle,
                                   self.db.commit_media_object),
                   'Note': (self.db.get_note_from_handle,
                            self.db.commit_note)}

            links = [link for link in self.db.find_backlink_handles(tag_handle)]
            pmon = progressdlg.ProgressMonitor(progressdlg.GtkProgressDialog, 
                                                popup_time=2)
            status = progressdlg.LongOpStatus(msg=_("Removing Tags"),
                                              total_steps=len(links),
                                              interval=len(links)//20, 
                                              can_cancel=True)
            pmon.add_op(status)

            trans = self.db.transaction_begin()
            for classname, handle in links:
                status.heartbeat()
                if status.should_cancel():
                    break
                obj = fnc[classname][0](handle) # get from handle
                obj.remove_tag(tag_handle)
                fnc[classname][1](obj, trans) # commit

            self.db.remove_tag(tag_handle, trans)
            self.__change_tag_priority(trans)
            if not status.was_cancelled():
                msg = _('Delete Tag (%s)') % tag_name
                self.db.transaction_commit(trans, msg)
                store.remove(iter_)
                status.end()

#-------------------------------------------------------------------------
#
# New Tag Dialog
#
#-------------------------------------------------------------------------
class NewTagDialog(object):
    """
    A dialog to enable the user to create a new tag.
    """
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.entry = None
        self.color = None
        self.top = self._create_dialog()

    def run(self):
        """
        Run the dialog and return the result.
        """
        result = (None, None)
        response = self.top.run()
        if response == gtk.RESPONSE_OK:
            result = (self.entry.get_text(), self.color.get_color().to_string())
        self.top.destroy()
        return result

    def _create_dialog(self):
        """
        Create a dialog box to enter a new tag.
        """
        # pylint: disable-msg=E1101
        title = _("%(title)s - Gramps") % {'title': _("New Tag")}
        top = gtk.Dialog(title)
        top.set_default_size(300, 100)
        top.set_modal(True)
        top.set_transient_for(self.parent_window)
        top.set_has_separator(False)
        top.vbox.set_spacing(5)

        hbox = gtk.HBox()
        top.vbox.pack_start(hbox, False, False, 10)

        label = gtk.Label(_('Tag Name:'))
        self.entry = gtk.Entry()
        self.color = gtk.ColorButton()
        title = _("%(title)s - Gramps") % {'title': _("Pick a Color")}
        self.color.set_title(title)
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(self.entry, True, True, 5)
        hbox.pack_start(self.color, False, False, 5)
        
        top.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        top.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        top.show_all()
        return top
