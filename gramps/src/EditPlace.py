#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
# python modules
#
#-------------------------------------------------------------------------
import pickle

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import GDK
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
from RelLib import *
import Sources
import ImageSelect

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
pycode_tgts = [('url', 0, 0)]

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace:

    def __init__(self,parent,place,func=None):
        self.place = place
        self.db = parent.db
        self.parent = parent
        self.callback = func
        self.path = parent.db.getSavePath()
        self.not_loaded = 1
        self.ref_not_loaded = 1
        self.lists_changed = 0
        if place:
            self.srcreflist = place.getSourceRefList()
        else:
            self.srcreflist = []
            
        self.top_window = libglade.GladeXML(const.placesFile,"placeEditor")
        plwidget = self.top_window.get_widget("photolist")
        self.glry = ImageSelect.Gallery(place, self.path, plwidget, self.db, self)
        self.title = self.top_window.get_widget("place_title")
        self.city = self.top_window.get_widget("city")
        self.parish = self.top_window.get_widget("parish")
        self.county = self.top_window.get_widget("county")
        self.state = self.top_window.get_widget("state")
        self.country = self.top_window.get_widget("country")
        self.longitude = self.top_window.get_widget("longitude")
        self.latitude = self.top_window.get_widget("latitude")
        self.note = self.top_window.get_widget("place_note")

        self.web_list = self.top_window.get_widget("web_list")
        self.web_url = self.top_window.get_widget("web_url")
        self.web_go = self.top_window.get_widget("web_go")
        self.web_description = self.top_window.get_widget("url_des")
        
        self.loc_list = self.top_window.get_widget("loc_list")
        self.loc_city = self.top_window.get_widget("loc_city")
        self.loc_county = self.top_window.get_widget("loc_county")
        self.loc_state  = self.top_window.get_widget("loc_state")
        self.loc_parish  = self.top_window.get_widget("loc_parish")
        self.loc_country = self.top_window.get_widget("loc_country")

        self.ulist = place.getUrlList()[:]
        self.llist = place.get_alternate_locations()[:]

        self.title.set_text(place.get_title())
        mloc = place.get_main_location()
        self.city.set_text(mloc.get_city())
        self.county.set_text(mloc.get_county())
        self.state.set_text(mloc.get_state())
        self.parish.set_text(mloc.get_parish())
        self.country.set_text(mloc.get_country())
        self.longitude.set_text(place.get_longitude())
        self.latitude.set_text(place.get_latitude())
        self.refinfo = self.top_window.get_widget("refinfo")
        self.slist = self.top_window.get_widget("slist")

        self.note.set_point(0)
        self.note.insert_defaults(place.getNote())
        self.note.set_word_wrap(1)

        self.top_window.signal_autoconnect({
            "destroy_passed_object"     : Utils.destroy_passed_object,
            "on_photolist_select_icon"  : self.glry.on_photo_select_icon,
            "on_photolist_button_press" : self.glry.on_button_press_event,
            "on_switch_page"            : self.on_switch_page,
            "on_addphoto_clicked"       : self.glry.on_add_photo_clicked,
            "on_deletephoto_clicked"    : self.glry.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.glry.popup_change_description,
            "on_add_url_clicked"        : self.on_add_url_clicked,
            "on_delete_url_clicked"     : self.on_delete_url_clicked,
            "on_update_url_clicked"     : self.on_update_url_clicked,
            "on_add_loc_clicked"        : self.on_add_loc_clicked,
            "on_delete_loc_clicked"     : self.on_delete_loc_clicked,
            "on_update_loc_clicked"     : self.on_update_loc_clicked,
            "on_web_list_select_row"    : self.on_web_list_select_row,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_loc_list_select_row"    : self.on_loc_list_select_row,
            "on_web_list_button_press"  : self.web_list_double_click,
            "on_loc_list_button_press"  : self.loc_list_double_click,
            "on_apply_clicked"          : self.on_place_apply_clicked
            })

        self.top = self.top_window.get_widget("placeEditor")

        # Typing CR selects OK button
        self.top.editable_enters(self.title);
        self.top.editable_enters(self.city);
        self.top.editable_enters(self.parish);
        self.top.editable_enters(self.county);
        self.top.editable_enters(self.state);
        self.top.editable_enters(self.country);
        self.top.editable_enters(self.longitude);
        self.top.editable_enters(self.latitude);

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,self.top_window,self.slist)
        
        if self.place.getId() == "":
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.web_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                    pycode_tgts,GDK.ACTION_COPY)
        self.web_list.drag_source_set(GDK.BUTTON1_MASK,
                                      pycode_tgts, GDK.ACTION_COPY)
        self.web_list.connect('drag_data_get',
                              self.url_source_drag_data_get)
        self.web_list.connect('drag_data_received',
                              self.url_dest_drag_data_received)

        self.redraw_url_list()
        self.redraw_location_list()
        
    def url_dest_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'place = "%s"' % data[1]
            if place == self.place.getId() or mytype != 'url':
                return
            foo = pickle.loads(data[2]);
            self.ulist.append(foo)
            self.lists_changed = 1
            self.redraw_url_list()

    def url_source_drag_data_get(self,widget, context, sel_data, info, time):
        ev = widget.get_row_data(widget.focus_row)
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str(('url',self.place.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def update_lists(self):
        self.place.setUrlList(self.ulist)
        self.place.set_alternate_locations(self.llist)
        if self.lists_changed:
            Utils.modified()
            
    def redraw_url_list(self):
        length = Utils.redraw_list(self.ulist,self.web_list,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")

    def redraw_location_list(self):
        Utils.redraw_list(self.llist,self.loc_list,disp_loc)


    def on_web_go_clicked(self,obj):
        import gnome.url

        text = obj.get()
        if text != "":
            gnome.url.show(text)

    def set(self,field,getf,setf):
        text = field.get_text()
        if text != getf():
            setf(text)
            Utils.modified()
    
    def on_place_apply_clicked(self,obj):

        note = self.note.get_chars(0,-1)
        mloc = self.place.get_main_location()

        self.set(self.city,mloc.get_city,mloc.set_city)
        self.set(self.parish,mloc.get_parish,mloc.set_parish)
        self.set(self.state,mloc.get_state,mloc.set_state)
        self.set(self.county,mloc.get_county,mloc.set_county)
        self.set(self.country,mloc.get_country,mloc.set_country)
        self.set(self.title,self.place.get_title,self.place.set_title)
        self.set(self.longitude,self.place.get_longitude,
                 self.place.set_longitude)
        self.set(self.latitude,self.place.get_latitude,
                 self.place.set_latitude)

        if self.lists_changed:
            self.place.setSourceRefList(self.srcreflist)
            Utils.modified()
        
        if note != self.place.getNote():
            self.place.setNote(note)
            Utils.modified()

        self.update_lists()

        Utils.destroy_passed_object(self.top)
        if self.callback:
            self.callback(self.place)

    def on_switch_page(self,obj,a,page):
        if page == 3 and self.not_loaded:
            self.not_loaded = 0
            self.glry.load_images()
        elif page == 5 and self.ref_not_loaded:
            self.ref_not_loaded = 0
            self.display_references()

    def on_update_url_clicked(self,obj):
        import UrlEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            if self.place:
                name = _("Internet Address Editor for %s") % self.place.get_title()
            else:
                name = _("Internet Address Editor")
            UrlEdit.UrlEditor(self,name,obj.get_row_data(row))

    def on_update_loc_clicked(self,obj):
        import LocEdit
        if obj.selection:
            row = obj.selection[0]
            LocEdit.LocationEditor(self,obj.get_row_data(row))

    def on_delete_url_clicked(self,obj):
        if Utils.delete_selected(obj,self.ulist):
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_loc_clicked(self,obj):
        if Utils.delete_selected(obj,self.llist):
            self.lists_changed = 1
            self.redraw_location_list()

    def on_add_url_clicked(self,obj):
        import UrlEdit
        if self.place:
            name = _("Internet Address Editor for %s") % self.place.get_title()
        else:
            name = _("Internet Address Editor")
        UrlEdit.UrlEditor(self,name,None)

    def on_add_loc_clicked(self,obj):
        import LocEdit
        LocEdit.LocationEditor(self,None)

    def web_list_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_update_url_clicked(obj)

    def loc_list_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_update_loc_clicked(obj)

    def on_web_list_select_row(self,obj,row,b,c):
        url = obj.get_row_data(row)
        if url == None:
            self.web_url.set_text("")
            self.web_go.set_sensitive(0)
            self.web_description.set_text("")
        else:
            path = url.get_path()
            self.web_url.set_text(path)
            self.web_go.set_sensitive(1)
            self.web_description.set_text(url.get_description())

    def on_loc_list_select_row(self,obj,row,b,c):
        loc = obj.get_row_data(row)

        self.loc_city.set_text(loc.get_city())
        self.loc_county.set_text(loc.get_county())
        self.loc_state.set_text(loc.get_state())
        self.loc_parish.set_text(loc.get_parish())
        self.loc_country.set_text(loc.get_country())

    def display_references(self):
        pevent = []
        fevent = []
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for event in [p.getBirth(), p.getDeath()] + p.getEventList():
                if event.getPlace() == self.place:
                    pevent.append((p,event))
        for f in self.db.getFamilyMap().values():
            for event in f.getEventList():
                if event.getPlace() == self.place:
                    fevent.append((f,event))
                    
        self.refinfo.set_point(0)
        self.refinfo.set_word_wrap(1)

        if len(pevent) > 0:
            self.refinfo.insert_defaults(_("People") + "\n")
            self.refinfo.insert_defaults("_________________________\n\n")
            t = _("%s [%s]: event %s\n")

            for e in pevent:
                msg = t % (GrampsCfg.nameof(e[0]),e[0].getId(),e[1].getName())
                self.refinfo.insert_defaults(msg)

        if len(fevent) > 0:
            self.refinfo.insert_defaults("\n%s\n" % _("Families"))
            self.refinfo.insert_defaults("_________________________\n\n")
            t = _("%s [%s]: event %s\n")

            for e in fevent:
                father = e[0].getFather()
                mother = e[0].getMother()
                if father and mother:
                    fname = "%s and %s" % (GrampsCfg.nameof(father),GrampsCfg.nameof(mother))
                elif father:
                    fname = "%s" % GrampsCfg.nameof(father)
                else:
                    fname = "%s" % GrampsCfg.nameof(mother)

                msg = t % (fname,e[0].getId(),e[1].getName())
                self.refinfo.insert_defaults(msg)
        
#-------------------------------------------------------------------------
#
# disp_url
#
#-------------------------------------------------------------------------
def disp_url(url):
    return [url.get_path(),url.get_description()]

#-------------------------------------------------------------------------
#
# disp_loc
#
#-------------------------------------------------------------------------
def disp_loc(loc):
    return [loc.get_city(),loc.get_county(),loc.get_state(),loc.get_country()]

#-------------------------------------------------------------------------
#
# DeletePlaceQuery
#
#-------------------------------------------------------------------------
class DeletePlaceQuery:

    def __init__(self,place,db,update):
        self.db = db
        self.place = place
        self.update = update
        
    def query_response(self):
        del self.db.getPlaceMap()[self.place.getId()]
        Utils.modified()

        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for event in [p.getBirth(), p.getDeath()] + p.getEventList():
                if event.getPlace() == self.place:
                    event.setPlace(None)
        for f in self.db.getFamilyMap().values():
            for event in f.getEventList():
                if event.getPlace() == self.place:
                    event.setPlace(None)
        self.update(0)
