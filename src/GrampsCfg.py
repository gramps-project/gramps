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

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade
import gnome
import gnome.ui

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import GrampsGconfKeys
import RelLib
import const
import Utils
import PaperMenu
import Plugins
import DateHandler

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
INDEX         = "i"
OBJECT        = "o"
DATA          = "d"

_surname_styles = [
    _("Father's surname"),
    _("None"),
    _("Combination of mother's and father's surname"),
    _("Icelandic style"),
    ]

_name_format_list = [
    (_("Firstname Surname"),  Utils.normal_name, Utils.phonebook_name, lambda x: x.get_surname()),
    (_("Surname, Firstname"), Utils.phonebook_name, Utils.phonebook_name, lambda x: x.get_surname()),
    (_("Firstname SURNAME"),  Utils.upper_name, Utils.phonebook_upper_name, lambda x : x.get_upper_surname()),
    (_("SURNAME, Firstname"), Utils.phonebook_upper_name, Utils.phonebook_upper_name, lambda x: x.get_upper_surname()),
    ]

panellist = [
    (_("Database"),
     [( _("General"), 1),
      ( _("Media Objects"), 7),
      ( _("GRAMPS IDs"), 8)]),
    (_("Display"),
     [( _("General"), 3),
      ( _("Dates and Names"), 4),
      ( _("Toolbar and Statusbar"), 2)]),
    (_("Usage"),
     [( _("Report Preferences"), 6),
      ( _("Researcher Information"), 5),
      ( _("Data Guessing"), 9)]),
    ]


# Not exactly gconf keys, but the functions directly dependent on them
def get_nameof():
    return _name_format_list[GrampsGconfKeys.get_name_format(_name_format_list)][1]

def get_display_name():
    return _name_format_list[GrampsGconfKeys.get_name_format(_name_format_list)][2]

def get_display_surname():
    return _name_format_list[GrampsGconfKeys.get_name_format(_name_format_list)][3]

def get_toolbar_style():
    saved_toolbar = GrampsGconfKeys.get_toolbar()
    if saved_toolbar in range(4):
        return saved_toolbar
    else:
        try:
            gnome_toolbar_str = GrampsGconfKeys.client.get_string("/desktop/gnome/interface/toolbar_style")
            gnome_toolbar = eval("gtk.TOOLBAR_%s" % 
                        gnome_toolbar_str.replace('-','_').upper())
        except:
            gnome_toolbar = 2
        return gnome_toolbar

def set_calendar_date_format():
    format_list = DateHandler.get_date_formats()
    DateHandler.set_format(GrampsGconfKeys.get_date_format(format_list))
    RelLib.display.set_format(GrampsGconfKeys.get_date_format(format_list))

#-------------------------------------------------------------------------
#
# make_path - 
#   Creates a directory if it does not already exist. Assumes that the
#   parent directory already exits
#
#-------------------------------------------------------------------------
def make_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def loadConfig():
    """
    Load preferences on startup. Not much to do, since all the prefs
    are in gconf and can be retrieved any time. 
    """
    make_path(os.path.expanduser("~/.gramps"))
    make_path(os.path.expanduser("~/.gramps/filters"))
    make_path(os.path.expanduser("~/.gramps/plugins"))
    make_path(os.path.expanduser("~/.gramps/templates"))
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_researcher():
    n = GrampsGconfKeys.get_researcher_name()
    a = GrampsGconfKeys.get_researcher_addr()
    c = GrampsGconfKeys.get_researcher_city()
    s = GrampsGconfKeys.get_researcher_state()
    ct = GrampsGconfKeys.get_researcher_country()
    p = GrampsGconfKeys.get_researcher_postal()
    ph = GrampsGconfKeys.get_researcher_phone()
    e = GrampsGconfKeys.get_researcher_email()

    owner = RelLib.Researcher()
    owner.set(n,a,c,s,ct,p,ph,e)
    return owner
    
ext_items = []

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class ConfigWidget:
    def __init__(self,panel,key,label,default):
        self.p = panel
        self.k = key
        self.l = label
        self.w = None
        self.d = default
        self.tag = "/apps/gramps/%s/%s" % (panel,key)
        
    def set(self):
        pass

class ConfigEntry(ConfigWidget):

    def get_widgets(self):
        l = gtk.Label(self.l)
        l.show()
        self.w = gtk.Entry()
        self.w.show()
        
        val = get_string(self.tag)
        if val == None:
            self.w.set_text(self.d)
        else:
            self.w.set_text(val)
        return [l,self.w]

    def set(self):
        val = unicode(self.w.get_text())
        GrampsGconfKeys.client.set_string(self.tag,val)

class ConfigInt(ConfigWidget):

    def set_range(self,lower,upper):
        self.lower = lower
        self.upper = upper
        
    def get_widgets(self):
        l = gtk.Label(self.l)
        l.show()
        self.w = gtk.SpinButton(digits=0)
        self.w.show()
        
        val = get_string(self.tag)
        if val == None:
            val = int(self.d)
        else:
            val = int(val)

        adj = gtk.Adjustment(val,self.lower,self.upper,1,1,1)
        
        self.w.set_adjustment(adj)
        return [l,self.w]

    def set(self):
        val = self.w.get_value_as_int()
        GrampsGconfKeys.client.set_int(self.tag,val)

class ConfigCheckbox(ConfigWidget):
    
    def get_widgets(self):
        self.w = gtk.CheckButton(self.l)
        self.w.show()
        val = get_bool(self.tag)
        if val == None:
            self.w.set_active(self.d)
        else:
            self.w.set_active(val)
        return [self.w]

    def set(self):
        val = self.w.get_active()
        GrampsGconfKeys.client.set_bool(self.tag,val)
        

class ConfigFile(ConfigWidget):

    def get_widgets(self):
        self.w = gnome.ui.FileEntry(self.tag)
        lbl = gtk.Label(self.l)
        self.w.show()
        lbl.show()
        val = get_string(self.tag)
        self.w.set_title("%s -- GRAMPS" % (self.l))
        if val == None:
            self.w.gtk_entry().set_text(self.d)
        else:
            self.w.gtk_entry().set_text(val)
        return [lbl,self.w]

    def set(self):
        val = self.w.get_full_path(0)
        GrampsGconfKeys.client.set_string(self.tag,val)
        

def add_text(category,panel,frame,config_tag,label,default):
    ext_items.append((category,panel,frame,ConfigEntry(panel,config_tag,label,default)))

def add_file_entry(category,panel,frame,config_tag,label,default):
    ext_items.append((category,panel,frame,ConfigFile(panel,config_tag,label,default)))

def add_int(category,panel,frame,config_tag,label,default,range=(0,100)):
    cfgint = ConfigInt(panel,config_tag,label,default)
    cfgint.set_range(range[0],range[1])
    ext_items.append((category,panel,frame,cfgint))

def add_checkbox(category,panel,frame,config_tag,label,default):
    ext_items.append((category,panel,frame,ConfigCheckbox(panel,config_tag,label,default)))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GrampsPreferences:
    def __init__(self,db):
        self.built = 0
        self.db = db
        self.top = gtk.glade.XML(const.prefsFile,"preferences","gramps")
        self.top.signal_autoconnect({
            "on_close_clicked" : self.on_close_clicked,
            "on_help_clicked" : self.on_propertybox_help,
            "on_tree_select_row" : self.select
            })

        self.window = self.top.get_widget("preferences")
        self.tree = self.top.get_widget("tree")
        self.store = gtk.TreeStore(gobject.TYPE_STRING)
        self.selection = self.tree.get_selection()
        self.selection.connect('changed',self.select)
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.tree.set_model(self.store)
        self.panel = self.top.get_widget("panel")
        self.ofmt = self.top.get_widget("output_format")
        self.gfmt = self.top.get_widget("graphical_format")

        self.imap = {}
        self.build_tree()
        self.build()
        self.build_ext()
        self.built = 1
        self.window.show()

    def build_tree(self):
        prev = None
        ilist = []
        for (name,lst) in panellist:
            node = self.store.insert_after(None, prev)
            self.store.set(node,0,name)
            next = None
            for (subname,tab) in lst:
                next = self.store.insert_after(node,next)
                ilist.append((next,tab))
                self.store.set(next,0,subname)
        for next,tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab
        
    def build(self):

        auto = self.top.get_widget("autoload")
        auto.set_active(GrampsGconfKeys.get_autoload())
        auto.connect('toggled',lambda obj: GrampsGconfKeys.save_autoload(obj.get_active()))

        lds = self.top.get_widget("uselds")
        lds.set_active(GrampsGconfKeys.get_uselds())
        lds.connect('toggled',lambda obj: GrampsGconfKeys.save_uselds(obj.get_active()))

        mr = self.top.get_widget("mediaref")
        mc = self.top.get_widget("mediacopy")
        if GrampsGconfKeys.get_media_reference():
            mr.set_active(1)
        else:
            mc.set_active(1)
        mr.connect('toggled',lambda obj: save_media_reference(obj.get_active()))

        dg = self.top.get_widget("globalprop")
        dg.set_active(GrampsGconfKeys.get_media_global())
        dg.connect('toggled',lambda obj: GrampsGconfKeys.save_media_global(obj.get_active()))

        dl = self.top.get_widget("localprop")
        dl.set_active(GrampsGconfKeys.get_media_local())
        dl.connect('toggled',lambda obj: GrampsGconfKeys.save_media_local(obj.get_active()))

        index_vis = self.top.get_widget("show_child_id")
        index_vis.set_active(GrampsGconfKeys.get_index_visible())
        index_vis.connect('toggled',lambda obj: GrampsGconfKeys.save_index_visible(obj.get_active()))

        ipr = self.top.get_widget("iprefix")
        ipr.set_text(GrampsGconfKeys.get_person_id_prefix())
        ipr.connect('changed',lambda obj: GrampsGconfKeys.save_iprefix(obj.get_text()))
        opr = self.top.get_widget("oprefix")
        opr.set_text(GrampsGconfKeys.get_object_id_prefix())
        opr.connect('changed',lambda obj: GrampsGconfKeys.save_oprefix(obj.get_text()))
        fpr = self.top.get_widget("fprefix")
        fpr.set_text(GrampsGconfKeys.get_family_id_prefix())
        fpr.connect('changed',lambda obj: GrampsGconfKeys.save_fprefix(obj.get_text()))
        spr = self.top.get_widget("sprefix")
        spr.set_text(GrampsGconfKeys.get_source_id_prefix())
        spr.connect('changed',lambda obj: GrampsGconfKeys.save_sprefix(obj.get_text()))
        ppr = self.top.get_widget("pprefix")
        ppr.set_text(GrampsGconfKeys.get_place_id_prefix())
        ppr.connect('changed',lambda obj: GrampsGconfKeys.save_pprefix(obj.get_text()))

        sb2 = self.top.get_widget("stat2")
        sb3 = self.top.get_widget("stat3")
        if GrampsGconfKeys.get_statusbar() == 0 or GrampsGconfKeys.get_statusbar() == 1:
            sb2.set_active(1)
        else:
            sb3.set_active(1)
        sb2.connect('toggled',
                lambda obj: GrampsGconfKeys.save_statusbar(2-obj.get_active()))

        toolbarmenu = self.top.get_widget("tooloptmenu")
        toolbarmenu.set_history(GrampsGconfKeys.get_toolbar())
        toolbarmenu.connect('changed',lambda obj: GrampsGconfKeys.save_toolbar(obj.get_history()))

        pvbutton = self.top.get_widget('pvbutton')
        fvbutton = self.top.get_widget('fvbutton')
        if GrampsGconfKeys.get_default_view() == 0:
            pvbutton.set_active(1)
        else:
            fvbutton.set_active(1)
        fvbutton.connect('toggled',lambda obj: GrampsGconfKeys.save_default_view(obj.get_active()))

        familyview1 = self.top.get_widget('familyview1')
        familyview2 = self.top.get_widget('familyview2')
        if GrampsGconfKeys.get_family_view() == 0:
            familyview1.set_active(1)
        else:
            familyview2.set_active(1)
        familyview2.connect('toggled',lambda obj: GrampsGconfKeys.save_family_view(obj.get_active()))

        usetips = self.top.get_widget('usetips')
        usetips.set_active(GrampsGconfKeys.get_usetips())
        usetips.connect('toggled',lambda obj: GrampsGconfKeys.save_usetips(obj.get_active()))

        paper_obj = self.top.get_widget("paper_size")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(PaperMenu.paper_sizes)):
            name = PaperMenu.paper_sizes[index].get_name()
            if name == GrampsGconfKeys.get_paper_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            menu.append(item)
        menu.set_active(choice)
        paper_obj.set_menu(menu)
        paper_obj.connect("changed", 
                    lambda obj: GrampsGconfKeys.save_paper_preference(obj.get_menu().get_active().get_data(DATA)))

        lastnamegen_obj = self.top.get_widget("lastnamegen")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(_surname_styles)):
            name = _surname_styles[index]
            item = gtk.MenuItem(name)
            item.set_data(DATA,index)
            item.show()
            menu.append(item)
        menu.set_active(GrampsGconfKeys.get_lastnamegen(_surname_styles))
        lastnamegen_obj.set_menu(menu)
        lastnamegen_obj.connect("changed", 
                    lambda obj: GrampsGconfKeys.save_lastnamegen(obj.get_menu().get_active().get_data(DATA)),_surname_styles)

        self.osubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_text_doc_list():
            if name == GrampsGconfKeys.get_output_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            self.osubmenu.append(item)
            index = index + 1
        self.osubmenu.set_active(choice)
        self.ofmt.set_menu(self.osubmenu)
        self.ofmt.connect("changed", 
                    lambda obj: GrampsGconfKeys.save_output_preference(obj.get_menu().get_active().get_data(DATA)))

        self.gsubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_draw_doc_list():
            if name == GrampsGconfKeys.get_goutput_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            self.gsubmenu.append(item)
            index = index + 1
        self.gsubmenu.set_active(choice)
        self.gfmt.set_menu(self.gsubmenu)
        self.gfmt.connect("changed", 
                    lambda obj: GrampsGconfKeys.save_goutput_preference(obj.get_menu().get_active().get_data(DATA)))

        date_option = self.top.get_widget("date_format")
        date_menu = gtk.Menu()
        dlist = DateHandler.get_date_formats()
        for index in range(0,len(dlist)):
            item = gtk.MenuItem(dlist[index])
            item.set_data(INDEX,index)
            item.show()
            date_menu.append(item)
        try:
            # Technically, a selected format might me out of range
            # for this locale's format list. 
            date_menu.set_active(GrampsGconfKeys.get_date_format(dlist))
        except:
            pass

        date_option.set_menu(date_menu)
        date_option.connect("changed",
                    lambda obj: GrampsGconfKeys.save_date_format(obj.get_menu().get_active().get_data(INDEX),dlist))

        name_option = self.top.get_widget("name_format")
        name_menu = gtk.Menu()
        for index in range(0,len(_name_format_list)):
            name_tuple = _name_format_list[index]
            item = gtk.MenuItem(name_tuple[0])
            item.set_data(INDEX,index)
            item.show()
            name_menu.append(item)
        name_menu.set_active(GrampsGconfKeys.get_name_format(_name_format_list))
        name_option.set_menu(name_menu)
        name_option.connect("changed", 
                    lambda obj: GrampsGconfKeys.save_name_format(obj.get_menu().get_active().get_data(INDEX),_name_format_list))

        resname = self.top.get_widget("resname")
        resname.set_text(GrampsGconfKeys.get_researcher_name())
        resname.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_name(obj.get_text()))
        resaddr = self.top.get_widget("resaddr")
        resaddr.set_text(GrampsGconfKeys.get_researcher_addr())
        resaddr.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_addr(obj.get_text()))
        rescity = self.top.get_widget("rescity")
        rescity.set_text(GrampsGconfKeys.get_researcher_city())
        rescity.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_city(obj.get_text()))
        resstate = self.top.get_widget("resstate")
        resstate.set_text(GrampsGconfKeys.get_researcher_state())
        resstate.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_state(obj.get_text()))
        rescountry = self.top.get_widget("rescountry")
        rescountry.set_text(GrampsGconfKeys.get_researcher_country())
        rescountry.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_country(obj.get_text()))
        respostal = self.top.get_widget("respostal")
        respostal.set_text(GrampsGconfKeys.get_researcher_postal())
        respostal.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_postal(obj.get_text()))
        resphone = self.top.get_widget("resphone")
        resphone.set_text(GrampsGconfKeys.get_researcher_phone())
        resphone.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_phone(obj.get_text()))
        resemail = self.top.get_widget("resemail")
        resemail.set_text(GrampsGconfKeys.get_researcher_email())
        resemail.connect('changed',lambda obj: GrampsGconfKeys.save_researcher_email(obj.get_text()))

        repdir = self.top.get_widget("repdir").gtk_entry()
        repdir.set_text(GrampsGconfKeys.get_report_dir())
        repdir.connect('changed',lambda obj: GrampsGconfKeys.save_report_dir(obj.get_text()))
        webdir = self.top.get_widget("htmldir").gtk_entry()
        webdir.set_text(GrampsGconfKeys.get_web_dir())
        webdir.connect('changed',lambda obj: GrampsGconfKeys.save_web_dir(obj.get_text()))

    def build_ext(self):
        self.c = {}
        self.ext_list = []
        for (c,p,f,o) in ext_items:
            self.ext_list.append(o)
            if self.c.has_key(c):
                if self.c[c][p].has_key(f):
                    self.c[c][p][f].append(o)
                else:
                    self.c[c][p][f] = [o]
            else:
                self.c[c] = {}
                self.c[c][p] = {}
                self.c[c][p][f] = [o]

        next_panel=13
        for c in self.c.keys():
            node = self.tree.insert_node(None,None,[c],is_leaf=0,expanded=1)
            self.tree.node_set_row_data(node,0)
            next = None
            for panel in self.c[c].keys():
                next = self.tree.insert_node(node,next,[panel],is_leaf=1,expanded=1)
                self.tree.node_set_row_data(next,next_panel)
                next_panel = next_panel + 1
                box = gtk.VBox()
                box.show()
                col = 0
                panel_label = gtk.Label("")
                panel_label.show()
                self.panel.append_page(box,panel_label)
                for frame in self.c[c][panel].keys():
                    pairs = self.c[c][panel][frame]
                    fr = gtk.Frame(frame)
                    fr.show()
                    box.pack_start(fr,gtk.FALSE,gtk.FALSE)
                    table = gtk.Table(len(pairs),2)
                    table.show()
                    fr.add(table)
                    for wobj in pairs:
                        w = wobj.get_widgets()
                        if len(w) == 2:
                            table.attach(w[0],0,1,col,col+1,
                                         gtk.FILL,gtk.SHRINK,5,5)
                            table.attach(w[1],1,2,col,col+1,
                                         gtk.FILL|gtk.EXPAND,gtk.SHRINK,5,5)
                        else:
                            table.attach(w[0],0,2,col,col+1,
                                         gtk.FILL|gtk.EXPAND,gtk.SHRINK,5,5)
                        col = col + 1
            
    def select(self,obj):
        store,node = self.selection.get_selected()
        if node:
            path = store.get_path(node)
        if node and self.imap.has_key(path):
            self.panel.set_current_page(self.imap[path])
        
    def on_propertybox_help(self,obj):
        gnome.help_display('gramps-manual','gramps-prefs')

    def on_close_clicked(self,obj):
        self.save_data()
        Utils.destroy_passed_object(self.window)
    
    def on_propertybox_apply(self,obj):
        self.save_data()

    def save_data(self):
        for o in self.ext_list:
            o.set()

#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    GrampsPreferences(db)
