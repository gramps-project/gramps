#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# python
#
#-------------------------------------------------------------------------

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
import DateHandler
import NameDisplay
import RelLib
import Utils
import GrampsMime
import const

from GrampsWidgets import SimpleButton

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

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
        hbox.set_spacing(3)
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

    def __init__(self,dbstate,uistate,track,name):
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
        self.create_buttons()

    def create_buttons(self):
        """
        Creates a button box consisting of three buttons, one for Add,
        one for Edit, and one for Delete. This button box is then appended
        hbox (self).
        """
        self.add_btn  = SimpleButton(gtk.STOCK_ADD, self.add_button_clicked)
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)
        self.del_btn  = SimpleButton(gtk.STOCK_REMOVE, self.del_button_clicked)

        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.add_btn,False)
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

class EmbeddedList(ButtonTab):
    """
    This class provides the base class for all the list tabs. It
    maintains a gtk.TreeView, including the selection and button
    sensitivity.
    """
    
    _HANDLE_COL = -1
    
    def __init__(self, dbstate, uistate, track, name, build_model):
        """
        Creates a new list, using the passed build_model to
        populate the list.
        """
        ButtonTab.__init__(self, dbstate, uistate, track, name)
        self.build_model = build_model

        # handle the selection
        self.selection = self.tree.get_selection()
        self.selection.connect('changed',self._selection_changed)

        # build the columns
        self.columns = []
        self.build_columns()

        # build the initial data
        self.rebuild()
        self.show_all()

    def get_icon_name(self):
        """
        Specifies the basic icon used for a generic list. Typically,
        a derived class will override this. The icon chose is the
        STOCK_JUSTIFY_FILL icon, which in the default GTK style
        looks kind of like a list.
        """
        return gtk.STOCK_JUSTIFY_FILL

    def build_interface(self):
        """
        Builds the interface, instantiating a gtk.TreeView in a
        gtk.ScrolledWindow.
        """

        # create the tree, turn on rule hinting and connect the
        # button press to the double click function.
        
        self.tree = gtk.TreeView()
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
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(),
                                        text=pair[1])

            # insert the colum into the tree
            column.set_resizable(True)
            column.set_min_width(75)
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

    _column_names = [
        (_('Type'),0),
        (_('Description'),1),
        (_('ID'),2),
        (_('Date'),3),
        (_('Place'),4),
        (_('Cause'),5),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        self.changed = False
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Events'), EventRefModel)

    def get_icon_name(self):
        return 'gramps-event'

    def get_data(self):
        return self.obj.get_event_ref_list()

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4),(1,5))

    def add_button_clicked(self,obj):
        import EventEdit
        ref = RelLib.EventRef()
        EventEdit.EventRefEditor(self.dbstate,self.uistate,self.track,
                                 None, ref, self.obj, self.event_added)

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.obj.get_event_ref_list()
            ref_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            import EventEdit
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            EventEdit.EventRefEditor(self.dbstate,self.uistate,self.track,
                                     event, ref, self.obj, self.event_updated)

    def event_updated(self,value):
        self.changed = True
        print value
        self.rebuild()

    def event_added(self,value):
        self.changed = True
        self.rebuild()
                                     
#-------------------------------------------------------------------------
#
# SourceBackRefList
#
#-------------------------------------------------------------------------
class SourceBackRefList(EmbeddedList):

    _HANDLE_COL = 3

    _column_names = [
        (_('Type'),0),
        (_('ID'),1),
        (_('Name'),2),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('References'), SourceBackRefModel)

    def close(self):
        self.model.close()

    def _set_label(self):
        self.tab_image.show()
        self.label.set_text("<b>%s</b>" % self.tab_name)
        self.label.set_use_markup(True)

    def create_buttons(self):
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

    def get_icon_name(self):
        return 'gramps-source'

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1,0),(1,1),(1,2))

    def add_button_clicked(self,obj):
        pass

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.obj.get_event_ref_list()
            ref_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            print ref

#-------------------------------------------------------------------------
#
# DataEmbedList
#
#-------------------------------------------------------------------------
class DataEmbedList(EmbeddedList):

    _column_names = [
        (_('Key'),0),
        (_('Value'),1),
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

    _column_names = [
        (_('Type'),0),
        (_('Value'),1),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Attributes'), AttrModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class WebEmbedList(EmbeddedList):

    _HANDLE_COL = -1

    _column_names = [
        (_('Type'),0),
        (_('Path'),1),
        (_('Description'),2),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Internet'), WebModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1),(1,2))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class NameEmbedList(EmbeddedList):

    _HANDLE_COL = -1

    _column_names = [
        (_('Name'),0),
        (_('Type'),1),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Names'), NameModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class AddrEmbedList(EmbeddedList):

    _HANDLE_COL = -1

    _column_names = [
        (_('Date'),0),
        (_('Street'),1),
        (_('State'),2),
        (_('City'),3),
        (_('Country'),4),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Addresses'), AddressModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4))

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class NoteTab(GrampsTab):

    def __init__(self, dbstate, uistate, track, note_obj):
        self.note_obj = note_obj        
        GrampsTab.__init__(self, dbstate, uistate, track, _('Note'))
        self.show_all()

    def is_empty(self):
        """
        Indicates if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        buf = self.text.get_buffer()
        return len(buf.get_text(buf.get_start_iter(),buf.get_end_iter())) == 0

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

        self.flowed.connect('toggled',self.flow_changed)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.text)

        vbox.pack_start(scroll,True)
        vbox.set_spacing(6)

        hbox = gtk.HBox()
        hbox.set_spacing(6)
        hbox.pack_start(self.flowed,False)
        hbox.pack_start(self.format,False)

        vbox.pack_start(hbox,False)
        
        self.pack_start(vbox,True)
        if self.note_obj:
            self.text.get_buffer().insert_at_cursor(self.note_obj.get())
        self.rebuild()

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

    def get_icon_name(self):
        return 'gramps-media'

    def build_interface(self):
        self.iconmodel= gtk.ListStore(gtk.gdk.Pixbuf,str)
        self.iconlist = gtk.IconView()
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_text_column(1)
        self.iconlist.set_model(self.iconmodel)
        self.iconlist.set_selection_mode(gtk.SELECTION_SINGLE)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.iconlist)
        self.pack_start(scroll,True)

    def get_data(self):
        return self.media_list

    def rebuild(self):
        self.iconmodel= gtk.ListStore(gtk.gdk.Pixbuf,str)
        for ref in self.media_list:
            handle = ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(handle)
            pixbuf = self.get_image(obj)
            self.iconmodel.append(row=[pixbuf,obj.get_description()])
        self.iconlist.set_model(self.iconmodel)
        self._set_label()

    def get_image(self,obj):
        import ImgManip
        
        mtype = obj.get_mime_type()
        if mtype[0:5] == "image":
            image = ImgManip.get_thumbnail_image(obj.get_path())
        else:
            image = GrampsMime.find_mime_type_pixbuf(mtype)
        if not image:
            image = gtk.gdk.pixbuf_new_from_file(const.icon)
        return image

    def get_selected(self):
        node = self.iconlist.get_selected_items()
        if len(node) > 0:
            return self.media_list[node[0][0]]
        return None

    def add_button_clicked(self,obj):
        print "Media Add clicked"

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            self.media_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        print "Media Edit clicked"

#-------------------------------------------------------------------------
#
# SourceEmbedList
#
#-------------------------------------------------------------------------
class SourceEmbedList(EmbeddedList):

    _HANDLE_COL = 4

    _column_names = [
        (_('ID'),0),
        (_('Title'),1),
        (_('Author'),2),
        (_('Page'),3),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Sources'), SourceRefModel)

    def get_icon_name(self):
        return 'gramps-event'

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3))

    def add_button_clicked(self,obj):
        pass

    def del_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.obj.get_event_ref_list()
            ref_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self,obj):
        ref = self.get_selected()
        if ref:
            print ref

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
                             _GENDER[child.get_gender()],
                             self.column_father_rel(child),
                             self.column_mother_rel(child),
                             self.column_birth_day(child),
                             self.column_death_day(child),
                             self.column_birth_place(child),
                             self.column_death_place(child),
                             child.get_handle(),
                             child.get_primary_name().get_sort_name(),
                             self.column_birth_sort(child),
                             self.column_death_sort(child),
                             ])
            index += 1

    def get_data(self):
        return self.family.get_child_handle_list()

    def display_rel(self,rtype):
        if type(rtype) == tuple:
            rel = rtype[0]
            val = rtype[1]
        else:
            rel = rtype
            val = "???"
            
        if rel == RelLib.Family.CUSTOM:
            return unicode(val)
        else:
            return Utils.child_relations[rel]

    def column_father_rel(self,data):
        fhandle = self.family.handle
        for (handle, mrel, frel) in data.get_parent_family_handle_list():
            if handle == fhandle:
                return self.display_rel(frel)
        return ""

    def column_mother_rel(self,data):
        fhandle = self.family.handle
        for (handle, mrel, frel) in data.get_parent_family_handle_list():
            if handle == fhandle:
                return self.display_rel(mrel)
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
                event.get_cause(),
                event_ref
                ])

    def column_type(self,event):
        t,v = event.get_type()
        if t == RelLib.Event.CUSTOM:
            return v
        else:
            if Utils.personal_events.has_key(t):
                return Utils.personal_events[t]
            else:
                return Utils.family_events[t]

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
        t,v = attr.get_type()
        if t == RelLib.Attribute.CUSTOM:
            return v
        elif Utils.personal_attributes.has_key(t):
            return Utils.personal_attributes[t]
        else:
            return Utils.family_attributes[t]

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
        t,v = obj.get_type()
        if t == RelLib.Name.CUSTOM:
            return v
        else:
            return Utils.name_types[t]

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
# AddressModel
#
#-------------------------------------------------------------------------
class WebModel(gtk.ListStore):

    def __init__(self,obj_list,db):
        gtk.ListStore.__init__(self,str,str,str,object)
        self.db = db
        for obj in obj_list:
            self.append(row=[obj.type, obj.path, obj.desc, obj])

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
# DataModel
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
# SourceBacRefModel
#
#-------------------------------------------------------------------------
class SourceBackRefModel(gtk.ListStore):

    def __init__(self,sref_list,db):
        gtk.ListStore.__init__(self,str,str,str,str)
        self.db = db
        self.sref_list = sref_list
        self.idle = 0
        self.idle = gobject.idle_add(self.load_model().next)

    def close(self):
        gobject.source_remove(self.idle)

    def load_model(self):
        for ref in self.sref_list:
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
            
