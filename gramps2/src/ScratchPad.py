#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import cPickle as pickle
import os
from xml.sax.saxutils import escape
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import TreeTips
import DateHandler
import GrampsDisplay

from DdTargets import DdTargets


#-------------------------------------------------------------------------
#
# icons used in the object listing
#
#-------------------------------------------------------------------------

_stock_image = os.path.join(const.image_dir,'stock_link.png')
LINK_PIC = gtk.gdk.pixbuf_new_from_file(_stock_image)
BLANK_PIC = gtk.gdk.Pixbuf(0,0,8,1,1)

#-------------------------------------------------------------------------
#
# wrapper classes to provide object specific listing in the ListView
#
#-------------------------------------------------------------------------

class ScratchPadWrapper(object):

    def __init__(self,dbstate,obj):
        self.dbstate = dbstate
        self.database_changed(dbstate.db)
        self._db.connect('database-changed', self.database_changed)

        self._obj = obj
        self._type  = _("Unknown")
        self._title = ''
        self._value = ''

    def database_changed(self,db):
        self._db = db

    def get_type(self):
        return self._type

    def get_title(self):
        return self._title

    def get_value(self):
        return self._value

    def pack(self):
        return str(self._obj)

    def is_valid(self):
        return True

class ScratchPadGrampsTypeWrapper(ScratchPadWrapper):
        
    def __init__(self,dbstate,obj):
        ScratchPadWrapper.__init__(self,dbstate,obj)

        #unpack object
        exec 'unpack_data = %s' % self._obj
        exec 'o_type = "%s"' % unpack_data[0]
        self._obj = pickle.loads(unpack_data[2])
        self._pickle = obj

    def pack(self):
        return self._pickle

    def is_valid(self):
        valid_func_map = {'Person': self._db.get_person_from_handle,
                          'Family': self._db.get_family_from_handle,
                          'Event':  self._db.get_event_from_handle,
                          'Place': self._db.get_place_from_handle,
                          'MediaObject': self._db.get_object_from_handle,
                          'Source': self._db.get_source_from_handle}

        for (classname,handle) in self._obj.get_referenced_handles_recursively():
            if classname in valid_func_map.keys():
                if not valid_func_map[classname](handle):
                    return False
            
        return True


class ScratchPadAddress(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.ADDRESS]
    DRAG_TARGET  = DdTargets.ADDRESS
    ICON         = BLANK_PIC
    
    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Address")
        self._title = DateHandler.get_date(self._obj)
        self._value = "%s %s %s %s" % (self._obj.get_street(),self._obj.get_city(),
                                       self._obj.get_state(),self._obj.get_country())


    def tooltip(self):
        global escape
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Address"),
            _("Date"), escape(DateHandler.get_date(self._obj)),
            _("Location"),
            escape(self._obj.get_street()),
            escape(self._obj.get_city()),
            escape(self._obj.get_state()),
            escape(self._obj.get_country()),
            escape(self._obj.get_postal_code()),
            _("Telephone"), escape(self._obj.get_phone()))
    
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))
            
        return s

class ScratchPadEvent(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.EVENT]
    DRAG_TARGET  = DdTargets.EVENT
    ICON         = LINK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Event")
        self._title = const.display_pevent(self._obj.get_name())
        self._value = self._obj.get_description()


    def tooltip(self):
        global escape
        
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Event"),
            _("Type"),escape(const.display_pevent(self._obj.get_name())),
            _("Date"),escape(DateHander.get_date(self._obj)),
            _("Place"),escape(place_title(self._db,self._obj)),
            _("Cause"),escape(self._obj.get_cause()),
            _("Description"), escape(self._obj.get_description()))

        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

class ScratchPadFamilyEvent(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_EVENT]
    DRAG_TARGET  = DdTargets.FAMILY_EVENT
    ICON         = BLANK_PIC
    
    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Family Event")
        self._title = const.display_fevent(self._obj.get_name())
        self._value = self._obj.get_description()


    def tooltip(self):
        global escape
        
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Family Event"),
            _("Type"),escape(const.display_fevent(self._obj.get_name())),
            _("Date"),escape(DateHander.get_date(self._obj)),
            _("Place"),escape(place_title(self.db,self._obj)),
            _("Cause"),escape(self._obj.get_cause()),
            _("Description"), escape(self._obj.get_description()))

        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

class ScratchPadUrl(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.URL]
    DRAG_TARGET  = DdTargets.URL
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Url")
        self._title = self._obj.get_path()
        self._value = self._obj.get_description()


    def tooltip(self):
        global escape
        return "<big><b>%s</b></big>\n\n"\
               "\t<b>%s:</b>\t%s\n"\
               "\t<b>%s:</b>\t%s" % (_("Url"),
                                     _("Path"),
                                     escape(self._obj.get_path()),
                                     _("Description"),
                                     escape(self._obj.get_description()))

class ScratchPadAttribute(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.ATTRIBUTE]
    DRAG_TARGET  = DdTargets.ATTRIBUTE
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Attribute")
        self._title = const.display_pattr(self._obj.get_type())
        self._value = self._obj.get_value()

    def tooltip(self):
        global escape
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (_("Attribute"),
                                  _("Type"),
                                  escape(const.display_pattr(self._obj.get_type())),
                                  _("Value"),
                                  escape(self._obj.get_value()))
        
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))

        return s

class ScratchPadFamilyAttribute(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_ATTRIBUTE]
    DRAG_TARGET  = DdTargets.FAMILY_ATTRIBUTE
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Family Attribute")
        self._title = const.display_fattr(self._obj.get_type())
        self._value = self._obj.get_value()

    def tooltip(self):
        global escape
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (_("Family Attribute"),
                                  _("Type"),
                                  escape(const.display_fattr(self._obj.get_type())),
                                  _("Value"),
                                  escape(self._obj.get_value()))
        
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))

        return s

class ScratchPadSourceRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.SOURCEREF]
    DRAG_TARGET  = DdTargets.SOURCEREF
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("SourceRef")

        base = self._db.get_source_from_handle(self._obj.get_base_handle())
        self._title = base.get_title()
        self._value = self._obj.get_text(),

    def tooltip(self):
        global escape
        base = self._db.get_source_from_handle(self._obj.get_base_handle())
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (
            _("SourceRef"),
            _("Title"),escape(base.get_title()),
            _("Page"), escape(self._obj.get_page()),
            _("Text"), escape(self._obj.get_text()),
            _("Comment"), escape(self._obj.get_note()))

        return s

class ScratchPadName(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.NAME]
    DRAG_TARGET  = DdTargets.NAME
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate,obj)
        self._type  = _("Name")
        self._title = self._obj.get_name()
        self._value = self._obj.get_type()


    def tooltip(self):
        global escape
        
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Name"),
            _("Name"),escape(self._obj.get_name()),
            _("Type"),escape(self._obj.get_type()))

        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

class ScratchPadText(ScratchPadWrapper):

    DROP_TARGETS = DdTargets.all_text()
    DRAG_TARGET  = DdTargets.TEXT
    ICON         = BLANK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadWrapper.__init__(self,dbstate,obj)
        self._type  = _("Text")

        self._title = ""
        self._value = self._obj

    def tooltip(self):
        global escape
        return "<big><b>%s</b></big>\n"\
               "%s" % (_("Text"),
                       escape(self._obj))

class ScratchMediaObj(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.MEDIAOBJ]
    DRAG_TARGET  = DdTargets.MEDIAOBJ
    ICON         = LINK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadWrapper.__init__(self,dbstate,obj)
        self._type  = _("Media Object")

        self._title = ""
        self._value = ""

    def tooltip(self):
        global escape
        return "<big><b>%s</b></big>\n"\
               "%s" % (_("Media Object"),
                       escape(self._obj))

class ScratchPersonLink(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.PERSON_LINK]
    DRAG_TARGET  = DdTargets.PERSON_LINK
    ICON         = LINK_PIC

    def __init__(self,dbstate,obj):
        ScratchPadWrapper.__init__(self,dbstate,obj)
        self._type  = _("Person Link")

        person = self._db.get_person_from_handle(self._obj)
        self._title = person.get_primary_name().get_name()
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self._db.get_event_from_handle(birth_handle)
            date_str = DateHandler.get_date(birth)
            if date_str != "":
                self._value = escape(date_str)


    def tooltip(self):
        global escape

        person = self._db.get_person_from_handle(self._obj)

        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Person Link"),
            _("Name"),escape(self._title),
            _("Birth"),escape(self._value))

        if len(person.get_source_references()) > 0:
            psrc_ref = person.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

#-------------------------------------------------------------------------
#
# Wrapper classes to deal with lists of objects
#
#-------------------------------------------------------------------------

class ScratchDropList(object):

    def __init__(self,model,obj_list):
        self._model = model
        self._obj_list = pickle.loads(obj_list)

    def get_objects(self):
        return [self._cls(self._model,obj) for obj in self._obj_list]

class ScratchPersonLinkList(ScratchDropList):

    DROP_TARGETS = [DdTargets.PERSON_LINK_LIST]
    DRAG_TARGET  = None

    def __init__(self,model,obj_list):
        ScratchDropList.__init__(self,model,obj_list)
        self._cls = ScratchPersonLink
    


#-------------------------------------------------------------------------
#
# ScratchPadListModel class
#
#-------------------------------------------------------------------------
class ScratchPadListModel(gtk.ListStore):

    def __init__(self):
        gtk.ListStore.__init__(self,
                               str,    # object type
                               object, # object
                               object  # tooltip callback
                               )


#-------------------------------------------------------------------------
#
# ScratchPadListView class
#
#-------------------------------------------------------------------------
class ScratchPadListView:

    LOCAL_DRAG_TARGET = ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0)
    LOCAL_DRAG_TYPE   = 'MY_TREE_MODEL_ROW'
    
    def __init__(self, db, widget):
        
        self.database_changed(db)
        self._db.connect('database-changed', self.database_changed)

        db_signals = (
            'person-update',
            'person-delete',
            'person-rebuild',
            'family-update',
            'family-delete',
            'family-rebuild',
            'source-update',
            'source-delete',
            'source-rebuild',
            'place-update',
            'place-delete',
            'place-rebuild',
            'media-update',
            'media-delete',
            'media-rebuild'
            )

        for signal in db_signals:
            self._db.connect(signal,self.remove_invalid_objects)
            
        self._widget = widget

        self._target_type_to_wrapper_class_map = {}
        self._previous_drop_time = 0

        self.otitles = [(_('Type'),-1,150),
                        (_('Title'),-1,150),
                        (_('Value'),-1,150),
                        ('',-1,0)] # To hold the tooltip text

        # Create the tree columns
        self._col1 = gtk.TreeViewColumn(_("Type"))
        self._col2 = gtk.TreeViewColumn(_("Title"))
        self._col3 = gtk.TreeViewColumn(_("Value"))

        # Add columns
        self._widget.append_column(self._col1)
        self._widget.append_column(self._col2)
        self._widget.append_column(self._col3)

        # Create cell renders
        self._col1_cellpb = gtk.CellRendererPixbuf()
        self._col1_cell = gtk.CellRendererText()
        self._col2_cell = gtk.CellRendererText()
        self._col3_cell = gtk.CellRendererText()

        # Add cells to view
        self._col1.pack_start(self._col1_cellpb, False)
        self._col1.pack_start(self._col1_cell, True)
        self._col2.pack_start(self._col2_cell, True)
        self._col3.pack_start(self._col3_cell, True)

        # Setup the cell data callback funcs
        self._col1.set_cell_data_func(self._col1_cellpb, self.object_pixbuf)
        self._col1.set_cell_data_func(self._col1_cell, self.object_type)
        self._col2.set_cell_data_func(self._col2_cell, self.object_title)
        self._col3.set_cell_data_func(self._col3_cell, self.object_value)                        
        
        self.treetips = TreeTips.TreeTips(self._widget,2,True)

	# Set the column that inline searching will use.
        # The search does not appear to work properly so I am disabling it for now.
        self._widget.set_enable_search(False)
        #self._widget.set_search_column(1)

        self._widget.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                   (ScratchPadListView.LOCAL_DRAG_TARGET,) + \
                                   DdTargets.all_targets(),
                                   ACTION_COPY)

        self._widget.connect('drag_data_get', self.object_drag_data_get)
        self._widget.connect('drag_begin', self.object_drag_begin)
        self._widget.connect('drag_data_received',
                             self.object_drag_data_received)

        self.register_wrapper_classes()

    def database_changed(self,db):
        self._db = db

    def remove_invalid_objects(self,dummy=None):
        model = self._widget.get_model()

        for o in model:
            if not o.is_valid():
                model.remove(o)
    
    # Method to manage the wrapper classes.
    
    def register_wrapper_classes(self):
        self.register_wrapper_class(ScratchPadAddress)
        self.register_wrapper_class(ScratchPadEvent)
        self.register_wrapper_class(ScratchPadFamilyEvent)
        self.register_wrapper_class(ScratchPadUrl)
        self.register_wrapper_class(ScratchPadAttribute)
        self.register_wrapper_class(ScratchPadFamilyAttribute)
        self.register_wrapper_class(ScratchPadSourceRef)
        self.register_wrapper_class(ScratchPadName)
        self.register_wrapper_class(ScratchPadText)
        self.register_wrapper_class(ScratchMediaObj)
        self.register_wrapper_class(ScratchPersonLink)
        self.register_wrapper_class(ScratchPersonLinkList)
        

    def register_wrapper_class(self,wrapper_class):
        for drop_target in wrapper_class.DROP_TARGETS:            
            self._target_type_to_wrapper_class_map[drop_target.drag_type] = wrapper_class


    # Methods for rendering the cells.
    
    def object_pixbuf(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 1)
        cell.set_property('pixbuf', o.__class__.ICON)
        
    def object_type(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 1)
        cell.set_property('text', o.get_type())
        
    def object_title(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 1)
        cell.set_property('text', o.get_title())

    
    def object_value(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 1)
        cell.set_property('text', o.get_value())


    # handlers for the drag and drop events.
    
    def on_object_select_row(self,obj):        
        tree_selection = self._widget.get_selection()
        model,iter = tree_selection.get_selected()

        self._widget.unset_rows_drag_source()

        if iter != None:
            o = model.get_value(iter,1)

            targets = [ScratchPadListView.LOCAL_DRAG_TARGET] + \
                      [target.target() for target in o.__class__.DROP_TARGETS]

            self._widget.enable_model_drag_source(BUTTON1_MASK, targets, ACTION_COPY)

    def object_drag_begin(self, context, a):
        return

    def object_drag_data_get(self, widget, context, sel_data, info, time):
        tree_selection = widget.get_selection()
        model,iter = tree_selection.get_selected()
        o = model.get_value(iter,1)
        
        sel_data.set(sel_data.target, 8, o.pack())

    def object_drag_data_received(self,widget,context,x,y,selection,info,time):

        # Ignore drops from the same widget.
        if ScratchPadListView.LOCAL_DRAG_TYPE in context.targets:            
            return

        model = widget.get_model()
        sel_data = selection.data

        # There is a strange bug that means that if there is a selection
        # in the list we get multiple drops of the same object. Luckily
        # the time values are the same so we can drop all but the first.
        if time == self._previous_drop_time:
            return 
        
        # Find a wrapper class
        possible_wrappers = [target for target in context.targets \
                             if target in self._target_type_to_wrapper_class_map.keys()]

        if len(possible_wrappers) == 0:
            # No wrapper for this class
            return

        # Just select the first match.
        wrapper_class = self._target_type_to_wrapper_class_map[str(possible_wrappers[0])]

        o = wrapper_class(self._db,sel_data)

        # If the wrapper object is a subclass of ScratchDropList then
        # the drag data was a list of objects and we need to decode
        # all of them.
        if isinstance(o,ScratchDropList):
            o_list = o.get_objects()
        else:
            o_list = [o]
            
        for o in o_list:
            drop_info = widget.get_dest_row_at_pos(x, y)
            if drop_info:
                path, position = drop_info
                iter = model.get_iter(path)
                if (position == gtk.TREE_VIEW_DROP_BEFORE
                    or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    model.insert_before(iter,[o.__class__.DRAG_TARGET.drag_type,o,o.tooltip])
                else:
                    model.insert_after(iter,[o.__class__.DRAG_TARGET.drag_type,o,o.tooltip])
            else:
                model.append([o.__class__.DRAG_TARGET.drag_type,o,o.tooltip])
            

        # remember time for double drop workaround.
        self._previous_drop_time = time


    # proxy methods to provide access to the real widget functions.
    
    def set_model(self,model=None):
        self._widget.set_model(model)
        self._widget.get_selection().connect('changed',self.on_object_select_row)

    def get_model(self):
        return self._widget.get_model()

    def get_selection(self):
        return self._widget.get_selection()

    def set_search_column(self,col):
        return self._widget.set_search_column(col)

#-------------------------------------------------------------------------
#
# ScatchPadWindow class
#
#-------------------------------------------------------------------------
class ScratchPadWindow:
    """
        The ScratchPad provides a temporary area to hold objects that can
        be reused accross multiple Person records. The pad provides a window
        onto which objects can be dropped and then dragged into new Person
        dialogs. The objects are stored as the pickles that are built by the
        origininating widget. The objects are only unpickled in order to
        provide the text in the display.

        No attempt is made to ensure that any references contained within
        the pickles are valid. Because the pad extends the life time of drag
        and drop objects, it is possible that references that were valid
        when an object is copied to the pad are invalid by the time they
        are dragged to a new Person. For this reason, using the pad places
        a responsibility on all '_drag_data_received' methods to check the
        references of objects before attempting to use them.
        """
    
    # Class attribute used to hold the content of the
    # ScratchPad. A class attribute is used so that the content
    # it preserved even when the ScratchPad window is closed.
    # As there is only ever one ScratchPad we do not need to
    # maintain a list of these.
    otree = None
    
    def __init__(self,database,parent):
        """Initializes the ScratchPad class, and displays the window"""

        self.parent = parent

        self.database_changed(database)
        self.db.connect('database-changed', self.database_changed)

        self.glade_file = os.path.join(const.glade_dir,"scratchpad.glade")

        self.top = gtk.glade.XML(self.glade_file,"scratch_pad","gramps")
        self.window = self.top.get_widget("scratch_pad")

        self.window.set_icon_from_file(const.icon)
        self.clear_all_btn = self.top.get_widget("btn_clear_all")
        self.clear_btn = self.top.get_widget("btn_clear")
        
        self.object_list = ScratchPadListView(self.db,self.top.get_widget('objectlist'))
        self.object_list.get_selection().connect('changed',self.set_clear_btn_sensitivity)
        self.set_clear_btn_sensitivity(sel=self.object_list.get_selection())
        
        if not ScratchPadWindow.otree:
            ScratchPadWindow.otree = ScratchPadListModel()

        self.set_clear_all_btn_sensitivity(treemodel=ScratchPadWindow.otree)
        ScratchPadWindow.otree.connect('row-deleted',self.set_clear_all_btn_sensitivity)
        ScratchPadWindow.otree.connect('row-inserted',self.set_clear_all_btn_sensitivity)
        
        
        self.object_list.set_model(ScratchPadWindow.otree)
        
        self.top.signal_autoconnect({
            "on_close_scratchpad" : self.on_close_scratchpad,
            "on_clear_clicked": self.on_clear_clicked,
            "on_help_clicked": self.on_help_clicked,
            "on_objectlist_delete_event": self.on_delete_event,
            "on_scratch_pad_delete_event": self.on_delete_event
            })

        self.clear_all_btn.connect_object('clicked', gtk.ListStore.clear, ScratchPadWindow.otree)
        self.db.connect('database-changed', lambda x: ScratchPadWindow.otree.clear())
        
        self.add_itself_to_menu()
        self.window.show()

    def database_changed(self,database):
        self.db = database
        
    def set_clear_all_btn_sensitivity(self, treemodel=None, path=None, iter=None, user_param1=None):
        if len(treemodel) == 0:
            self.clear_all_btn.set_sensitive(False)
        else:
            self.clear_all_btn.set_sensitive(True)

    def set_clear_btn_sensitivity(self, sel=None, user_param1=None):
        if sel.count_selected_rows() == 0:
            self.clear_btn.set_sensitive(False)
        else:
            self.clear_btn.set_sensitive(True)
        

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()
        
    def add_itself_to_menu(self):
        """Add the ScratchPad window to the list of windows in the
        main GRAMPS interface. If this is the first instance to be
        created a submenu is created, if it is not the first instance
        then an entry is created in the existing sub menu."""
        return
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Scratch Pad'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        """Remove the instance of the pad from the Window menu in the
        main GRAMPS window. If this is the last pad then remove the
        ScratchPad sub menu as well."""
        return 
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-scratch-pad')

    def on_close_scratchpad(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def on_clear_clicked(self,obj):
        """Deletes the selected object from the object list"""
        selection = self.object_list.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
        return        
        

def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val

def place_title(db,event):
    pid = event.get_place_handle()
    if pid:
        return db.get_place_from_handle(pid).get_title()
    else:
        return u''

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ScratchPad(database,person,callback,parent=None):
    ScratchPadWindow(database,parent)
    
