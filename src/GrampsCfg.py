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

import PaperMenu
import Plugins
import Calendar

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

from gettext import gettext as _

client = gconf.client_get_default()
client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)

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
      ( _("Media Objects"), 9),
      ( _("GRAMPS internal IDs"), 10),
      ( _("Revision Control"),2)]),
    (_("Display"),
     [( _("General"), 5),
      ( _("Dates and Calendars"), 6),
      ( _("Toolbar and Statusbar"), 4)]),
    (_("Usage"),
     [( _("Find"), 3),
      ( _("Report Preferences"), 8),
      ( _("Researcher Information"), 7),
      ( _("Data Guessing"), 11)]),
    ]


#-------------------------------------------------------------------------
#
# Visible globals
#
#-------------------------------------------------------------------------

iprefix       = "I%04d"
oprefix       = "O%04d"
sprefix       = "S%04d"
pprefix       = "P%04d"
fprefix       = "F%04d"
autoload      = 0
autosave_int  = 0
uselds        = 0
autocomp      = 1
usevc         = 0
vc_comment    = 0
uncompress    = 0
lastfile      = None
nameof        = Utils.normal_name
display_name  = Utils.normal_name
display_surname = lambda x : x.get_surname()
status_bar    = 1
toolbar       = gtk.TOOLBAR_BOTH
save_toolbar  = gtk.TOOLBAR_BOTH
calendar      = 0
paper_preference = ""
output_preference = ""
goutput_preference = ""
lastnamegen   = None
report_dir    = "./"
web_dir       = "./"
db_dir        = "./"
id_edit       = 0
index_visible = 0
mediaref      = 1
globalprop    = 1
localprop     = 1
defaultview   = 0
familyview    = 0

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------
_name_format  = 0
_callback     = None

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
INDEX         = "i"
OBJECT        = "o"
DATA          = "d"

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
def loadConfig(call):
    global autoload
    global autosave_int
    global uselds
    global autocomp
    global calendar
    global usevc
    global iprefix
    global fprefix
    global pprefix
    global oprefix
    global sprefix
    global vc_comment
    global uncompress
    global id_edit
    global index_visible
    global lastfile
    global nameof
    global display_name
    global display_surname
    global _name_format
    global _callback
    global paper_preference
    global output_preference
    global goutput_preference
    global lastnamegen
    global report_dir
    global web_dir
    global db_dir
    global status_bar
    global toolbar
    global save_toolbar
    global mediaref
    global globalprop
    global localprop
    global defaultview
    global familyview
    
    _callback = call
    lastfile = get_string("/apps/gramps/last-file")
    uselds = get_bool("/apps/gramps/use-lds")
    ac = get_bool("/apps/gramps/disable-auto-complete",0)
    mediaref = get_bool("/apps/gramps/make-reference",1)
    globalprop = get_bool("/apps/gramps/media-global",1)
    localprop = get_bool("/apps/gramps/media-local",1)
    calendar = get_bool("/apps/gramps/show-calendar")
    usevc = get_bool("/apps/gramps/version-control")
    vc_comment = get_bool("/apps/gramps/use-comment")
    uncompress = get_bool("/apps/gramps/dont-compress-xml")
    id_edit = get_bool("/apps/gramps/id-edit")
    index_visible = get_bool("/apps/gramps/index-visible")
    status_bar = get_int("/apps/gramps/statusbar")
    gnome_toolbar_str = get_string("/desktop/gnome/interface/toolbar_style","BOTH")

    try:
        gnome_toolbar = eval("gtk.TOOLBAR_%s" % 
                        gnome_toolbar_str.replace('-','_').upper())
    except:
        gnome_toolbar = 2
        
    save_toolbar = get_int("/apps/gramps/toolbar",5)
    if save_toolbar == 5:
        toolbar = gnome_toolbar
    else:
        toolbar = save_toolbar
    defaultview = get_int("/apps/gramps/defaultview")
    familyview = get_int("/apps/gramps/familyview")
    
    autoload = get_bool("/apps/gramps/autoload",0)
    autosave_int = get_int("/apps/gramps/auto-save-interval")
    dateFormat = get_int("/apps/gramps/date-format")
    dateEntry = get_int("/apps/gramps/date-entry")
    paper_preference = get_string("/apps/gramps/paper-preference")
    output_preference = get_string("/apps/gramps/output-preference")
    goutput_preference = get_string("/apps/gramps/goutput-preference")
    lastnamegen = get_int("/apps/gramps/surname-guessing")
    _name_format = get_int("/apps/gramps/nameFormat")

    iprefix = get_string("/apps/gramps/iprefix")
    fprefix = get_string("/apps/gramps/fprefix")
    sprefix = get_string("/apps/gramps/sprefix")
    oprefix = get_string("/apps/gramps/oprefix")
    pprefix = get_string("/apps/gramps/pprefix")

    report_dir = get_string("/apps/gramps/report-directory")
    web_dir = get_string("/apps/gramps/website-directory")
    db_dir = get_string("/apps/gramps/db-directory")

    if report_dir == None:
        report_dir = "./"
    else:
        report_dir = os.path.normpath(report_dir) + os.sep

    if web_dir == None:
        web_dir = "./"
    else:
        web_dir = os.path.normpath(web_dir) + os.sep
        
    if db_dir == None:
        db_dir = "./"
    else:
        db_dir = os.path.normpath(db_dir) + os.sep

    if paper_preference == None:
        paper_preference = "Letter"

    if output_preference == None:
        output_preference = ""

    if goutput_preference == None:
        goutput_preference = ""
        
    if iprefix == None:
        iprefix = "I"
    if fprefix == None:
        fprefix = "F"
    if sprefix == None:
        sprefix = "S"
    if pprefix == None:
        pprefix = "P"
    if oprefix == None:
        oprefix = "O"

    autocomp = not ac
        
    Calendar.set_format_code(dateFormat)
    Calendar.Calendar.ENTRYCODE = dateEntry

    nameof = _name_format_list[_name_format][1]
    display_name = _name_format_list[_name_format][2]
    display_surname = _name_format_list[_name_format][3]

    make_path(os.path.expanduser("~/.gramps"))
    make_path(os.path.expanduser("~/.gramps/filters"))
    make_path(os.path.expanduser("~/.gramps/plugins"))
    make_path(os.path.expanduser("~/.gramps/templates"))

def get_string(value,defval=""):
    v = client.get_string(value)
    if client.get(value):
        return v
    else:
        return defval

def get_bool(key,defval=0):
    v = client.get_bool(key)
    if client.get(key):
        return v
    else:
        return defval

def get_int(key,defval=0):
    v = client.get_int(key)
    if client.get(key):
        return v
    else:
        return defval

def set_int(key,value):
    client.set_int(key,value)

def set_bool(key,value):
    client.set_bool(key,value)

def set_string(key,value):
    client.set_string(key,value)

def sync():
    client.suggest_sync()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_last_file(file):
    set_string("/apps/gramps/last-file",file)
    sync()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_researcher():
    n = get_string("/apps/gramps/researcher-name")
    a = get_string("/apps/gramps/researcher-addr")
    c = get_string("/apps/gramps/researcher-city")
    s = get_string("/apps/gramps/researcher-state")
    ct = get_string("/apps/gramps/researcher-country")
    p = get_string("/apps/gramps/researcher-postal")
    ph = get_string("/apps/gramps/researcher-phone")
    e = get_string("/apps/gramps/researcher-email")

    owner = RelLib.Researcher()
    owner.set(n,a,c,s,ct,p,ph,e)
    return owner
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def get_config_text(panel,key):
    val = get_string("/apps/gramps/%s/%s" % (panel,key))
    if val:
        return val
    else:
        return ""

def get_config_bool(panel,key):
    return get_bool("/apps/gramps/%s/%s" % (panel,key))

def get_config_int(panel,key):
    return get_int("/apps/gramps/%s/%s" % (panel,key))

ext_items = []

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
        set_string(self.tag,val)

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
        set_int(self.tag,val)

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
        set_bool(self.tag,val)
        

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
        set_string(self.tag,val)
        

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
        asave_int = self.top.get_widget("autosave_interval")
        idedit = self.top.get_widget("gid_edit")
#        cap = self.top.get_widget('capitalize')
        index_vis = self.top.get_widget("show_child_id")
        lds = self.top.get_widget("uselds")
        ac = self.top.get_widget("autocomp")
        mr = self.top.get_widget("mediaref")
        mc = self.top.get_widget("mediacopy")
        dg = self.top.get_widget("globalprop")
        dl = self.top.get_widget("localprop")
        cal = self.top.get_widget("calendar")
        vc = self.top.get_widget("use_vc")
        vcom = self.top.get_widget("vc_comment")
        compress = self.top.get_widget("uncompress")

        auto.set_active(autoload)
        asave_int.set_value(int(autosave_int))
        lds.set_active(uselds)
        ac.set_active(autocomp)
        if mediaref:
            mr.set_active(1)
        else:
            mc.set_active(1)
        dg.set_active(globalprop)
        dl.set_active(localprop)
        cal.set_active(calendar)
        vc.set_active(usevc)
        vcom.set_active(vc_comment)
        compress.set_active(uncompress)
        idedit.set_active(id_edit)
#        cap.set_active(capitalize)
        index_vis.set_active(index_visible)

        self.top.get_widget("iprefix").set_text(iprefix)
        self.top.get_widget("oprefix").set_text(oprefix)
        self.top.get_widget("fprefix").set_text(fprefix)
        self.top.get_widget("sprefix").set_text(sprefix)
        self.top.get_widget("pprefix").set_text(pprefix)

        if status_bar == 0 or status_bar == 1:
            self.top.get_widget("stat2").set_active(1)
        else:
            self.top.get_widget("stat3").set_active(1)

        self.top.get_widget("tooloptmenu").set_history(save_toolbar)

        if defaultview == 0:
            self.top.get_widget('pvbutton').set_active(1)
        else:
            self.top.get_widget('fvbutton').set_active(1)

        if familyview == 0:
            self.top.get_widget('familyview1').set_active(1)
        else:
            self.top.get_widget('familyview2').set_active(1)

        paper_obj = self.top.get_widget("paper_size")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(PaperMenu.paper_sizes)):
            name = PaperMenu.paper_sizes[index].get_name()
            if name == paper_preference:
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
        menu.set_active(lastnamegen)
        lastnamegen_obj.set_menu(menu)

        self.osubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_text_doc_list():
            if name == output_preference:
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
            if name == goutput_preference:
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
        name_menu.set_active(_name_format)
        name_option.set_menu(name_menu)

        cname = get_string("/apps/gramps/researcher-name")
        caddr = get_string("/apps/gramps/researcher-addr")
        ccity = get_string("/apps/gramps/researcher-city")
        cstate = get_string("/apps/gramps/researcher-state")
        ccountry = get_string("/apps/gramps/researcher-country")
        cpostal = get_string("/apps/gramps/researcher-postal")
        cphone = get_string("/apps/gramps/researcher-phone")
        cemail = get_string("/apps/gramps/researcher-email")

        self.top.get_widget("resname").set_text(cname)
        self.top.get_widget("resaddr").set_text(caddr)
        self.top.get_widget("rescity").set_text(ccity)
        self.top.get_widget("resstate").set_text(cstate)
        self.top.get_widget("rescountry").set_text(ccountry)
        self.top.get_widget("respostal").set_text(cpostal)
        self.top.get_widget("resphone").set_text(cphone)
        self.top.get_widget("resemail").set_text(cemail)

        self.top.get_widget("dbdir").gtk_entry().set_text(db_dir)
        self.top.get_widget("repdir").gtk_entry().set_text(report_dir)
        self.top.get_widget("htmldir").gtk_entry().set_text(web_dir)

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
        _callback(1)

    def save_data(self):
        global nameof
        global display_name
        global display_surname
        global uselds
        global autocomp
        global autosave_int
        global mediaref
        global globalprop
        global localprop
        global calendar
        global usevc
        global iprefix
        global fprefix
        global pprefix
        global sprefix
        global oprefix
        global vc_comment
        global uncompress
        global id_edit
        global index_visible
        global status_bar
        global toolbar
        global save_toolbar
        global defaultview
        global familyview
        global paper_preference
        global output_preference
        global goutput_preference
        global report_dir
        global web_dir
        global db_dir
        global lastnamegen
        global autoload
    
        autoload = self.top.get_widget("autoload").get_active()
        autosave_int = self.top.get_widget("autosave_interval").get_value_as_int()
        uselds = self.top.get_widget("uselds").get_active()
        autocomp = self.top.get_widget("autocomp").get_active()
        mediaref = self.top.get_widget("mediaref").get_active()
        localprop = self.top.get_widget("localprop").get_active()
        globalprop = self.top.get_widget("globalprop").get_active()
        calendar = self.top.get_widget("calendar").get_active()
        usevc = self.top.get_widget("use_vc").get_active()
        vc_comment = self.top.get_widget("vc_comment").get_active()
        uncompress = self.top.get_widget("uncompress").get_active()
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
        gnome_toolbar_str = get_string("/desktop/gnome/interface/toolbar_style",'BOTH')
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

        dbdir_temp = self.top.get_widget("dbdir").get_full_path(1)
        if dbdir_temp != None and os.path.isdir(dbdir_temp):
            db_dir = os.path.normpath(dbdir_temp) + os.sep

        repdir_temp = self.top.get_widget("repdir").get_full_path(1)
        if repdir_temp != None and os.path.isdir(repdir_temp):
            report_dir = os.path.normpath(repdir_temp) + os.sep

        webdir_temp = self.top.get_widget("htmldir").get_full_path(1)
        if webdir_temp != None and os.path.isdir(webdir_temp):
            web_dir = os.path.normpath(webdir_temp) + os.sep

        paper_preference = paper_obj.get_data(DATA)
        output_preference = output_obj.get_data(DATA)
        goutput_preference = goutput_obj.get_data(DATA)
    
        set_bool("/apps/gramps/use-lds",uselds)
        set_bool("/apps/gramps/disable-auto-complete",not autocomp)
        set_bool("/apps/gramps/make-reference",mediaref)
        set_bool("/apps/gramps/media-global",globalprop)
        set_bool("/apps/gramps/media-local",localprop)
        set_bool("/apps/gramps/show-calendar",calendar)
        set_bool("/apps/gramps/version-control",usevc)
        set_bool("/apps/gramps/use-comment",vc_comment)
        set_bool("/apps/gramps/dont-compress-xml",uncompress)
        set_bool("/apps/gramps/id-edit",id_edit)
        set_bool("/apps/gramps/index-visible",index_visible)
        set_int("/apps/gramps/statusbar",status_bar)
        set_int("/apps/gramps/toolbar",save_toolbar)
        set_int("/apps/gramps/defaultview",defaultview)
        set_int("/apps/gramps/familyview",familyview)
        set_string("/apps/gramps/paper-preference",paper_preference)
        set_string("/apps/gramps/output-preference",output_preference)
        set_string("/apps/gramps/goutput-preference",goutput_preference)
        set_bool("/apps/gramps/autoload",autoload)
        set_int("/apps/gramps/auto-save-interval",autosave_int)
        
        if autosave_int != 0:
            Utils.enable_autosave(None,autosave_int)
        else:
            Utils.disable_autosave()
        
        set_string("/apps/gramps/report-directory",report_dir)
        set_string("/apps/gramps/website-directory",web_dir)
        set_string("/apps/gramps/db-directory",db_dir)
        set_string("/apps/gramps/iprefix",iprefix)
        set_string("/apps/gramps/fprefix",fprefix)
        set_string("/apps/gramps/pprefix",pprefix)
        set_string("/apps/gramps/oprefix",oprefix)
        set_string("/apps/gramps/sprefix",sprefix)
        
        # search for the active date format selection
        format_menu = self.top.get_widget("date_format").get_menu()
        active = format_menu.get_active().get_data(INDEX)
        
        Calendar.set_format_code(active)
        set_int("/apps/gramps/date-format",active)
        
        format_menu = self.top.get_widget("date_entry_format").get_menu()
        entry_active = format_menu.get_active().get_data(INDEX)
        
        Calendar.Calendar.ENTRYCODE = entry_active
        set_int("/apps/gramps/date-entry",entry_active)
        
        # get the name format
        
        format_menu = self.top.get_widget("name_format").get_menu()
        active_name = format_menu.get_active().get_data(INDEX)
        
        nameof = _name_format_list[active_name][1]
        display_name = _name_format_list[active_name][2]
        display_surname = _name_format_list[active_name][3]
        set_int("/apps/gramps/nameFormat",active_name)

        format_menu = self.top.get_widget("lastnamegen").get_menu()
        lastnamegen = format_menu.get_active().get_data(DATA)
        set_int("/apps/gramps/surname-guessing",lastnamegen)
        
        name = unicode(self.top.get_widget("resname").get_text())
        addr = unicode(self.top.get_widget("resaddr").get_text())
        city = unicode(self.top.get_widget("rescity").get_text())
        state = unicode(self.top.get_widget("resstate").get_text())
        country = unicode(self.top.get_widget("rescountry").get_text())
        postal = unicode(self.top.get_widget("respostal").get_text())
        phone = unicode(self.top.get_widget("resphone").get_text())
        email = unicode(self.top.get_widget("resemail").get_text())
        
        set_string("/apps/gramps/researcher-name",name)
        set_string("/apps/gramps/researcher-addr",addr)
        set_string("/apps/gramps/researcher-city",city)
        set_string("/apps/gramps/researcher-state",state)
        set_string("/apps/gramps/researcher-country",country)
        set_string("/apps/gramps/researcher-postal",postal)
        set_string("/apps/gramps/researcher-phone",phone)
        set_string("/apps/gramps/researcher-email",email)
        
        self.db.set_iprefix(iprefix)
        self.db.set_fprefix(fprefix)
        self.db.set_sprefix(sprefix)
        self.db.set_oprefix(oprefix)
        self.db.set_pprefix(pprefix)
        
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
    set_bool(_view_str, not val)
    sync()

def get_view():
    return not client.get_bool(_view_str)

def save_filter(val):
    set_bool("/apps/gramps/filter",val)

def get_filter():
    return get_bool("/apps/gramps/filter")

def save_toolbar_on(val):
    set_bool(_toolbar_str, not val)
    sync()

def get_toolbar_on():
    return not client.get_bool(_toolbar_str)
