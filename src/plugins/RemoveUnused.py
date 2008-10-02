#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Stephane Charette
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

"Find unused objects and remove with the user's permission"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".RemoveUnused")

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade
import gobject
from gen.lib import StyledText

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import ManagedWindow
from DateHandler import displayer as _dd
from BasicUtils import UpdateCallback
from PluginUtils import Tool
from gen.plug import PluginManager

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class RemoveUnused(Tool.Tool,ManagedWindow.ManagedWindow,UpdateCallback):
    MARK_COL       = 0
    OBJ_ID_COL     = 1
    OBJ_NAME_COL   = 2
    OBJ_TYPE_COL   = 3
    OBJ_HANDLE_COL = 4

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.title = _('Unused Objects')

        Tool.Tool.__init__(self, dbstate, options_class, name)

        if self.db.readonly:
            return

        ManagedWindow.ManagedWindow.__init__(self, uistate,[],self.__class__)
        UpdateCallback.__init__(self,self.uistate.pulse_progressbar)

        self.dbstate = dbstate
        self.uistate = uistate

        self.tables = {
            'events'  : {'get_func': self.db.get_event_from_handle,
                         'remove'  : self.db.remove_event,
                         'get_text': self.get_event_text,
                         'editor'  : 'EditEvent',
                         'stock'   : 'gramps-event',
                         'name_ix' : 4},
            'sources' : {'get_func': self.db.get_source_from_handle,
                         'remove'  : self.db.remove_source,
                         'get_text': None,
                         'editor'  : 'EditSource',
                         'stock'   : 'gramps-source',
                         'name_ix' : 2},
            'places'  : {'get_func': self.db.get_place_from_handle,
                         'remove'  : self.db.remove_place,
                         'get_text': None,
                         'editor'  : 'EditPlace',
                         'stock'   : 'gramps-place',
                         'name_ix' : 2},
            'media'   : {'get_func': self.db.get_object_from_handle,
                         'remove'  : self.db.remove_object,
                         'get_text': None,
                         'editor'  : 'EditMedia',
                         'stock'   : 'gramps-media',
                         'name_ix' : 4},
            'repos'   : {'get_func': self.db.get_repository_from_handle,
                         'remove'  : self.db.remove_repository,
                         'get_text': None,
                         'editor'  : 'EditRepository',
                         'stock'   : 'gramps-repository',
                         'name_ix' : 3},
            'notes'   : {'get_func': self.db.get_note_from_handle,
                         'remove'  : self.db.remove_note,
                         'get_text': self.get_note_text,
                         'editor'  : 'EditNote',
                         'stock'   : 'gramps-notes',
                         'name_ix' : 2},
            }

        self.init_gui()

    def init_gui(self):
        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "unused.glade"

        self.top = glade.XML(self.glade_file,"unused","gramps")
        window = self.top.get_widget("unused")
        self.set_window(window,self.top.get_widget('title'),self.title)

        self.events_box = self.top.get_widget('events_box')
        self.sources_box = self.top.get_widget('sources_box')
        self.places_box = self.top.get_widget('places_box')
        self.media_box = self.top.get_widget('media_box')
        self.repos_box = self.top.get_widget('repos_box')
        self.notes_box = self.top.get_widget('notes_box')
        self.find_button = self.top.get_widget('find_button')
        self.remove_button = self.top.get_widget('remove_button')

        self.events_box.set_active(self.options.handler.options_dict['events'])
        self.sources_box.set_active(
            self.options.handler.options_dict['sources'])
        self.places_box.set_active(
            self.options.handler.options_dict['places'])
        self.media_box.set_active(self.options.handler.options_dict['media'])
        self.repos_box.set_active(self.options.handler.options_dict['repos'])
        self.notes_box.set_active(self.options.handler.options_dict['notes'])

        self.warn_tree = self.top.get_widget('warn_tree')
        self.warn_tree.connect('button_press_event', self.double_click)

        self.selection = self.warn_tree.get_selection()
        
        self.mark_button = self.top.get_widget('mark_button')
        self.mark_button.connect('clicked',self.mark_clicked)

        self.unmark_button = self.top.get_widget('unmark_button')
        self.unmark_button.connect('clicked',self.unmark_clicked)

        self.invert_button = self.top.get_widget('invert_button')
        self.invert_button.connect('clicked',self.invert_clicked)

        self.real_model = gtk.ListStore(gobject.TYPE_BOOLEAN, 
                                        gobject.TYPE_STRING, 
                                        gobject.TYPE_STRING, 
                                        gobject.TYPE_STRING, 
                                        gobject.TYPE_STRING)
        self.sort_model = gtk.TreeModelSort(self.real_model)
        self.warn_tree.set_model(self.sort_model)

        self.renderer = gtk.CellRendererText()
        self.img_renderer = gtk.CellRendererPixbuf()
        self.bool_renderer = gtk.CellRendererToggle()
        self.bool_renderer.connect('toggled',self.selection_toggled)

        # Add mark column
        mark_column = gtk.TreeViewColumn(_('Mark'),self.bool_renderer,
                                           active=RemoveUnused.MARK_COL)
        mark_column.set_sort_column_id(RemoveUnused.MARK_COL)
        self.warn_tree.append_column(mark_column)
        
        # Add image column
        img_column = gtk.TreeViewColumn(None, self.img_renderer )
        img_column.set_cell_data_func(self.img_renderer,self.get_image)
        self.warn_tree.append_column(img_column)        

        # Add column with object gramps_id
        id_column = gtk.TreeViewColumn(_('ID'), self.renderer,
                                       text=RemoveUnused.OBJ_ID_COL)
        id_column.set_sort_column_id(RemoveUnused.OBJ_ID_COL)
        self.warn_tree.append_column(id_column)

        # Add column with object name
        name_column = gtk.TreeViewColumn(_('Name'), self.renderer,
                                         text=RemoveUnused.OBJ_NAME_COL)
        name_column.set_sort_column_id(RemoveUnused.OBJ_NAME_COL)
        self.warn_tree.append_column(name_column)

        self.top.signal_autoconnect({
            "destroy_passed_object"   : self.close,
            "on_remove_button_clicked": self.do_remove,
            "on_find_button_clicked"  : self.find,
            })

        self.dc_label = self.top.get_widget('dc_label')

        self.sensitive_list = [self.warn_tree,self.mark_button,
                               self.unmark_button,self.invert_button,
                               self.dc_label,self.remove_button]

        for item in self.sensitive_list:
            item.set_sensitive(False)

        self.show()

    def build_menu_names(self, obj):
        return (self.title,None)

    def find(self, obj):
        self.options.handler.options_dict['events'] = \
                                        int(self.events_box.get_active())
        self.options.handler.options_dict['sources'] = \
                                        int(self.sources_box.get_active())
        self.options.handler.options_dict['places'] = \
                                        int(self.places_box.get_active())
        self.options.handler.options_dict['media'] = \
                                        int(self.media_box.get_active())
        self.options.handler.options_dict['repos'] = \
                                        int(self.repos_box.get_active())
        self.options.handler.options_dict['notes'] = \
                                        int(self.notes_box.get_active())

        for item in self.sensitive_list:
            item.set_sensitive(True)

        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.real_model.clear()
        self.collect_unused()

        self.uistate.progress.hide()
        self.uistate.window.window.set_cursor(None)
        self.window.window.set_cursor(None)
        self.reset()
        
        # Save options
        self.options.handler.save_options()

    def collect_unused(self):
        # Run through all requested tables and check all objects
        # for being referenced some place. If not, add_results on them.
        
        tables = {
            'events'  : {'cursor_func': self.db.get_event_cursor,
                         'total_func' : self.db.get_number_of_events},
            'sources' : {'cursor_func': self.db.get_source_cursor,
                         'total_func' : self.db.get_number_of_sources},
            'places'  : {'cursor_func': self.db.get_place_cursor,
                         'total_func' : self.db.get_number_of_places},
            'media'   : {'cursor_func': self.db.get_media_cursor,
                         'total_func' : self.db.get_number_of_media_objects},
            'repos'   : {'cursor_func': self.db.get_repository_cursor,
                         'total_func' : self.db.get_number_of_repositories},
            'notes'   : {'cursor_func': self.db.get_note_cursor,
                         'total_func' : self.db.get_number_of_notes},
            }

        for the_type in tables.keys():
            if not self.options.handler.options_dict[the_type]:
                # This table was not requested. Skip it.
                continue

            cursor = tables[the_type]['cursor_func']()
            total = tables[the_type]['total_func']()
            self.set_total(total)
            item = cursor.first()
            while item:
                (handle,data) = item

                hlist = [x for x in self.db.find_backlink_handles(handle)]
                if len(hlist) == 0:
                    self.add_results((the_type, handle, data))
                item = cursor.next()
                self.update()
            cursor.close()
            self.reset()

    def do_remove(self, obj):
        trans = self.db.transaction_begin("",batch=False)
        self.db.disable_signals()

        for row_num in range(len(self.real_model)-1,-1,-1):
            path = (row_num,)
            row = self.real_model[path]
            if not row[RemoveUnused.MARK_COL]:
                continue

            the_type = row[RemoveUnused.OBJ_TYPE_COL]
            handle = row[RemoveUnused.OBJ_HANDLE_COL]
            remove_func = self.tables[the_type]['remove']
            remove_func(handle, trans)

            self.real_model.remove(row.iter)

        self.db.transaction_commit(trans, _("Remove unused objects"))
        self.db.enable_signals()
        self.db.request_rebuild()

    def selection_toggled(self,cell,path_string):
        sort_path = tuple([int (i) for i in path_string.split(':')])
        real_path = self.sort_model.convert_path_to_child_path(sort_path)
        row = self.real_model[real_path]
        row[RemoveUnused.MARK_COL] = not row[RemoveUnused.MARK_COL]
        self.real_model.row_changed(real_path,row.iter)

    def mark_clicked(self,mark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = True

    def unmark_clicked(self,unmark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = False

    def invert_clicked(self,invert_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = not row[RemoveUnused.MARK_COL]

    def double_click(self, obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            (model, node) = self.selection.get_selected()
            if not node:
                return
            sort_path = self.sort_model.get_path(node)
            real_path = self.sort_model.convert_path_to_child_path(sort_path)
            row = self.real_model[real_path]
            the_type = row[RemoveUnused.OBJ_TYPE_COL]
            handle = row[RemoveUnused.OBJ_HANDLE_COL]
            self.call_editor(the_type, handle)

    def call_editor(self,the_type, handle):
        try:
            obj = self.tables[the_type]['get_func'](handle)
            editor_str = 'from Editors import %s as editor' \
                         % self.tables[the_type]['editor']
            exec(editor_str)            
            editor(self.dbstate, self.uistate, [], obj)
        except Errors.WindowActiveError:
            pass

    def get_image(self, column, cell, model, iter, user_data=None):
        the_type = model.get_value(iter, RemoveUnused.OBJ_TYPE_COL)
        the_stock = self.tables[the_type]['stock']
        cell.set_property('stock-id', the_stock)

    def add_results(self, results):
        (the_type, handle, data) = results
        gramps_id = data[1]

        # if we have a function that will return to us some type
        # of text summary, then we should use it; otherwise we'll
        # use the generic field index provided in the tables above
        if self.tables[the_type]['get_text']:
            text = self.tables[the_type]['get_text'](the_type, handle, data)
        else:
            # grab the text field index we know about, and hope
            # it represents something useful to the user
            name_ix = self.tables[the_type]['name_ix']
            text = data[name_ix]

        # insert a new row into the table        
        self.real_model.append(row=[False, gramps_id, text, the_type, handle])

    def get_event_text(self, the_type, handle, data):
        """
        Come up with a short line of text that we can use as
        a summary to represent this event.
        """

        # get the event:
        event = self.tables[the_type]['get_func'](handle)

        # first check to see if the event has a descriptive name
        text = event.get_description()  # (this is rarely set for events)

        # if we don't have a description...
        if text == '':
            # ... then we merge together several fields

            # get the event type (marriage, birth, death, etc.)
            text = str(event.get_type())

            # see if there is a date
            date = _dd.display(event.get_date_object())
            if date != '':
                text += '; %s' % date

            # see if there is a place
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.db.get_place_from_handle(place_handle)
                text += '; %s' % place.get_title()

        return text
        
    def get_note_text(self, the_type, handle, data):
        """
        We need just the first few words of a note as a summary.
        """
        # get the note object
        note = self.tables[the_type]['get_func'](handle)

        # get the note text; this ignores (discards) formatting
        text = note.get()

        # convert whitespace to a single space
        text = " ".join(text.split())

        # if the note is too long, truncate it
        if len(text) > 80:
            text = text[:80] + "..."

        return text

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class CheckOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'events'  : 1,
            'sources' : 1,
            'places'  : 1,
            'media'   : 1,
            'repos'   : 1,
            'notes'   : 1,
        }
        self.options_help = {
            'events'  : ("=0/1","Whether to use check for unused events",
                         ["Do not check events","Check events"],
                         True),
            'sources' : ("=0/1","Whether to use check for unused sources",
                         ["Do not check sources","Check sources"],
                         True),
            'places'  : ("=0/1","Whether to use check for unused places",
                          ["Do not check places","Check places"],
                          True),
            'media'   : ("=0/1","Whether to use check for unused media",
                          ["Do not check media","Check media"],
                          True),
            'repos'   : ("=0/1","Whether to use check for unused repositories",
                          ["Do not check repositories","Check repositories"],
                          True),
            'notes'   : ("=0/1","Whether to use check for unused notes",
                          ["Do not check notes","Check notes"],
                          True),
            }

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_tool(
    name = 'remove_unused',
    category = Tool.TOOL_DBFIX,
    tool_class = RemoveUnused,
    options_class = CheckOptions,
    modes = PluginManager.TOOL_MODE_GUI,
    translated_name = _("Remove Unused Objects"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Removes unused objects from the database")
    )
