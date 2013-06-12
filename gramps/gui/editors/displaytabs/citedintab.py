#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
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

from __future__ import print_function
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import sys

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from gramps.gen.errors import WindowActiveError
from gramps.gen.display.name import displayer as _nd
from gramps.gen.utils.db import (get_citation_referents, family_name,
                    get_participant_from_event)
from .grampstab import GrampsTab
from ...widgets import SimpleButton


_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_RETURN = Gdk.keyval_from_name("Return")

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class CitedInTab(GrampsTab):
    """
    This class provides the tabpage for overview of where a source is
    cited.
    It shows these objects in a treeviewl and allows to load citations in the 
    top  part of the source editor.
    """
    def __init__(self, dbstate, uistate, track, src, cite_apply_callback):
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
        @param src: source which we manage in this tab
        @type src: gen.lib.Source
        @param glade: glade objects with the needed widgets
        """
        self.src = src
        self.readonly = dbstate.db.readonly
        self.srtdata = []
        self.cite_apply_callback = cite_apply_callback
        
        GrampsTab.__init__(self, dbstate, uistate, track, _("Cited In"))
        self._set_label()

    def build_interface(self):
        """
        method called in init of GrampsTab
        """
        self.generate_data()
        self.build_model()
        self.setup_interface()
        self.show_all()

    def get_icon_name(self):
        return 'gramps-citation'

    def is_empty(self):
        """
        Return True if there is no data to show
        """
        return len(self.srtdata) == 0

    def setup_interface(self):
        """
        Set all information on the widgets
        * button tabs to load citation
        * treeview in scrollable with info
        """
        ##print (self.srtdata)
        ##print(self.obj2citemap)
        #create the load button, add it to a hbox, and add that box to the 
        #tab page
        self.load_btn  = SimpleButton(Gtk.STOCK_APPLY, self.apply_button_clicked)
        self.load_btn.set_tooltip_text(_("Apply a selected citation so as to"
                                " edit it in the top part of this interface"))
        self.edit_btn = SimpleButton(Gtk.STOCK_EDIT, self.edit_button_clicked)
        self.edit_btn.set_tooltip_text(_("Edit the object containing the"
                                " selected citation"))

        hbox = Gtk.HBox()
        hbox.set_spacing(6)
        hbox.pack_start(self.load_btn, False, True, 0)
        hbox.pack_start(self.edit_btn, False, True, 0)

        hbox.show_all()
        self.pack_start(hbox, False, True, 0)
        if self.dbstate.db.readonly:
            self.load_btn.set_sensitive(False)

        # create the tree, turn on rule hinting and connect the
        # button press to the double click function.
        self.tree = Gtk.TreeView()
        self.tree.set_rules_hint(True)
        self.tree.connect('button_press_event', self.double_click)
        self.tree.connect('key_press_event', self.key_pressed)
        
        self.make_columns()
        self.tree.set_model(self.model)

        self.selection = self.tree.get_selection()

        # create the scrolled window, and attach the treeview
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        #add this to the tab
        self.pack_start(scroll, True, True, 0)

    def generate_data(self):
        """
        Obtain all objects this source is cited in
        """
        self.srtdata = []
        self.obj2citemap = {}
        if not self.src.handle:
            #new object
            return
        db = self.dbstate.db
        #we don't nest calls to find_backlink_handles, so obtain first for 
        #the source, then in loop for citations
        listtopobj = [x for x in  db.find_backlink_handles(self.src.handle)]
        for (cobjclass, chandle) in listtopobj:
            #this will only be citations!
            ##print ('t1', cobjclass, chandle)
            if cobjclass == 'Citation':
                cite = db.get_citation_from_handle(chandle)
                has_backlink = False
                for (objclass, handle) in db.find_backlink_handles(chandle):
                    ##print ('t2', objclass, handle)
                    has_backlink = True
                    if objclass == 'Person':
                        ref = db.get_person_from_handle(handle)
                        self.__add_person(ref, cite)
                    elif objclass == 'Family':
                        ref = db.get_family_from_handle(handle)
                        self.__add_family(ref, cite)
                    elif objclass == 'Event':
                        ref = db.get_event_from_handle(handle)
                        self.__add_event(ref, cite)
                    elif objclass == 'Place':
                        ref = db.get_place_from_handle(handle)
                        self.__add_place(ref, cite)
                    elif objclass == 'Repository':
                        ref = db.get_repository_from_handle(handle)
                        self.__add_repo(ref, cite)
                    elif objclass in ['MediaObject', 'Media']:
                        ref = db.get_object_from_handle(handle)
                        self.__add_media(ref, cite)
                    else:
                        #most strange, not possible for citation there!
                        print ("Error in citedintab.py: citation referenced "
                                "outside citation. Run rebuild reference tables")
                if not has_backlink:
                    self.__add_cite(cite)
            else:
                #most strange, not possible !
                print ("Error in citedintab.py: source referenced "
                        "outside citation. Run rebuild reference tables")
        self.srtdata = sorted(self.srtdata, key=lambda x: glocale.sort_key(x[0]))

    def __add_object(self, obj, cite, descr_obj, shortdescr, objname):
        """
        obtain citation data of the object and store here so it can be shown
        in a treeview. If obj=None, an unused citation...
        """
        if obj is None:
            #adding of a citation which is part of not a singel object. The
            #citation is added under None.
            if not None in self.obj2citemap:
                self.obj2citemap[None] = {'prim': [], 'sec': [], 'subsec': []}
                #add for sorting in the treeview to map
                self.srtdata.append((descr_obj, None, shortdescr, objname))
            #add this citation
            self.obj2citemap[None]['prim'].append(cite.handle)
            return
            
        if not obj.handle in self.obj2citemap:
            self.obj2citemap[obj.handle] = {'prim': [], 'sec': [], 'subsec': []}
            #add for sorting in the treeview to map
            self.srtdata.append((descr_obj, obj.handle, shortdescr, objname))
        #we analyse the object to determine where the citation is used.
        if hasattr(obj, 'get_citation_list'):
            for citehandle in obj.get_citation_list():
                ##print ('t4', citehandle)
                if cite.handle == citehandle:
                    self.obj2citemap[obj.handle]['prim'].append(cite.handle)
        #now search the citation in secondary objects. This can maximally be
        # 2 levels deep, eg citation in attribute of eventref
        for objsec in obj.get_citation_child_list():
            ##print ('t5', objsec)
            if hasattr(objsec, 'get_citation_list'):
                for citehandle in objsec.get_citation_list():
                    ##print ('t6', citehandle)
                    if cite.handle == citehandle:
                        self.obj2citemap[obj.handle]['sec'].append(
                                    (cite.handle, self.format_sec_obj(objsec)))
            
            if hasattr(objsec, 'get_citation_child_list'):
                for objsubsec in objsec.get_citation_child_list():
                    ##print ('t7', objsubsec)
                    #eg attribute of eventref of person
                    for citehandle in objsubsec.get_citation_list():
                        if cite.handle == citehandle:
                            self.obj2citemap[obj.handle]['subsec'].append(
                                    (cite.handle, 
                                     _('%(first)s -> %(sec)s') % {
                                      'first': self.format_sec_obj(objsec),
                                      'sec' : self.format_sec_obj(objsubsec)}))

    def __add_person(self, obj, cite):
        """
        see __add_object
        """
        name = _nd.display_name(obj.get_primary_name())
        self.__add_object(obj, cite, _("Person %(id)s: %(descr)s") % {
                    'id': obj.get_gramps_id(),
                    'descr': name}, _("Cited in Person"), "Person")

    def __add_family(self, obj, cite):
        """
        see __add_object
        """
        name = family_name(obj, self.dbstate.db, _("Unknown Family"))
        self.__add_object(obj, cite, _("Family %(id)s: %(descr)s") % {
                    'id': obj.get_gramps_id(),
                    'descr': name}, _("Cited in Family"), "Family")

    def __add_event(self, obj, cite):
        """
        see __add_object
        """
        who = get_participant_from_event(self.dbstate.db, obj.handle)
        desc = obj.get_description()
        event_name = obj.get_type()
        if desc:
            event_name = '%s - %s' % (event_name, desc)
        if who:
            event_name = '%s - %s' % (event_name, who)
        name = _('Event %(id)s: %(descr)s') % {
                    'id': obj.get_gramps_id(),
                    'descr': event_name}
        self.__add_object(obj, cite, name, _("Cited in Event"), "Event")

    def __add_place(self, obj, cite):
        """
        see __add_object
        """
        self.__add_object(obj, cite, _('Place %(id)s: %(descr)s') % {
                    'id': obj.get_gramps_id(),
                    'descr': obj.get_title()}, _("Cited in Place"), "Place")

    def __add_repo(self, obj, cite):
        """
        see __add_object
        """
        self.__add_object(obj, cite, _('Repository %(id)s: %(descr)s') % {
                    'id': obj.get_gramps_id(),
                    'descr': obj.get_name()}, _("Cited in Repository"), "Repository")

    def __add_media(self, obj, cite):
        """
        see __add_object
        """
        name = obj.get_description().strip()
        if not name:
            name = obj.get_path()
        if not name:
            name = obj.get_mime_type()
        self.__add_object(obj, cite, _('Media %(id)s: %(descr)s') % {
                    'id': obj.get_gramps_id(),
                    'descr': name}, _("Cited in Media"), "Media")

    def __add_cite(self, cite):
        """
        see __add_object
        """
        self.__add_object(None, cite, _('Unused Citations'),
                    _('Unused Citation'), "Citation")

    def format_sec_obj(self, objsec):
        """
        text for treeview on citation in secondary object
        """
        classname = objsec.__class__.__name__
        classobj = classname
        descr = '' #TODO TO SET THIS !!
        if classname == "Address":
            descr = objsec.get_street()
            classobj = _("Address")
        elif classname == "Attribute":
            descr = str(objsec.get_type())
            classobj = _("Attribute")
        elif classname == "ChildRef":
            ref = objsec.get_reference_handle()
            person = self.dbstate.db.get_person_from_handle(ref)
            descr = _nd.display_name(person.get_primary_name())
            classobj = _("Child")
        elif classname == "EventRef":
            ref = objsec.get_reference_handle()
            event = self.dbstate.db.get_event_from_handle(ref)
            descr = str(event.get_type())
            classobj = _("Event Reference")
        elif classname == "LdsOrd":
            descr = objsec.type2str()
            classobj = _("LDS Ordinance")
        elif classname == "MediaRef":
            ref = objsec.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(ref)
            descr = obj.get_description().strip()
            if not descr:
                descr = obj.get_path()
            if not descr:
                descr = obj.get_mime_type()
            classobj = _("Media Reference")
        elif classname == "Name":
            descr = _nd.display_name(objsec)
            classobj = _("Name")
        elif classname == "PersonRef":
            ref = objsec.get_reference_handle()
            person = self.dbstate.db.get_person_from_handle(ref)
            if person is None:
                descr = ref
            else:
                descr = _nd.display_name(person.get_primary_name())

        descr = _("%(secobj)s: %(descr)s") % {
                    'secobj': classobj,
                    'descr' : descr}
        return descr

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs,
        the apply button handler is called
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.apply_button_clicked(obj)

    def key_pressed(self, obj, event):
        """
        Handles the return key being pressed on list. If the key is pressed,
        the Load button handler is called
        """
        if event.type == Gdk.EventType.KEY_PRESS:
            #print 'key pressed', event.keyval, event.get_state(), _ADD
            if  event.keyval in (_RETURN, _KP_ENTER):
                self.apply_button_clicked(obj)
                return True
            else:
                return GrampsTab.key_pressed(self, obj, event)
            return False

    def apply_button_clicked(self, obj):
        """
        Function called with the Load button is clicked. This function
        should be overridden by the derived class.
        """
        sel = self.get_selected()
        if sel[0]:
            self.cite_apply_callback(sel[0])

    def edit_button_clicked(self, obj):
        """
        Function called with the Load button is clicked. This function
        should be overridden by the derived class.
        """
        sel = self.get_selected()
        ref = sel[1]
        reftype = sel[2]
        if not ref:
            return

        from .. import (EditEvent, EditPerson, EditFamily, EditPlace, 
                        EditMedia, EditRepository)

        if reftype == 'Person':
            try:
                person = self.dbstate.db.get_person_from_handle(ref)
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
        elif reftype == 'Family':
            try:
                family = self.dbstate.db.get_family_from_handle(ref)
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                pass
        elif reftype == 'Place':
            try:
                place = self.dbstate.db.get_place_from_handle(ref)
                EditPlace(self.dbstate, self.uistate, [], place)
            except WindowActiveError:
                pass
        elif reftype == 'Media':
            try:
                obj = self.dbstate.db.get_object_from_handle(ref)
                EditMedia(self.dbstate, self.uistate, [], obj)
            except WindowActiveError:
                pass
        elif reftype == 'Event':
            try:
                event = self.dbstate.db.get_event_from_handle(ref)
                EditEvent(self.dbstate, self.uistate, [], event)
            except WindowActiveError:
                pass
        elif reftype == 'Repository':
            try:
                repo = self.dbstate.db.get_repository_from_handle(ref)
                EditRepository(self.dbstate, self.uistate, [], repo)
            except WindowActiveError:
                pass

    def build_model(self):
        """
        set up the model the treeview will use based on the data
        """
        # store (citationhandle, primobjhandle, name, citationgid, index, classname)
        # here, depending on the leve, name will be primobjname, secobjname, or
        # subsecobjname
        # citationhandle will be '' for rows which create sublevels
        self.model = Gtk.TreeStore(str, str, str, str, int, str)
        
        if sys.version_info[0] < 3:
            self.idle = GObject.idle_add(self.load_model().next)
        else:
            self.idle = GObject.idle_add(self.load_model().__next__)
    
    def load_model(self):
        """
        To make sure source editor is responsive, we use idle_add to 
        build the model.
        WARNING: a consequence of above is that loading can still be happening
            while the GUI using this model is no longer used. Disconnect any
            methods before closing the GUI.
        """
        for (descr, primhandle, shortdescr, objname) in self.srtdata:
            data = self.obj2citemap[primhandle]
            #top level node
            iter = self.model.append(None, ['', primhandle, descr, '', -1, objname])
            for ind, chandle in enumerate(data['prim']):
                citation = self.dbstate.db.get_citation_from_handle(chandle)
                self.model.append(iter, [chandle, primhandle, shortdescr,
                        citation.get_gramps_id(), ind, objname])
            base = len(data['prim'])
            for ind, val in enumerate(data['sec']):
                chandle, secdescr = val
                citation = self.dbstate.db.get_citation_from_handle(chandle)
                self.model.append(iter, [chandle, primhandle, secdescr,
                        citation.get_gramps_id(), base+ind, objname])
            base += len(data['sec'])
            for ind, val in enumerate(data['subsec']):
                chandle, subsecdescr = val
                citation = self.dbstate.db.get_citation_from_handle(chandle)
                self.model.append(iter, [chandle, primhandle, subsecdescr,
                        citation.get_gramps_id(), base+ind, objname])
            yield True
        #only now can we expand all nodes:
        self.tree.expand_all()
        yield False

    def make_columns(self):
        #make the columns in the treeview
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Cited in"), renderer, text=2)
        self.tree.append_column(column)
        column = Gtk.TreeViewColumn(_("Citation"), renderer, text=3)
        self.tree.append_column(column)

    def get_selected(self):
        """
        Return the (citation_handle, primary_object_handle, classname_prim_obj)
        associated with the selected row in the model.
        If no selection has been made, None is returned.
        If not on a citation, citation_handle will be empty string ''
        """
        (model, iter) = self.selection.get_selected()
        # store contains: (citationhandle, primobjhandle, name, citationgid, index)
        if iter:
            return  (model.get_value(iter, 0), model.get_value(iter, 1),
                     model.get_value(iter, 5))
        return None

