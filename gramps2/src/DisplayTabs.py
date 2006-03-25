#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import gobject
import pango
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# python
#
#-------------------------------------------------------------------------

from TransUtils import sgettext as _
import pickle

try:
    set()
except:
    from sets import Set as set
    
#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DisplayTabs")

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
import DateHandler
import NameDisplay
import RelLib
import Utils
import ImgManip
import Spell
import Errors

from DdTargets import DdTargets
from GrampsWidgets import SimpleButton

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
dnddata = None

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

class GrampsTab(gtk.HBox):
    """
    This class provides the base level class for 'tabs', which are used to
    fill in notebook tabs for GRAMPS edit dialogs. Each tab returns a
    gtk container widget which can be inserted into a gtk.Notebook by the
    instantiating object.

    All tab classes should inherit from GrampsTab
    """

    def __init__(self,dbstate,uistate,track,name):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        """
        gtk.HBox.__init__(self)

        # store information to pass to child windows
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.changed = False
        
        # save name used for notebook label, and build the widget used
        # for the label
        
        self.tab_name = name
        self.label_container = self.build_label_widget()

        # build the interface
        self.build_interface()

    def is_empty(self):
        """
        Indicates if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        return True

    def build_label_widget(self):
        """
        Standard routine to build a widget. Does not need to be overridden
        by the derrived class. Creates an container that has the label and
        the icon in it.
        @returns: widget to be used for the notebook label.
        @rtype: gtk.HBox
        """
        hbox = gtk.HBox()
        self.tab_image = gtk.image_new_from_stock(self.get_icon_name(),
                                                  gtk.ICON_SIZE_MENU)
        self.label = gtk.Label(self.tab_name)
        hbox.pack_start(self.tab_image)
        hbox.set_spacing(6)
        hbox.add(self.label)
        hbox.show_all()
        return hbox

    def get_icon_name(self):
        """
        Provides the name of the registered stock icon to be used as the
        icon in the label. This is typically overridden by the derrived
        class to provide the new name.
        @returns: stock icon name
        @rtype: str
        """
        return gtk.STOCK_NEW

    def get_tab_widget(self):
        """
        Provides the widget to be used for the notebook tab label. A
        container class is provided, and the object may manipulate the
        child widgets contained in the container.
        @returns: gtk widget
        @rtype: gtk.HBox
        """
        return self.label_container

    def _set_label(self):
        """
        Updates the label based of if the tab contains information. Tabs
        without information will not have an icon, and the text will not
        be bold. Tabs that contain data will have their icon displayed and
        the label text will be in bold face.
        """
        if not self.is_empty():
            self.tab_image.show()
            self.label.set_text("<b>%s</b>" % self.tab_name)
            self.label.set_use_markup(True)
        else:
            self.tab_image.hide()
            self.label.set_text(self.tab_name)

    def build_interface(self):
        """
        Builds the interface for the derived class. This function should be
        overridden in the derived class. Since the classes are derrived from
        gtk.HBox, the self.pack_start, self.pack_end, and self.add functions
        can be used to add widgets to the interface.
        """
        pass

class ButtonTab(GrampsTab):
    """
    This class derives from the base GrampsTab, yet is not a usable Tab. It
    serves as another base tab for classes which need an Add/Edit/Remove button
    combination.
    """

    _MSG = {
        'add'   : _('Add'),
        'del'   : _('Remove'),
        'edit'  : _('Edit'),
        'share' : _('Share'),
        }

    def __init__(self,dbstate,uistate,track,name,share_button=False):
        """
        Similar to the base class, except after Build
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        """
        GrampsTab.__init__(self,dbstate,uistate,track,name)
        self.tooltips = gtk.Tooltips()
        self.create_buttons(share_button)

    def create_buttons(self,share_button=False):
        """
        Creates a button box consisting of three buttons, one for Add,
        one for Edit, and one for Delete. This button box is then appended
        hbox (self).
        """
        self.add_btn  = SimpleButton(gtk.STOCK_ADD, self.add_button_clicked)
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)
        self.del_btn  = SimpleButton(gtk.STOCK_REMOVE, self.del_button_clicked)

        self.tooltips.set_tip(self.add_btn,  self._MSG['add'])
        self.tooltips.set_tip(self.edit_btn, self._MSG['edit'])
        self.tooltips.set_tip(self.del_btn,  self._MSG['del'])
        
        if share_button:
            self.share_btn  = SimpleButton(gtk.STOCK_INDEX, self.share_button_clicked)
            self.tooltips.set_tip(self.share_btn, self._MSG['share'])
        
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.add_btn,False)
        if share_button:
            vbox.pack_start(self.share_btn,False)
        vbox.pack_start(self.edit_btn,False)
        vbox.pack_start(self.del_btn,False)
        vbox.show_all()
        self.pack_start(vbox,False)

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs,
        the Edit button handler is called
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.edit_button_clicked(obj)

    def add_button_clicked(self,obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Add clicked"

    def share_button_clicked(self,obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Share clicked"

    def del_button_clicked(self,obj):
        """
        Function called with the Delete button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Delete clicked"

    def edit_button_clicked(self,obj):
        """
        Function called with the Edit button is clicked or the double
        click is caught. This function should be overridden by the derived
        class.
        """
        print "Uncaught Edit clicked"

    def _selection_changed(self,obj=None):
        """
        Attached to the selection's 'changed' signal. Checks
        to see if anything is selected. If it is, the edit and
        delete buttons are enabled, otherwise the are disabled.
        """
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
            self.del_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            self.del_btn.set_sensitive(False)

class EmbeddedList(ButtonTab):
    """
    This class provides the base class for all the list tabs. It
    maintains a gtk.TreeView, including the selection and button
    sensitivity.
    """
    
    _HANDLE_COL = -1
    _DND_TYPE   = None
    _DND_EXTRA  = None
    
    def __init__(self, dbstate, uistate, track, name, build_model,share=False):
        """
        Creates a new list, using the passed build_model to
        populate the list.
        """
        ButtonTab.__init__(self, dbstate, uistate, track, name, share)
        self.changed = False
        self.build_model = build_model

        # handle the selection
        self.selection = self.tree.get_selection()
        self.selection.connect('changed',self._selection_changed)

        # build the columns
        self.columns = []
        self.build_columns()

        if self._DND_TYPE:
            self._set_dnd()

        # build the initial data
        self.rebuild()
        self.show_all()

    def find_index(self,obj):
        """
        returns the index of the object within the associated data
        """
        return self.get_data().index(obj)

    def _set_dnd(self):
        """
        Sets up drag-n-drop. The source and destionation are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        if self._DND_EXTRA:
            dnd_types = [ self._DND_TYPE.target(), self._DND_EXTRA.target() ]
        else:
            dnd_types = [ self._DND_TYPE.target() ]
        
        self.tree.drag_dest_set(gtk.DEST_DEFAULT_ALL, dnd_types, ACTION_COPY)
        self.tree.drag_source_set(BUTTON1_MASK, [self._DND_TYPE.target()], ACTION_COPY)
        self.tree.connect('drag_data_get', self.drag_data_get)
        self.tree.connect('drag_data_received', self.drag_data_received)
        
    def drag_data_get(self,widget, context, sel_data, info, time):
        """
        Provide the drag_data_get function, which passes a tuple consisting of:

           1) Drag type defined by the .drag_type field specfied by the value
              assigned to _DND_TYPE
           2) The id value of this object, used for the purpose of determining
              the source of the object. If the source of the object is the same
              as the object, we are doing a reorder instead of a normal drag
              and drop
           3) Pickled data. The pickled version of the selected object
           4) Source row. Used for a reorder to determine the original position
              of the object
        """

        # get the selected object, returning if not is defined
        obj = self.get_selected()
        if not obj:
            return

        # pickle the data, and build the tuple to be passed
        value = (self._DND_TYPE.drag_type, id(self), obj,self.find_index(obj))
        data = pickle.dumps(value)

        # pass as a string (8 bits)
        sel_data.set(sel_data.target, 8, data)

    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.data:
            dnddata = pickle.loads(sel_data.data)
            mytype = dnddata[0]
            selfid = dnddata[1]
            obj = dnddata[2]
            row_from = dnddata[3]

            # make sure this is the correct DND type for this object
            if mytype == self._DND_TYPE.drag_type:
                
                # determine the destination row
                row = self._find_row(x,y)

                # if the is same object, we have a move, otherwise,
                # it is a standard drag-n-drop
                
                if id(self) == selfid:
                    self._move(row_from,row,obj)
                else:
                    self._handle_drag(row,obj)
                self.rebuild()
            elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                self.handle_extra_type(mytype,obj)

    def handle_extra_type(self, objtype, obj):
        pass

    def _find_row(self,x,y):
        row = self.tree.get_path_at_pos(x,y)
        if row == None:
            return len(self.get_data())
        else:
            return row[0][0]

    def _handle_drag(self, row, obj):
        self.get_data().insert(row,obj)
        self.changed = True
        self.rebuild()

    def _move(self, row_from, row_to, obj):
        dlist = self.get_data()
        if row_from < row_to:
            dlist.insert(row_to,obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to-1,obj)
        self.changed = True
        self.rebuild()

    def get_icon_name(self):
        """
        Specifies the basic icon used for a generic list. Typically,
        a derived class will override this. The icon chose is the
        STOCK_JUSTIFY_FILL icon, which in the default GTK style
        looks kind of like a list.
        """
        return gtk.STOCK_JUSTIFY_FILL

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.get_data()
            ref_list.remove(ref)
            self.changed = True
            self.rebuild()

    def build_interface(self):
        """
        Builds the interface, instantiating a gtk.TreeView in a
        gtk.ScrolledWindow.
        """

        # create the tree, turn on rule hinting and connect the
        # button press to the double click function.
        
        self.tree = gtk.TreeView()
        self.tree.set_reorderable(True)
        self.tree.set_rules_hint(True)
        self.tree.connect('button_press_event',self.double_click)

        # create the scrolled window, and attach the treeview
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add(self.tree)
        self.pack_start(scroll,True)

    def get_selected(self):
        """
        returns the value associated with selected row in the model,
        based of the _HANDLE_COL value. Each model must define this
        to indicate what the returned value should be. If no selection
        has been made, None is returned.
        """
        (model,node) = self.selection.get_selected()
        if node:
            return model.get_value(node,self._HANDLE_COL)
        return None

    def is_empty(self):
        """
        Returns True if the get_data returns a length greater than
        0. Typically, get_data returns the list of associated data.
        """
        return len(self.get_data()) == 0
    
    def get_data(self):
        """
        Returns the data associated with the list. This is typically
        a list of objects.

        This should be overridden in the derrived classes.
        """
        return []

    def column_order(self):
        """
        Specifies the column order for the columns. This should be
        in the format of a list of tuples, in the format of (int,int),
        where the first in indicates if the column is visible, and the
        second column indicates the index into the model.

        This should be overridden in the derrived classes.
        """
        return []

    def build_columns(self):
        """
        Builds the columns and inserts them into the TreeView. Any
        previous columns exist, they will be in the self.columns array,
        and removed. 
        """

        # remove any existing columns, which would be stored in
        # self.columns
        
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        # loop through the values returned by column_order
        
        for pair in self.column_order():

            # if the first value isn't 1, then we skip the values
            if not pair[0]:
                continue

            # extract the name from the _column_names variable, and
            # assign it to the column name. The text value is extracted
            # from the model column specified in pair[1]
            name = self._column_names[pair[1]][0]
            renderer = gtk.CellRendererText()
            renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
            column = gtk.TreeViewColumn(name, renderer, text=pair[1])

            # insert the colum into the tree
            column.set_resizable(True)
            column.set_min_width(self._column_names[pair[1]][2])
            column.set_sort_column_id(self._column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def rebuild(self):
        """
        Rebuilds the data in the database by creating a new model,
        using the build_model function passed at creation time.
        """
        self.model = self.build_model(self.get_data(),self.dbstate.db)
        self.tree.set_model(self.model)
        self._set_label()
        self._selection_changed()

#-------------------------------------------------------------------------
#
# EventEmbedList
#
#-------------------------------------------------------------------------
class EventEmbedList(EmbeddedList):

    _HANDLE_COL = 6
    _DND_TYPE   = DdTargets.EVENTREF
    _DND_EXTRA  = DdTargets.EVENT

    _MSG = {
        'add'   : _('Add a new event'),
        'del'   : _('Remove the selected event'),
        'edit'  : _('Edit the selected event'),
        'share' : _('Share an exisiting event'),
        }

    _column_names = [
        (_('Type'),0,100),
        (_('Description'),1,175),
        (_('ID'),2, 60),
        (_('Date'),3, 150),
        (_('Place'),4, 140),
        (_('Role'),5, 80),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Events'), EventRefModel, True)

    def get_icon_name(self):
        return 'gramps-event'

    def get_data(self):
        return self.obj.get_event_ref_list()

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4),(1,5))

    def handle_extra_type(self, objtype, obj):
        from Editors import EditEventRef
        try:
            ref = RelLib.EventRef()
            event = self.dbstate.db.get_event_from_handle(obj)
            if self.obj.__class__.__name__ == 'Person':
                event.set_type((RelLib.Event.BIRTH,''))
                ref.set_role((RelLib.EventRef.PRIMARY,''))
            else:
                event.set_type((RelLib.Event.MARRIAGE,''))
                ref.set_role((RelLib.EventRef.FAMILY,''))
            EditEventRef(self.dbstate,self.uistate,self.track,
                         event, ref, self.obj, self.event_added)
        except Errors.WindowActiveError:
            pass

    def add_button_clicked(self,obj):
        from Editors import EditEventRef
        try:
            ref = RelLib.EventRef()
            event = RelLib.Event()
            if self.obj.__class__.__name__ == 'Person':
                event.set_type((RelLib.Event.BIRTH,''))
                ref.set_role((RelLib.EventRef.PRIMARY,''))
            else:
                event.set_type((RelLib.Event.MARRIAGE,''))
                ref.set_role((RelLib.EventRef.FAMILY,''))
            EditEventRef(self.dbstate,self.uistate,self.track,
                         event, ref, self.obj, self.event_added)
        except Errors.WindowActiveError:
            pass

    def share_button_clicked(self,obj):
        from Editors import EditEventRef
        import SelectEvent

        sel = SelectEvent.SelectEvent(self.dbstate.db,"Event Select")
        event = sel.run()
        if event:
            try:
                ref = RelLib.EventRef()
                if self.obj.__class__.__name__ == 'Person':
                    ref.set_role((RelLib.EventRef.PRIMARY,''))
                else:
                    ref.set_role((RelLib.EventRef.FAMILY,''))
                EditEventRef(self.dbstate,self.uistate,self.track,
                             event, ref, self.obj, self.event_added)
            except Errors.WindowActiveError:
                pass

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            from Editors import EditEventRef
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            try:
                EditEventRef(self.dbstate,self.uistate,self.track,
                             event, ref, self.obj, self.event_updated)
            except Errors.WindowActiveError:
                pass

    def event_updated(self,ref,event):
        self.changed = True
        self.rebuild()

    def event_added(self,ref,event):
        ref.ref = event.handle
        self.get_data().append(ref)
        self.changed = True
        self.rebuild()

class PersonEventEmbedList(EventEmbedList):

    def __init__(self,dbstate,uistate,track,obj):        
        self.orig_data = [ data for data in [ obj.get_birth_ref(), \
                                              obj.get_death_ref()] + \
                            obj.get_event_ref_list() \
                            if data ]
        EventEmbedList.__init__(self, dbstate, uistate, track, obj)

    def get_data(self):
        return self.orig_data

    def return_info(self):
        new_list = []
        birth_ref = None
        death_ref = None
        
        for ref in self.orig_data:
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            if birth_ref == None and event.get_type()[0] == RelLib.Event.BIRTH:
                birth_ref = ref
            elif death_ref == None and event.get_type()[0] == RelLib.Event.DEATH:
                death_ref = ref
            else:
                new_list.append(ref)
        return (birth_ref, death_ref, new_list)
            
#-------------------------------------------------------------------------
#
# BackRefList
#
#-------------------------------------------------------------------------
class BackRefList(EmbeddedList):

    _HANDLE_COL = 3

    _column_names = [
        (_('Type'),0, 100),
        (_('ID'),  1,  75),
        (_('Name'),2, 250),
        ]
    
    def __init__(self,dbstate,uistate,track,obj,refmodel):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('References'), refmodel)
        self.model.connect('row-inserted',self.update_label)

    def update_label(self,*obj):
        if not self.model.empty:
            self._set_label()

    def close(self):
        self.model.close()

    def is_empty(self):
        return self.model.empty

    def create_buttons(self,share=False):
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)

        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.edit_btn,False)
        vbox.show_all()
        self.pack_start(vbox,False)

    def _selection_changed(self,obj=None):
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1,0),(1,1),(1,2))

    def find_node(self):
        (model,node) = self.selection.get_selected()
        try:
            return (model.get_value(node,0),model.get_value(node,3))
        except:
            return (None,None)
    
    def edit_button_clicked(self,obj):
        (reftype, ref) = self.find_node()
        if reftype == 'Person':
            try:
                from Editors import EditPerson
                
                person = self.dbstate.db.get_person_from_handle(ref)
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Family':
            try:
                from Editors import EditFamily
                
                family = self.dbstate.db.get_family_from_handle(ref)
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Source':
            try:
                from Editors import EditSource
                
                source = self.dbstate.db.get_source_from_handle(ref)
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Place':
            try:
                from Editors import EditPlace
                
                place = self.dbstate.db.get_place_from_handle(ref)
                EditPlace(self.dbstate,self.uistate,[],place)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Media':
            try:
                from Editors import EditMedia
                
                obj = self.dbstate.db.get_object_from_handle(ref)
                EditMedia(self.dbstate,self.uistate, [], obj)
            except Errors.WindowActiveError:
                pass

class SourceBackRefList(BackRefList):

    def __init__(self,dbstate,uistate,track,obj):
        BackRefList.__init__(self, dbstate, uistate, track, obj,
                             BackRefModel)

    def get_icon_name(self):
        return 'gramps-source'

class EventBackRefList(BackRefList):

    def __init__(self,dbstate,uistate,track,obj):
        BackRefList.__init__(self, dbstate, uistate, track, obj,
                             BackRefModel)

    def get_icon_name(self):
        return 'gramps-event'

class MediaBackRefList(BackRefList):

    def __init__(self,dbstate,uistate,track,obj):
        BackRefList.__init__(self, dbstate, uistate, track, obj,
                             BackRefModel)

    def get_icon_name(self):
        return 'gramps-media'

class PlaceBackRefList(BackRefList):

    def __init__(self,dbstate,uistate,track,obj):
        BackRefList.__init__(self, dbstate, uistate, track, obj,
                             BackRefModel)

    def get_icon_name(self):
        return 'gramps-place'


#-------------------------------------------------------------------------
#
# DataEmbedList
#
#-------------------------------------------------------------------------
class DataEmbedList(EmbeddedList):

    _DND_TYPE   = DdTargets.DATA
    _column_names = [
        (_('Key'),0,150),
        (_('Value'),1,250),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Data'), DataModel)

    def get_data(self):
        return self.obj.get_data_map()

    def column_order(self):
        return ((1,0),(1,1))

    def add_button_clicked(self,obj):
        pass

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.obj.get_data_map()
            ref_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            print ref

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class AttrEmbedList(EmbeddedList):

    _HANDLE_COL = 2
    _DND_TYPE   = DdTargets.ATTRIBUTE

    _column_names = [
        (_('Type'),0,250),
        (_('Value'),1,200),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Attributes'), AttrModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

    def add_button_clicked(self,obj):
        from Editors import EditAttribute
        pname = ''
        attr_list = []
        attr = RelLib.Attribute()
        try:
            EditAttribute(
                self.dbstate, self.uistate, self.track, attr,
                pname, attr_list, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,name):
        self.get_data().append(name)
        self.changed = True
        self.rebuild()

    def edit_button_clicked(self,obj):
        attr = self.get_selected()
        if attr:
            from Editors import EditAttribute
            pname = ''
            attr_list = []
            try:
                EditAttribute(
                    self.dbstate, self.uistate, self.track, attr,
                    pname, attr_list, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,name):
        self.changed = True
        self.rebuild()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class WebEmbedList(EmbeddedList):

    _HANDLE_COL = 3
    _DND_TYPE   = DdTargets.URL

    _column_names = [
        (_('Type')       ,0, 100),
        (_('Path')       ,1, 200),
        (_('Description'),2, 150),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Internet'), WebModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1),(1,2))

    def add_button_clicked(self,obj):
        from Editors import EditUrl
        url = RelLib.Url()
        try:
            EditUrl(self.dbstate, self.uistate, self.track,
                    '', url, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,url):
        self.get_data().append(url)
        self.rebuild()

    def edit_button_clicked(self,obj):
        url = self.get_selected()
        if url:
            from Editors import EditUrl
            try:
                EditUrl(self.dbstate, self.uistate, self.track,
                        '', url, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,url):
        self.rebuild()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class NameEmbedList(EmbeddedList):

    _HANDLE_COL = 2
    _DND_TYPE   = DdTargets.NAME

    _column_names = [
        (_('Name'),0, 250),
        (_('Type'),1, 100),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Names'), NameModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

    def add_button_clicked(self,obj):
        from Editors import EditName
        name = RelLib.Name()
        try:
            EditName(self.dbstate, self.uistate, self.track,
                     name, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,name):
        self.get_data().append(name)
        self.rebuild()

    def edit_button_clicked(self,obj):
        name = self.get_selected()
        if name:
            from Editors import EditName
            try:
                EditName(self.dbstate, self.uistate, self.track,
                         name, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,name):
        self.rebuild()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class AddrEmbedList(EmbeddedList):

    _HANDLE_COL = 5
    _DND_TYPE   = DdTargets.ADDRESS

    _column_names = [
        (_('Date'),    0, 150),
        (_('Street'),  1, 225),
        (_('State'),   2, 100),
        (_('City'),    3, 100),
        (_('Country'), 4, 75),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Addresses'), AddressModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4))

    def add_button_clicked(self,obj):
        from Editors import EditAddress
        addr = RelLib.Address()
        try:
            EditAddress(self.dbstate, self.uistate, self.track,
                        addr, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,name):
        self.get_data().append(name)
        self.rebuild()

    def edit_button_clicked(self,obj):
        addr = self.get_selected()
        if addr:
            from Editors import EditAddress
            try:
                EditAddress(self.dbstate, self.uistate, self.track,
                            addr, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,name):
        self.rebuild()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class LocationEmbedList(EmbeddedList):

    _HANDLE_COL = 5
    _DND_TYPE   = DdTargets.LOCATION

    _column_names = [
        (_('City'),           0, 150),
        (_('County'),         1, 100),
        (_('Church Parish'),  2, 100),
        (_('State/Province'), 3, 100),
        (_('Country'),        4, 75),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Alternate Locations'), LocationModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4))

    def add_button_clicked(self,obj):
        from Editors import EditLocation
        loc = RelLib.Location()
        try:
            EditLocation(self.dbstate, self.uistate, self.track,
                         loc, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,name):
        self.get_data().append(name)
        self.rebuild()

    def edit_button_clicked(self,obj):
        loc = self.get_selected()
        if loc:
            from Editors import EditLocation
            try:
                EditLocation(self.dbstate, self.uistate, self.track,
                             loc, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,name):
        self.rebuild()

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class NoteTab(GrampsTab):

    def __init__(self, dbstate, uistate, track, note_obj,title=_('Note')):
        self.note_obj = note_obj        
        GrampsTab.__init__(self, dbstate, uistate, track, title)
        self.show_all()

    def _update_label(self,*obj):
        cc = self.buf.get_char_count()
        if cc == 0 and not self.empty:
            self.empty = True
            self._set_label()
        elif cc != 0 and self.empty:
            self.empty = False
            self._set_label()

    def is_empty(self):
        """
        Indicates if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        return self.buf.get_char_count() == 0

    def build_interface(self):
        vbox = gtk.VBox()
        
        self.text = gtk.TextView()
        self.flowed = gtk.RadioButton(None,_('Flowed'))
        self.format = gtk.RadioButton(self.flowed,_('Formatted'))

        if self.note_obj and self.note_obj.get_format():
            self.format.set_active(True)
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.flowed.set_active(True)
            self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.spellcheck = Spell.Spell(self.text)

        self.flowed.connect('toggled',self.flow_changed)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.text)
        scroll.connect('focus-out-event',self.update)

        vbox.pack_start(scroll,True)
        vbox.set_spacing(6)

        hbox = gtk.HBox()
        hbox.set_spacing(6)
        hbox.pack_start(self.flowed,False)
        hbox.pack_start(self.format,False)

        vbox.pack_start(hbox,False)
        
        self.pack_start(vbox,True)
        self.buf = self.text.get_buffer()
        if self.note_obj:
            self.empty = False
            self.buf.insert_at_cursor(self.note_obj.get())
        else:
            self.empty = True
            
        self.buf.connect('changed',self.update)
        self.rebuild()

    def update(self,obj):
        if self.note_obj:
            start = self.buf.get_start_iter()
            stop = self.buf.get_end_iter()
            text = self.buf.get_text(start,stop)
            self.note_obj.set(text)
        else:
            print "NOTE OBJ DOES NOT EXIST"
        self._update_label(obj)
        return False

    def flow_changed(self,obj):
        if obj.get_active():
            self.text.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.text.set_wrap_mode(gtk.WRAP_NONE)

    def rebuild(self):
        self._set_label()

#-------------------------------------------------------------------------
#
# GalleryTab
#
#-------------------------------------------------------------------------
class GalleryTab(ButtonTab):

    def __init__(self, dbstate, uistate, track,  media_list):
        ButtonTab.__init__(self, dbstate, uistate, track, _('Gallery'))
        self.media_list = media_list
        self.rebuild()
        self.show_all()

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs,
        the Edit button handler is called
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.edit_button_clicked(obj)

    def get_icon_name(self):
        return 'gramps-media'

    def is_empty(self):
        return len(self.media_list)==0

    def _build_icon_model(self):
        # build the list model
        self.iconmodel= gtk.ListStore(gtk.gdk.Pixbuf,str,object)

    def _connect_icon_model(self):
        self.iconlist.set_model(self.iconmodel)
        self.iconmodel.connect_after('row-inserted',self._update_internal_list)
        self.iconmodel.connect_after('row-deleted',self._update_internal_list)

    def build_interface(self):

        self._build_icon_model()
        # build the icon view
        self.iconlist = gtk.IconView()
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_text_column(1)
        self.iconlist.set_margin(12)
        self.iconlist.set_reorderable(True)
        self.iconlist.set_item_width(125)
        self.iconlist.set_spacing(24)
        self.iconlist.set_selection_mode(gtk.SELECTION_SINGLE)
        self.iconlist.connect('selection-changed',self._selection_changed)
        self.iconlist.connect('button_press_event',self.double_click)
        self._connect_icon_model()
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.iconlist)
        self.pack_start(scroll,True)

    def _update_internal_list(self, *obj):
        node = self.iconmodel.get_iter_first()
        newlist = []
        while node != None:
            newlist.append(self.iconmodel.get_value(node,2))
            node = self.iconmodel.iter_next(node)
        for i in xrange(len(self.media_list)):
            self.media_list.pop()
        for i in newlist:
            self.media_list.append(i)
        self.changed = True

    def get_data(self):
        return self.media_list

    def rebuild(self):
        self._build_icon_model()
        for ref in self.media_list:
            handle = ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(handle)
            pixbuf = ImgManip.get_thumb_from_obj(obj)
            self.iconmodel.append(row=[pixbuf,obj.get_description(),ref])
        self._connect_icon_model()
        self._set_label()
        self._selection_changed()
        
    def get_selected(self):
        node = self.iconlist.get_selected_items()
        if len(node) > 0:
            return self.media_list[node[0][0]]
        return None

    def add_button_clicked(self,obj):
        from Editors import EditMediaRef
        
        sref = RelLib.MediaRef()
        src = RelLib.MediaObject()
        try:
            EditMediaRef(self.dbstate, self.uistate, self.track,
                         src, sref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,media_ref, media):
        self.get_data().append(media_ref)
        self.changed = True
        self.rebuild()

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            self.media_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            from Editors import EditMediaRef

            obj = self.dbstate.db.get_object_from_handle(ref.get_reference_handle())
            try:
                EditMediaRef(self.dbstate, self.uistate, self.track,
                             obj, ref, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, media_ref, ref):
        self.changed = True
        self.rebuild()

#-------------------------------------------------------------------------
#
# SourceEmbedList
#
#-------------------------------------------------------------------------
class SourceEmbedList(EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.SOURCEREF
    _DND_EXTRA = DdTargets.SOURCE_LINK
        
    _column_names = [
        (_('ID'),     0, 75),
        (_('Title'),  1, 200),
        (_('Author'), 2, 125),
        (_('Page'),   3, 100),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Sources'), SourceRefModel, True)

    def get_icon_name(self):
        return 'gramps-event'

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3))

    def add_button_clicked(self,obj):
        from Editors import EditSourceRef
        
        sref = RelLib.SourceRef()
        src = RelLib.Source()
        try:
            EditSourceRef(self.dbstate, self.uistate, self.track,
                          src, sref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def share_button_clicked(self,obj):
        from Editors import EditSourceRef
        import SelectSource

        sel = SelectSource.SelectSource(self.dbstate.db,"Source Select")
        src = sel.run()
        sref = RelLib.SourceRef()
        if src:
            try:
                ref = RelLib.SourceRef()
                EditSourceRef(self.dbstate,self.uistate,self.track,
                              src, sref, self.add_callback)
            except Errors.WindowActiveError:
                pass

    def add_callback(self,reference, primary):
        reference.ref = primary.handle
        self.get_data().append(reference)
        self.changed = True
        self.rebuild()

    def edit_button_clicked(self,obj):
        from Editors import EditSourceRef

        sref = self.get_selected()
        src = self.dbstate.db.get_source_from_handle(sref.ref)
        if sref:
            try:
                EditSourceRef(self.dbstate, self.uistate, self.track,
                              src, sref, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,refererence,primary):
        self.changed = True
        self.rebuild()

    def handle_extra_type(self, objtype, obj):
        from Editors import EditSourceRef
        
        sref = RelLib.SourceRef()
        src = self.dbstate.db.get_source_from_handle(obj)
        try:
            EditSourceRef(self.dbstate, self.uistate, self.track,
                          src, sref, self.add_callback)
        except Errors.WindowActiveError:
            pass


#-------------------------------------------------------------------------
#
# RepoEmbedList
#
#-------------------------------------------------------------------------
class RepoEmbedList(EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.REPOREF
    _DND_EXTRA = DdTargets.REPO_LINK
        
    _column_names = [
        (_('ID'),     0, 75),
        (_('Title'),  1, 200),
        (_('Call Number'), 2, 125),
        (_('Type'),   3, 100),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Repositories'), RepoRefModel)

    def get_icon_name(self):
        return 'gramps-repository'

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3))

    def handle_extra_type(self, objtype, obj):
        from Editors import EditRepoRef
        try:
            ref = RelLib.RepoRef()
            repo = self.dbstate.db.get_repository_from_handle(obj)
            EditRepoRef(
                self.dbstate,self.uistate,self.track,
                repo, ref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_button_clicked(self,obj):
        from Editors import EditRepoRef
        
        ref = RelLib.RepoRef()
        repo = RelLib.Repository()
        try:
            EditRepoRef(
                self.dbstate, self.uistate, self.track,
                repo, ref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self,value):
        value[0].ref = value[1].handle
        self.get_data().append(value[0])
        self.changed = True
        self.rebuild()

    def edit_button_clicked(self,obj):
        from Editors import EditRepoRef

        ref = self.get_selected()
        if ref:
            repo = self.dbstate.db.get_repository_from_handle(ref.ref)
            try:
                EditRepoRef(
                    self.dbstate, self.uistate, self.track, repo,
                    ref, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self,name):
        self.changed = True
        self.rebuild()

#-------------------------------------------------------------------------
#
# ChildModel
#
#-------------------------------------------------------------------------
class ChildModel(gtk.ListStore):

    _HANDLE_COL = -8
    
    def __init__(self, family, db):
        self.family = family
        gtk.ListStore.__init__(self,int,str,str,str,str,str,
                               str,str,str,str,str,str,int,int)
        self.db = db
        index = 1
        for child_handle in self.get_data():
            child = db.get_person_from_handle(child_handle)
            self.append(row=[index,
                             child.get_gramps_id(),
                             NameDisplay.displayer.display(child),
                             Utils.gender[child.get_gender()],
                             self.column_father_rel(child),
                             self.column_mother_rel(child),
                             self.column_birth_day(child),
                             self.column_death_day(child),
                             self.column_birth_place(child),
                             self.column_death_place(child),
                             child.get_handle(),
                             NameDisplay.displayer.sort_string(child.primary_name),
                             self.column_birth_sort(child),
                             self.column_death_sort(child),
                             ])
            index += 1

    def get_data(self):
        return self.family.get_child_handle_list()

    def column_father_rel(self,data):
        fhandle = self.family.handle
        for (handle, mrel, frel) in data.get_parent_family_handle_list():
            if handle == fhandle:
                return Utils.format_child_relation(frel)
        return ""

    def column_mother_rel(self,data):
        fhandle = self.family.handle
        for (handle, mrel, frel) in data.get_parent_family_handle_list():
            if handle == fhandle:
                return Utils.format_child_relation(mrel)
        return ""

    def column_birth_day(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_birth_sort(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0

    def column_death_day(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_death_sort(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0
        
    def column_birth_place(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

#-------------------------------------------------------------------------
#
# EventRefModel
#
#-------------------------------------------------------------------------
class EventRefModel(gtk.ListStore):

    def __init__(self,event_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,str,str,object)
        self.db = db
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            self.append(row=[
                self.column_type(event),
                event.get_description(),
                event.get_gramps_id(),
                self.column_date(event_ref),
                self.column_place(event_ref),
                self.column_role(event_ref),
                event_ref
                ])

    def column_type(self,event):
        return Utils.format_event(event.get_type())

    def column_role(self,event_ref):
        return Utils.format_event_role(event_ref.get_role())

    def column_date(self,event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        return DateHandler.get_date(event)

    def column_place(self,event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

#-------------------------------------------------------------------------
#
# AttrModel
#
#-------------------------------------------------------------------------
class AttrModel(gtk.ListStore):

    def __init__(self,attr_list,db):
        gtk.ListStore.__init__(self,str,str,object)
        self.db = db
        for attr in attr_list:
            self.append(row=[
                self.type_name(attr),
                attr.get_value(),
                attr,
                ])

    def type_name(self, attr):
        return Utils.format_attribute( attr.get_type())

#-------------------------------------------------------------------------
#
# NameModel
#
#-------------------------------------------------------------------------
class NameModel(gtk.ListStore):

    def __init__(self,obj_list,db):
        gtk.ListStore.__init__(self,str,str,object)
        self.db = db
        for obj in obj_list:
            self.append(row=[
                NameDisplay.displayer.display_name(obj),
                self.type_name(obj),
                obj,
                ])

    def type_name(self, obj):
        return Utils.format_name_type(obj.get_type())

#-------------------------------------------------------------------------
#
# AddressModel
#
#-------------------------------------------------------------------------
class AddressModel(gtk.ListStore):

    def __init__(self,obj_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,str,object)
        self.db = db
        for obj in obj_list:
            self.append(row=[
                DateHandler.get_date(obj),
                obj.street,
                obj.city,
                obj.state,
                obj.country,
                obj,
                ])

#-------------------------------------------------------------------------
#
# LocationModel
#
#-------------------------------------------------------------------------
class LocationModel(gtk.ListStore):

    def __init__(self,obj_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,str,object)
        self.db = db
        for obj in obj_list:
            self.append(row=[obj.city, obj.county, obj.parish,
                             obj.state, obj.country, obj, ])

#-------------------------------------------------------------------------
#
# AddressModel
#
#-------------------------------------------------------------------------
class WebModel(gtk.ListStore):

    def __init__(self,obj_list,db):
        gtk.ListStore.__init__(self,str,str,str,object)
        self.db = db
        for obj in obj_list:
            self.append(row=[self.show_type(obj.type),
                             obj.path, obj.desc, obj])

    def show_type(self,rtype):
        return Utils.format_web_type(rtype)

#-------------------------------------------------------------------------
#
# DataModel
#
#-------------------------------------------------------------------------
class DataModel(gtk.ListStore):

    def __init__(self,attr_list,db):
        gtk.ListStore.__init__(self,str,str)
        self.db = db
        for attr in attr_list.keys():
            self.append(row=[attr, attr_list[attr] ])

#-------------------------------------------------------------------------
#
# SourceRefModel
#
#-------------------------------------------------------------------------
class SourceRefModel(gtk.ListStore):

    def __init__(self,sref_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,object)
        self.db = db
        for sref in sref_list:
            src = self.db.get_source_from_handle(sref.ref)
            self.append(row=[src.gramps_id, src.title, src.author,
                             sref.page, sref, ])

#-------------------------------------------------------------------------
#
# RepoRefModel
#
#-------------------------------------------------------------------------
class RepoRefModel(gtk.ListStore):

    def __init__(self,ref_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,object)
        self.db = db
        for ref in ref_list:
            repo = self.db.get_repository_from_handle(ref.ref)
            self.append(row=[repo.gramps_id, repo.name, ref.call_number,
                             self.type_of(repo), ref,])

    def type_of(self,ref):
        return Utils.format_source_media_type(ref.get_type())

#-------------------------------------------------------------------------
#
# BackRefModel
#
#-------------------------------------------------------------------------
class BackRefModel(gtk.ListStore):

    def __init__(self,sref_list,db):
        gtk.ListStore.__init__(self,str,str,str,str)
        self.db = db
        self.sref_list = sref_list
        self.idle = 0
        self.empty = True
        self.idle = gobject.idle_add(self.load_model().next)

    def close(self):
        gobject.source_remove(self.idle)

    def load_model(self):
        self.empty = True
        for ref in self.sref_list:
            self.empty = False
            dtype = ref[0]
            if dtype == 'Person':
                p = self.db.get_person_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = NameDisplay.displayer.display(p)
            elif dtype == 'Family':
                p = self.db.get_family_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = Utils.family_name(p,self.db)
            elif dtype == 'Source':
                p = self.db.get_source_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = p.get_title()
            elif dtype == 'Event':
                p = self.db.get_event_from_handle(ref[1])
                gid = p.gramps_id
                name = p.get_description()
                handle = p.handle
                if not name:
                    etype = p.get_type()
                    if etype[0] == RelLib.Event.CUSTOM:
                        name = etype[1]
                    elif Utils.personal_events.has_key(etype[0]):
                        name = Utils.personal_events[etype[0]]
                    else:
                        name = Utils.family_events[etype[0]]
            elif dtype == 'Place':
                p = self.db.get_place_from_handle(ref[1])
                name = p.get_title()
                gid = p.gramps_id
                handle = p.handle
            else:
                p = self.db.get_object_from_handle(ref[1])
                name = p.get_description()
                gid = p.gramps_id
                handle = p.handle

            self.append(row=[dtype,gid,name,handle])
            yield True
        yield False
