#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# $Id: Check.py 7321 2006-09-13 02:57:45Z dallingham $

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
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import ManagedWindow
from BasicUtils import UpdateCallback
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class RemoveUnused(Tool.Tool,ManagedWindow.ManagedWindow,UpdateCallback):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _('Remove Unused Objects tool')

        Tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self, uistate,[],self.__class__)
        UpdateCallback.__init__(self,self.uistate.pulse_progressbar)

        self.dbstate = dbstate
        self.uistate = uistate

        if self.db.readonly:
            return

        self.init_gui()

    def init_gui(self):
        window = gtk.Dialog("%s - GRAMPS" % self.label,
                            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                     gtk.STOCK_OK,     gtk.RESPONSE_ACCEPT))

        window.set_border_width(12)
        window.set_has_separator(False)

        self.events_box  = gtk.CheckButton(_('Remove unused events'))
        self.sources_box = gtk.CheckButton(_('Remove unused sources'))
        self.places_box  = gtk.CheckButton(_('Remove unused places'))
        self.media_box  = gtk.CheckButton(_('Remove unused media'))
        self.repos_box  = gtk.CheckButton(_('Remove unused repositories'))

        self.events_box.set_active(self.options.handler.options_dict['events'])
        self.sources_box.set_active(
            self.options.handler.options_dict['sources'])
        self.places_box.set_active(
            self.options.handler.options_dict['places'])
        self.media_box.set_active(self.options.handler.options_dict['media'])
        self.repos_box.set_active(self.options.handler.options_dict['repos'])

        label = gtk.Label()
        window.vbox.add(label)
        label.set_padding(12,12)
        window.vbox.add(self.events_box)
        window.vbox.add(self.sources_box)
        window.vbox.add(self.places_box)
        window.vbox.add(self.media_box)
        window.vbox.add(self.repos_box)
        window.vbox.show_all()

        self.set_window(window,label,self.label)

        self.window.connect('response',self.response_handler)
        self.show()

    def response_handler(self,window,response):
        if response == gtk.RESPONSE_ACCEPT:
            self.run_tool()
        else:
            self.close()

    def build_menu_names(self,obj):
        return (_("Tool settings"),self.label)

    def run_tool(self):
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

        sr = ShowResults(self.dbstate,self.uistate,self.track)
        self.add_results = sr.add_results

        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        sr.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.collect_unused()

        self.uistate.progress.hide()
        self.uistate.window.window.set_cursor(None)
        self.window.window.set_cursor(None)
        sr.window.window.set_cursor(None)
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
                    self.add_results((the_type,handle,data))
                item = cursor.next()
                self.update()
            cursor.close()
            self.reset()

#-------------------------------------------------------------------------
#
# Show the results
#
#-------------------------------------------------------------------------
class ShowResults(ManagedWindow.ManagedWindow):
    MARK_COL       = 0
    OBJ_ID_COL     = 1
    OBJ_NAME_COL   = 2
    OBJ_TYPE_COL   = 3
    OBJ_HANDLE_COL = 4

    def __init__(self,dbstate,uistate,track):
        self.title = _('Unused Objects')

        ManagedWindow.ManagedWindow.__init__(self,uistate,track,self.__class__)

        self.dbstate = dbstate
        self.db = dbstate.db

        self.tables = {
            'events'  : {'get_func': self.db.get_event_from_handle,
                         'remove'  : self.db.remove_event,
                         'editor'  : 'EditEvent',
                         'stock'   : 'gramps-event',
                         'name_ix' : 4},
            'sources' : {'get_func': self.db.get_source_from_handle,
                         'remove'  : self.db.remove_source,
                         'editor'  : 'EditSource',
                         'stock'   : 'gramps-source',
                         'name_ix' : 2},
            'places'  : {'get_func': self.db.get_place_from_handle,
                         'remove'  : self.db.remove_place,
                         'editor'  : 'EditPlace',
                         'stock'   : 'gramps-place',
                         'name_ix' : 2},
            'media'   : {'get_func': self.db.get_object_from_handle,
                         'remove'  : self.db.remove_object,
                         'editor'  : 'EditMedia',
                         'stock'   : 'gramps-media',
                         'name_ix' : 4},
            'repos'   : {'get_func': self.db.get_repository_from_handle,
                         'remove'  : self.db.remove_repository,
                         'editor'  : 'EditRepository',
                         'stock'   : 'gramps-repository',
                         'name_ix' : 3},
            }

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_result","gramps")
        window = self.top.get_widget("verify_result")
        self.set_window(window,self.top.get_widget('title'),self.title)
    
        self.top.signal_autoconnect({
            "destroy_passed_object"  : self.close,
            })

        self.warn_tree = self.top.get_widget('warn_tree')
        self.warn_tree.connect('button_press_event', self.double_click)

        self.selection = self.warn_tree.get_selection()
        
        self.hide_button = self.top.get_widget('hide_button')
        self.hide_button.destroy()

        self.mark_button = self.top.get_widget('mark_all')
        self.mark_button.connect('clicked',self.mark_clicked)

        self.unmark_button = self.top.get_widget('unmark_all')
        self.unmark_button.connect('clicked',self.unmark_clicked)

        self.invert_button = self.top.get_widget('invert_all')
        self.invert_button.connect('clicked',self.invert_clicked)

        self.real_model = gtk.ListStore(bool,str,str,str,str)
        self.sort_model = gtk.TreeModelSort(self.real_model)
        self.warn_tree.set_model(self.sort_model)

        self.renderer = gtk.CellRendererText()
        self.img_renderer = gtk.CellRendererPixbuf()
        self.bool_renderer = gtk.CellRendererToggle()
        self.bool_renderer.connect('toggled',self.selection_toggled)

        # Add mark column
        mark_column = gtk.TreeViewColumn(_('Mark'),self.bool_renderer,
                                           active=ShowResults.MARK_COL)
        mark_column.set_sort_column_id(ShowResults.MARK_COL)
        self.warn_tree.append_column(mark_column)
        
        # Add image column
        img_column = gtk.TreeViewColumn(None, self.img_renderer )
        img_column.set_cell_data_func(self.img_renderer,self.get_image)
        self.warn_tree.append_column(img_column)        

        # Add column with object gramps_id
        id_column = gtk.TreeViewColumn(_('ID'), self.renderer,
                                       text=ShowResults.OBJ_ID_COL)
        id_column.set_sort_column_id(ShowResults.OBJ_ID_COL)
        self.warn_tree.append_column(id_column)

        # Add column with object name
        name_column = gtk.TreeViewColumn(_('Name'), self.renderer,
                                         text=ShowResults.OBJ_NAME_COL)
        name_column.set_sort_column_id(ShowResults.OBJ_NAME_COL)
        self.warn_tree.append_column(name_column)

        # Add a button to remove selected objects
        remove_button = self.window.add_button(gtk.STOCK_REMOVE,
                                               gtk.RESPONSE_ACCEPT)
        self.window.connect('response',self.response_handler)
       
        self.window.show_all()
        self.window_shown = False

    def response_handler(self,window,response):
        if response == gtk.RESPONSE_ACCEPT:
            self.do_remove()

    def do_remove(self):
        trans = self.db.transaction_begin("",batch=False)
        self.db.disable_signals()

        for row_num in range(len(self.real_model)-1,-1,-1):
            path = (row_num,)
            row = self.real_model[path]
            if not row[ShowResults.MARK_COL]:
                continue

            the_type = row[ShowResults.OBJ_TYPE_COL]
            handle = row[ShowResults.OBJ_HANDLE_COL]
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
        row[ShowResults.MARK_COL] = not row[ShowResults.MARK_COL]
        self.real_model.row_changed(real_path,row.iter)

    def mark_clicked(self,mark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[ShowResults.MARK_COL] = True

    def unmark_clicked(self,unmark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[ShowResults.MARK_COL] = False

    def invert_clicked(self,invert_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[ShowResults.MARK_COL] = not row[ShowResults.MARK_COL]

    def double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            (model,node) = self.selection.get_selected()
            if not node:
                return
            sort_path = self.sort_model.get_path(node)
            real_path = self.sort_model.convert_path_to_child_path(sort_path)
            row = self.real_model[real_path]
            the_type = row[ShowResults.OBJ_TYPE_COL]
            handle = row[ShowResults.OBJ_HANDLE_COL]
            self.call_editor(the_type,handle)

    def call_editor(self,the_type,handle):
        try:
            obj = self.tables[the_type]['get_func'](handle)
            editor_str = 'from Editors import %s as editor' \
                         % self.tables[the_type]['editor']
            exec(editor_str)            
            editor(self.dbstate, self.uistate, [], obj)
        except Errors.WindowActiveError:
            pass

    def get_image(self, column, cell, model, iter, user_data=None):
        the_type = model.get_value(iter, ShowResults.OBJ_TYPE_COL)
        the_stock = self.tables[the_type]['stock']
        cell.set_property('stock-id', the_stock)

    def add_results(self,results):
        (the_type,handle,data) = results

        gramps_id = data[1]
        name_ix = self.tables[the_type]['name_ix']
        name = data[name_ix]
        
        self.real_model.append(row=[False,gramps_id,name,the_type,handle])
        
        if not self.window_shown:
            self.show()
            self.window_shown = True

    def build_menu_names(self,obj):
        return (self.title,None)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class CheckOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'events'  : 1,
            'sources' : 1,
            'places'  : 1,
            'media'   : 1,
            'repos'   : 1,
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
            }

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'remove_unused',
    category = Tool.TOOL_DBFIX,
    tool_class = RemoveUnused,
    options_class = CheckOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Remove unused objects"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Removes unused objects from the database")
    )
