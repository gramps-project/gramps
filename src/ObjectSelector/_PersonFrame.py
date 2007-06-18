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

# $Id$

#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

from RelLib import Person
from NameDisplay import displayer
display_name = displayer.display

from _ObjectFrameBase import ObjectFrameBase
from _PersonFilterFrame import PersonFilterFrame
from _PersonPreviewFrame import PersonPreviewFrame
from _PersonTreeFrame import PersonTreeFrame


class PersonFrame(ObjectFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        'selection-changed'  : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                (gobject.TYPE_STRING,
                                 gobject.TYPE_PYOBJECT)),
        
        'add-object': (gobject.SIGNAL_RUN_LAST,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_PYOBJECT,))

        }

    __person_id_field = 1
    
    def __init__(self,
                 dbstate,
                 uistate,
                 filter_spec = None):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 uistate=uistate,                                 
                                 filter_frame = PersonFilterFrame(filter_spec=filter_spec),
                                 preview_frame = PersonPreviewFrame(dbstate),
                                 tree_frame = PersonTreeFrame(dbstate))

        def handle_selection(treeselection):
            (model, iter) = treeselection.get_selected()
            if iter:                
                (person,rowref) = model.get_value(iter,0)
                if len(rowref) > 1 or model.is_list():
                    if person:
                        self.emit('selection-changed', "%s [%s]" % (display_name(person),
                                                                    person.get_gramps_id()),
                                  person)
                    else:
                        self.emit('selection-changed',"No Selection",None)
                else:
                    self.emit('selection-changed',"No Selection",None)                    
            else:
                self.emit('selection-changed',"No Selection",None)
            

        self._tree_frame.get_selection().connect('changed',handle_selection)                
        self._tree_frame.get_selection().connect('changed',self.set_preview)
        self._tree_frame.get_tree().connect('row-activated',self._on_row_activated)

        self._filter_frame.connect('apply-filter',lambda w,m: self._tree_frame.set_model(m))
        self._filter_frame.connect('clear-filter',lambda w: self._tree_frame.set_model(None))

        # Now that the filter is connected we need to tell it to apply any
        # filter_spec that may have been passed to it. We can't apply the filter
        # until the connections have been made.
        gobject.idle_add(self._filter_frame.on_apply)

    def _on_row_activated(self,widget,path,col):
        (model, iter) = widget.get_selection().get_selected()
        if iter:
            (o,rowref) = model.get_value(iter,0)
            if o:
                self.emit('add-object',o)

    def new_object(self,button):
        from Editors import EditPerson
        
        person = Person()
        EditPerson(self._dbstate,self._uistate,[],person)
        
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFrame)

if __name__ == "__main__":
    pass
