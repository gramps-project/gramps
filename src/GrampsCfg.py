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

#
# SUSE calls the gconf module "gnome.gconf"
#
try:
    import gconf
except ImportError:
    import gnome.gconf
    gconf = gnome.gconf

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import PaperMenu
import Plugins
import Calendar

client = gconf.client_get_default()
client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)

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

_date_format_list = [
    _("Month Day, Year"),
    _("MON Day, Year"),
    _("Day MON Year"),
    _("MM/DD/YYYY"),
    _("MM-DD-YYYY"),
    _("DD/MM/YYYY"),
    _("DD-MM-YYYY"),
    _("MM.DD.YYYY"),
    _("DD.MM.YYYY"),
    _("DD. Month Year"),
    _("YYYY/MM/DD"),
    _("YYYY-MM-DD"),
    _("YYYY.MM.DD"),
    ]

_date_entry_list = [
    _("MM/DD/YYYY, MM.DD.YYYY, or MM-DD-YYYY"),
    _("DD/MM/YYYY, DD.MM.YYYY, or DD-MM-YYYY"),
    _("YYYY/MM/DD, YYYY.MM.DD, or YYYY-MM-DD"),
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
      ( _("GRAMPS internal IDs"), 8)]),
    (_("Display"),
     [( _("General"), 3),
      ( _("Dates and Calendars"), 4),
      ( _("Toolbar and Statusbar"), 2)]),
    (_("Usage"),
     [( _("Report Preferences"), 6),
      ( _("Researcher Information"), 5),
      ( _("Data Guessing"), 9)]),
    ]

#-------------------------------------------------------------------------
#
# Obtain values from gconf keys
#
#-------------------------------------------------------------------------

def get_usetips():
    return client.get_bool("/apps/gramps/use-tips")

def get_betawarn():
    return client.get_bool("/apps/gramps/betawarn")

def get_iprefix():
    return client.get_string("/apps/gramps/iprefix")

def get_oprefix():
    return client.get_string("/apps/gramps/oprefix")

def get_sprefix():
    return client.get_string("/apps/gramps/sprefix")

def get_pprefix():
    return client.get_string("/apps/gramps/pprefix")

def get_fprefix():
    return client.get_string("/apps/gramps/fprefix")

def get_autoload():
    return client.get_bool("/apps/gramps/autoload")

def get_uselds():
    return client.get_bool("/apps/gramps/use-lds")

def get_lastfile():
    return client.get_string("/apps/gramps/recent-file")

def get_statusbar():
    return client.get_int("/apps/gramps/statusbar")

def get_toolbar():
    save_toolbar = client.get_int("/apps/gramps/toolbar")
    gnome_toolbar_str = client.get_string("/desktop/gnome/interface/toolbar_style")
    try:
        gnome_toolbar = eval("gtk.TOOLBAR_%s" % 
                        gnome_toolbar_str.replace('-','_').upper())
    except:
        gnome_toolbar = 2
    if save_toolbar == 5:
        return gnome_toolbar
    else:
        return save_toolbar

def get_calendar():
    return client.get_bool("/apps/gramps/show-calendar")

def get_paper_preference():
    return client.get_string("/apps/gramps/paper-preference")

def get_output_preference():
    return client.get_string("/apps/gramps/output-preference")

def get_goutput_preference():
    return client.get_string("/apps/gramps/goutput-preference")

def get_lastnamegen():
    return client.get_int("/apps/gramps/surname-guessing")

def get_report_dir():
    report_dir = client.get_string("/apps/gramps/report-directory")
    return os.path.normpath(report_dir) + os.sep

def get_web_dir():
    web_dir = client.get_string("/apps/gramps/website-directory")
    return os.path.normpath(web_dir) + os.sep

def get_id_edit():
    return client.get_bool("/apps/gramps/id-edit")

def get_index_visible():
    return client.get_bool("/apps/gramps/index-visible")

def get_media_reference():
    return client.get_bool("/apps/gramps/make-reference")

def get_media_global():
    return client.get_bool("/apps/gramps/media-global")

def get_media_local():
    return client.get_bool("/apps/gramps/media-local")

def get_default_view():
    return client.get_int("/apps/gramps/defaultview")

def get_family_view():
    return client.get_int("/apps/gramps/familyview")

def get_use_tips():
    return client.get_bool("/apps/gramps/use-tips")

def get_date_entry():
    return client.get_int("/apps/gramps/date-entry")

def get_date_format():
    return client.get_int("/apps/gramps/date-format")

def get_name_format():
    return client.get_int("/apps/gramps/name-format")

def get_researcher_name():
    return client.get_string("/apps/gramps/researcher-name")

def get_researcher_addr():
    return client.get_string("/apps/gramps/researcher-addr")

def get_researcher_city():
    return client.get_string("/apps/gramps/researcher-city")

def get_researcher_state():
    return client.get_string("/apps/gramps/researcher-state")

def get_researcher_country():
    return client.get_string("/apps/gramps/researcher-country")

def get_researcher_postal():
    return client.get_string("/apps/gramps/researcher-postal")

def get_researcher_phone():
    return client.get_string("/apps/gramps/researcher-phone")

def get_researcher_email():
    return client.get_string("/apps/gramps/researcher-email")

def get_nameof():
    return _name_format_list[get_name_format()][1]

def get_display_name():
    return _name_format_list[get_name_format()][2]

def get_display_surname():
    return _name_format_list[get_name_format()][3]

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
    
def sync():
    client.suggest_sync()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_last_file(file):
    client.set_string("/apps/gramps/recent-file",file)
    sync()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_researcher():
    n = get_researcher_name()
    a = get_researcher_addr()
    c = get_researcher_city()
    s = get_researcher_state()
    ct = get_researcher_country()
    p = get_researcher_postal()
    ph = get_researcher_phone()
    e = get_researcher_email()

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
        client.set_string(self.tag,val)

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
        client.set_int(self.tag,val)

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
        client.set_bool(self.tag,val)
        

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
        client.set_string(self.tag,val)
        

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
            "on_object_toggled" : self.on_object_toggled,
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
        for (name,list) in panellist:
            node = self.store.insert_after(None, prev)
            self.store.set(node,0,name)
            next = None
            for (subname,tab) in list:
                next = self.store.insert_after(node,next)
                ilist.append((next,tab))
                self.store.set(next,0,subname)
        for next,tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab
        
    def build(self):
        auto = self.top.get_widget("autoload")
        idedit = self.top.get_widget("gid_edit")
#        cap = self.top.get_widget('capitalize')
        index_vis = self.top.get_widget("show_child_id")
        lds = self.top.get_widget("uselds")
        mr = self.top.get_widget("mediaref")
        mc = self.top.get_widget("mediacopy")
        dg = self.top.get_widget("globalprop")
        dl = self.top.get_widget("localprop")
        cal = self.top.get_widget("calendar")

        auto.set_active(get_autoload())
        lds.set_active(get_uselds())
        if get_media_reference():
            mr.set_active(1)
        else:
            mc.set_active(1)
        dg.set_active(get_media_global())
        dl.set_active(get_media_local())
        cal.set_active(get_calendar())
        idedit.set_active(get_id_edit())
#        cap.set_active(capitalize)
        index_vis.set_active(get_index_visible())

        self.top.get_widget("iprefix").set_text(get_iprefix())
        self.top.get_widget("oprefix").set_text(get_oprefix())
        self.top.get_widget("fprefix").set_text(get_fprefix())
        self.top.get_widget("sprefix").set_text(get_sprefix())
        self.top.get_widget("pprefix").set_text(get_pprefix())

        if get_statusbar() == 0 or get_statusbar() == 1:
            self.top.get_widget("stat2").set_active(1)
        else:
            self.top.get_widget("stat3").set_active(1)

        self.top.get_widget("tooloptmenu").set_history(get_toolbar())

        if get_default_view() == 0:
            self.top.get_widget('pvbutton').set_active(1)
        else:
            self.top.get_widget('fvbutton').set_active(1)

        if get_family_view() == 0:
            self.top.get_widget('familyview1').set_active(1)
        else:
            self.top.get_widget('familyview2').set_active(1)

        self.top.get_widget('usetips').set_active(get_usetips())

        paper_obj = self.top.get_widget("paper_size")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(PaperMenu.paper_sizes)):
            name = PaperMenu.paper_sizes[index].get_name()
            if name == get_paper_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.connect("activate", self.on_format_toggled)
            item.show()
            menu.append(item)
        menu.set_active(choice)
        paper_obj.set_menu(menu)

        lastnamegen_obj = self.top.get_widget("lastnamegen")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(_surname_styles)):
            name = _surname_styles[index]
            item = gtk.MenuItem(name)
            item.set_data(DATA,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            menu.append(item)
        menu.set_active(get_lastnamegen())
        lastnamegen_obj.set_menu(menu)

        self.osubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_text_doc_list():
            if name == get_output_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.connect("activate", self.on_format_toggled)
            item.show()
            self.osubmenu.append(item)
            index = index + 1
        self.osubmenu.set_active(choice)
        self.ofmt.set_menu(self.osubmenu)

        self.gsubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_draw_doc_list():
            if name == get_goutput_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.connect("activate", self.on_format_toggled)
            item.show()
            self.gsubmenu.append(item)
            index = index + 1
        self.gsubmenu.set_active(choice)
        self.gfmt.set_menu(self.gsubmenu)

        date_option = self.top.get_widget("date_format")
        date_menu = gtk.Menu()
        for index in range(0,len(_date_format_list)):
            item = gtk.MenuItem(_date_format_list[index])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            date_menu.append(item)
        date_menu.set_active(Calendar.get_format_code())
        date_option.set_menu(date_menu)

        date_entry = self.top.get_widget("date_entry_format")
        date_menu = gtk.Menu()
        for index in range(0,len(_date_entry_list)):
            item = gtk.MenuItem(_date_entry_list[index])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            date_menu.append(item)
        date_menu.set_active(Calendar.Calendar.ENTRYCODE)
        date_entry.set_menu(date_menu)

        name_option = self.top.get_widget("name_format")
        name_menu = gtk.Menu()
        for index in range(0,len(_name_format_list)):
            name_tuple = _name_format_list[index]
            item = gtk.MenuItem(name_tuple[0])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            name_menu.append(item)
        name_menu.set_active(get_name_format())
        name_option.set_menu(name_menu)

        self.top.get_widget("resname").set_text(get_researcher_name())
        self.top.get_widget("resaddr").set_text(get_researcher_addr())
        self.top.get_widget("rescity").set_text(get_researcher_city())
        self.top.get_widget("resstate").set_text(get_researcher_state())
        self.top.get_widget("rescountry").set_text(get_researcher_country())
        self.top.get_widget("respostal").set_text(get_researcher_postal())
        self.top.get_widget("resphone").set_text(get_researcher_phone())
        self.top.get_widget("resemail").set_text(get_researcher_email())

        self.top.get_widget("repdir").gtk_entry().set_text(get_report_dir())
        self.top.get_widget("htmldir").gtk_entry().set_text(get_web_dir())

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
        store,iter = self.selection.get_selected()
        if iter:
            path = store.get_path(iter)
        if iter and self.imap.has_key(path):
            self.panel.set_current_page(self.imap[path])
        
    def on_propertybox_help(self,obj):
        gnome.help_display('gramps-manual','gramps-prefs')

    def on_close_clicked(self,obj):
        self.save_data()
        Utils.destroy_passed_object(self.window)
    
    def on_propertybox_apply(self,obj):
        self.save_data()

    def save_data(self):
    
        autoload = self.top.get_widget("autoload").get_active()
        uselds = self.top.get_widget("uselds").get_active()
        mediaref = self.top.get_widget("mediaref").get_active()
        localprop = self.top.get_widget("localprop").get_active()
        globalprop = self.top.get_widget("globalprop").get_active()
        calendar = self.top.get_widget("calendar").get_active()
        id_edit = self.top.get_widget("gid_edit").get_active()
        
        index_visible = self.top.get_widget("show_child_id").get_active()
        paper_obj = self.top.get_widget("paper_size").get_menu().get_active()

        output_obj = self.osubmenu.get_active()
        goutput_obj = self.gsubmenu.get_active()

        if self.top.get_widget("stat2").get_active():
            status_bar = 1
        else:
            status_bar = 2

        save_toolbar = self.top.get_widget("tooloptmenu").get_history()
        gnome_toolbar_str = client.get_string("/desktop/gnome/interface/toolbar_style")
        try:
            gnome_toolbar = eval("gtk.TOOLBAR_%s" % 
                            gnome_toolbar_str.replace('-','_').upper())
        except:
            gnome_toolbar = 2

        if save_toolbar == 5:
            toolbar = gnome_toolbar
        else:
            toolbar = save_toolbar

        defaultview = not self.top.get_widget("pvbutton").get_active()
        familyview = not self.top.get_widget("familyview1").get_active()
        usetips = self.top.get_widget("usetips").get_active()

        iprefix = unicode(self.top.get_widget("iprefix").get_text())
        if iprefix == "":
            iprefix = "I%04d"
        sprefix = unicode(self.top.get_widget("sprefix").get_text())
        if sprefix == "":
            sprefix = "S%04d"
        oprefix = unicode(self.top.get_widget("oprefix").get_text())
        if oprefix == "":
            oprefix = "O%04d"
        fprefix = unicode(self.top.get_widget("fprefix").get_text())
        if fprefix == "":
            fprefix = "F%04d"
        pprefix = unicode(self.top.get_widget("pprefix").get_text())
        if pprefix == "":
            pprefix = "P%04d"

        repdir_temp = self.top.get_widget("repdir").get_full_path(1)
        if repdir_temp != None and os.path.isdir(repdir_temp):
            report_dir = os.path.normpath(repdir_temp) + os.sep

        webdir_temp = self.top.get_widget("htmldir").get_full_path(1)
        if webdir_temp != None and os.path.isdir(webdir_temp):
            web_dir = os.path.normpath(webdir_temp) + os.sep

        paper_preference = paper_obj.get_data(DATA)
        output_preference = output_obj.get_data(DATA)
        goutput_preference = goutput_obj.get_data(DATA)
    
        client.set_bool("/apps/gramps/use-lds",uselds)
        client.set_bool("/apps/gramps/make-reference",mediaref)
        client.set_bool("/apps/gramps/media-global",globalprop)
        client.set_bool("/apps/gramps/media-local",localprop)
        client.set_bool("/apps/gramps/show-calendar",calendar)
        client.set_bool("/apps/gramps/id-edit",id_edit)
        client.set_bool("/apps/gramps/index-visible",index_visible)
        client.set_int("/apps/gramps/statusbar",status_bar)
        client.set_int("/apps/gramps/toolbar",save_toolbar)
        client.set_int("/apps/gramps/defaultview",defaultview)
        client.set_int("/apps/gramps/familyview",familyview)
        client.set_bool("/apps/gramps/use-tips",usetips)
        client.set_string("/apps/gramps/paper-preference",paper_preference)
        client.set_string("/apps/gramps/output-preference",output_preference)
        client.set_string("/apps/gramps/goutput-preference",goutput_preference)
        client.set_bool("/apps/gramps/autoload",autoload)
        
        client.set_string("/apps/gramps/report-directory",report_dir)
        client.set_string("/apps/gramps/website-directory",web_dir)
        client.set_string("/apps/gramps/iprefix",iprefix)
        client.set_string("/apps/gramps/fprefix",fprefix)
        client.set_string("/apps/gramps/pprefix",pprefix)
        client.set_string("/apps/gramps/oprefix",oprefix)
        client.set_string("/apps/gramps/sprefix",sprefix)
        
        # search for the active date format selection
        format_menu = self.top.get_widget("date_format").get_menu()
        active = format_menu.get_active().get_data(INDEX)
        
        Calendar.set_format_code(active)
        client.set_int("/apps/gramps/date-format",active)
        
        format_menu = self.top.get_widget("date_entry_format").get_menu()
        entry_active = format_menu.get_active().get_data(INDEX)
        
        Calendar.Calendar.ENTRYCODE = entry_active
        client.set_int("/apps/gramps/date-entry",entry_active)
        
        # get the name format
        
        format_menu = self.top.get_widget("name_format").get_menu()
        active_name = format_menu.get_active().get_data(INDEX)
        
        nameof = _name_format_list[active_name][1]
        display_name = _name_format_list[active_name][2]
        display_surname = _name_format_list[active_name][3]
        client.set_int("/apps/gramps/nameFormat",active_name)

        format_menu = self.top.get_widget("lastnamegen").get_menu()
        lastnamegen = format_menu.get_active().get_data(DATA)
        client.set_int("/apps/gramps/surname-guessing",lastnamegen)
        
        name = unicode(self.top.get_widget("resname").get_text())
        addr = unicode(self.top.get_widget("resaddr").get_text())
        city = unicode(self.top.get_widget("rescity").get_text())
        state = unicode(self.top.get_widget("resstate").get_text())
        country = unicode(self.top.get_widget("rescountry").get_text())
        postal = unicode(self.top.get_widget("respostal").get_text())
        phone = unicode(self.top.get_widget("resphone").get_text())
        email = unicode(self.top.get_widget("resemail").get_text())
        
        client.set_string("/apps/gramps/researcher-name",name)
        client.set_string("/apps/gramps/researcher-addr",addr)
        client.set_string("/apps/gramps/researcher-city",city)
        client.set_string("/apps/gramps/researcher-state",state)
        client.set_string("/apps/gramps/researcher-country",country)
        client.set_string("/apps/gramps/researcher-postal",postal)
        client.set_string("/apps/gramps/researcher-phone",phone)
        client.set_string("/apps/gramps/researcher-email",email)
        
        for o in self.ext_list:
            o.set()

        # update the config file
        
        sync()

    def on_object_toggled(self,obj):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        if self.built:
            self.on_propertybox_apply(obj)

    def on_format_toggled(self,obj):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        if self.built:
            self.on_propertybox_apply(obj)

#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    GrampsPreferences(db)

_view_str = "/apps/gramps/view"
_toolbar_str = "/apps/gramps/toolbar-on"

def save_view(val):
    client.set_bool(_view_str, not val)
    sync()

def get_view():
    return not client.get_bool(_view_str)

def save_filter(val):
    client.set_bool("/apps/gramps/filter",val)

def get_filter():
    return client.get_bool("/apps/gramps/filter")

def save_toolbar_on(val):
    client.set_bool(_toolbar_str, not val)
    sync()

def get_toolbar_on():
    return not client.get_bool(_toolbar_str)

def save_report_dir(val):
    client.set_string("apps/gramps/report-directory",val)

def save_web_dir(val):
    client.set_string("apps/gramps/web-directory",val)
