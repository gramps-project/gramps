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
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os

import PaperMenu

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import GTK
import gtk
import libglade
from gnome.config import get_string, get_bool, get_int, set_string, sync, set_bool, set_int

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from Date import *

import const
import utils
import ListColors

from intl import gettext
_ = gettext

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
    (_("Firstname Surname"), utils.normal_name),
    (_("Surname, Firstname"), utils.phonebook_name),
    ]

panellist = [
    (_("Database"),
     [( _("General"), 1),
      ( _("Dates and Calendars"), 7),
      ( _("Media Objects"), 10),
      ( _("GRAMPS internal IDs"), 11),
      ( _("Revision Control"),2)]),
    (_("Display"),
     [( _("General"), 5),
      ( _("Tool and Status Bars"), 4),
      ( _("List Colors"), 6)]),
    (_("Usage"),
     [( _("Find"), 3),
      ( _("Report Preferences"), 9),
      ( _("Researcher Information"), 8),
      ( _("Data Guessing"), 12)]),
    ]


#-------------------------------------------------------------------------
#
# Visible globals
#
#-------------------------------------------------------------------------

owner         = Researcher()
prefsTop      = None
iprefix       = "I"
oprefix       = "O"
sprefix       = "S"
pprefix       = "P"
fprefix       = "F"
autoload      = 0
autosave_int  = 0
usetabs       = 0
uselds        = 0
autocomp      = 1
usevc         = 0
vc_comment    = 0
uncompress    = 0
show_detail   = 0
hide_altnames = 0
lastfile      = None
nameof        = utils.normal_name
display_attr  = 0
attr_name     = ""
status_bar    = 0
toolbar       = 2
calendar      = 0
paper_preference = None
output_preference = None
lastnamegen   = None
report_dir    = "./"
web_dir       = "./"
db_dir        = "./"
id_visible    = 0
id_edit       = 0
index_visible = 0
mediaref      = 1
globalprop    = 1
localprop     = 1

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------
_name_format  = 0
_callback     = None
_druid        = None

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
ODDFGCOLOR    = "oddfg"
ODDBGCOLOR    = "oddbg"
EVENFGCOLOR   = "evenfg"
EVENBGCOLOR   = "evenbg"
ANCESTORFGCOLOR = "ancestorfg"
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
    global owner
    global usetabs
    global uselds
    global autocomp
    global calendar
    global usevc
    global iprefix, fprefix, pprefix, oprefix, sprefix
    global vc_comment
    global uncompress
    global id_visible
    global id_edit
    global index_visible
    global show_detail
    global hide_altnames
    global lastfile
    global nameof
    global display_attr
    global attr_name
    global _druid
    global _name_format
    global _callback
    global paper_preference
    global output_preference
    global lastnamegen
    global report_dir
    global web_dir
    global db_dir
    global status_bar
    global toolbar
    global mediaref
    global globalprop
    global localprop

    _callback = call
    lastfile = get_string("/gramps/data/LastFile")
    usetabs = get_bool("/gramps/config/UseTabs")
    uselds = get_bool("/gramps/config/UseLDS")
    ac = get_bool("/gramps/config/DisableAutoComplete")
    mediaref = get_bool("/gramps/config/MakeReference")
    globalprop = get_bool("/gramps/config/DisplayGlobal")
    localprop = get_bool("/gramps/config/DisplayLocal")
    calendar = get_bool("/gramps/config/ShowCalendar")
    usevc = get_bool("/gramps/config/UseVersionControl")
    vc_comment = get_bool("/gramps/config/UseComment")
    uncompress = get_bool("/gramps/config/DontCompressXML")
    id_visible = get_bool("/gramps/config/IdVisible")
    id_edit = get_bool("/gramps/config/IdEdit")
    index_visible = get_bool("/gramps/config/IndexVisible")
    show_detail = get_bool("/gramps/config/ShowDetail")
    status_bar = get_int("/gramps/config/StatusBar")
    t = get_int("/gramps/config/ToolBar")
    if t == 0:
        toolbar = 2
    else:
        toolbar = t-1
    display_attr = get_bool("/gramps/config/DisplayAttr")
    attr_name = get_string("/gramps/config/DisplayAttrName")
    
    hide_altnames = get_bool("/gramps/config/DisplayAltNames")
    autoload = get_bool("/gramps/config/autoLoad")
    autosave_int = get_int("/gramps/config/autoSaveInterval")
    dateFormat = get_int("/gramps/config/dateFormat")
    dateEntry = get_int("/gramps/config/dateEntry")
    paper_preference = get_string("/gramps/config/paperPreference")
    output_preference = get_string("/gramps/config/outputPreference")
    lastnamegen = get_int("/gramps/config/surnameGuessing")
    _name_format = get_int("/gramps/config/nameFormat")

    iprefix = get_string("/gramps/config/iprefix")
    fprefix = get_string("/gramps/config/fprefix")
    sprefix = get_string("/gramps/config/sprefix")
    oprefix = get_string("/gramps/config/oprefix")
    pprefix = get_string("/gramps/config/pprefix")

    report_dir = get_string("/gramps/config/ReportDirectory")
    web_dir = get_string("/gramps/config/WebsiteDirectory")
    db_dir = get_string("/gramps/config/DbDirectory")

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

    name = get_string("/gramps/researcher/name")
    addr = get_string("/gramps/researcher/addr")
    city = get_string("/gramps/researcher/city")
    state = get_string("/gramps/researcher/state")
    country = get_string("/gramps/researcher/country")
    postal = get_string("/gramps/researcher/postal")
    phone = get_string("/gramps/researcher/phone")
    email = get_string("/gramps/researcher/email")

    en = get_bool("/gramps/color/enableColors")
    if en == None:
        en = 0

    ListColors.set_enable(en)

    ListColors.oddfg = get_config_color(ODDFGCOLOR,(0,0,0))
    ListColors.oddbg = get_config_color(ODDBGCOLOR,(0xffff,0xffff,0xffff))
    ListColors.evenfg = get_config_color(EVENFGCOLOR,(0,0,0))
    ListColors.evenbg = get_config_color(EVENBGCOLOR,(0xffff,0xffff,0xffff))
    ListColors.ancestorfg = get_config_color(ANCESTORFGCOLOR,(0,0,0))

    if paper_preference == None:
        paper_preference = "Letter"

    if output_preference == None:
        output_preference = "OpenOffice"
        
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

    if display_attr == None:
        display_attr = 0

    if attr_name == None:
        attr_name = ""

    if autoload == None:
        autoload = 1
    if autosave_int == None:
        autosave_int = 0
    if mediaref == None:
        mediaref = 1
    if globalprop == None:
        globalprop = 1
    if localprop == None:
        localprop =1 
    if usetabs == None:
        usetabs = 0
    if uselds == None:
        uselds = 0
    if ac == None:
        autocomp = 1
    else:
        autocomp = not ac
        
    if calendar == None:
        calendar = 0
    if usevc == None:
        usevc = 0
    if vc_comment == None:
        vc_comment = 0
    if uncompress == None:
        uncompress = 0
    if id_visible == None:
        id_visible = 0
    if id_edit == None:
        id_edit = 0
    if index_visible == None:
        index_visible = 0
    if show_detail == None:
        show_detail = 0
    if status_bar == None:
        status_bar = 0
    if toolbar == None:
        toolbar = 2
    if hide_altnames == None:
        hide_altnames = 0
    if dateFormat == None:
        dateFormat = 0
    if dateEntry == None:
        dateEntry = 0

    set_format_code(dateFormat)
    Date.entryCode = dateEntry

    if lastnamegen == None or lastnamegen == 0:
        lastnamegen = 0

    if _name_format == None or _name_format == 0:
        _name_format = 0
        nameof = utils.normal_name
    else:
        nameof = utils.phonebook_name
        
    if name == None:
        _druid = libglade.GladeXML(const.configFile,"initDruid")
        _druid.signal_autoconnect({
            "destroy_passed_object" : druid_cancel_clicked,
            "on_initDruid_finish" : on_initDruid_finish
            })
    else:
        owner.set(name,addr,city,state,country,postal,phone,email)
        
    make_path(os.path.expanduser("~/.gramps"))
    make_path(os.path.expanduser("~/.gramps/filters"))
    make_path(os.path.expanduser("~/.gramps/plugins"))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def save_last_file(file):
    set_string("/gramps/data/LastFile",file)
    sync()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_initDruid_finish(obj,b):
    global owner
    
    name = _druid.get_widget("dresname").get_text()
    addr = _druid.get_widget("dresaddr").get_text()
    city = _druid.get_widget("drescity").get_text()
    state = _druid.get_widget("dresstate").get_text()
    country = _druid.get_widget("drescountry").get_text()
    postal = _druid.get_widget("drespostal").get_text()
    phone = _druid.get_widget("dresphone").get_text()
    email = _druid.get_widget("dresemail").get_text()

    owner.set(name,addr,city,state,country,postal,phone,email)
    store_researcher(owner)
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def store_researcher(res):
    set_string("/gramps/researcher/name",res.name)
    set_string("/gramps/researcher/addr",res.addr)
    set_string("/gramps/researcher/city",res.city)
    set_string("/gramps/researcher/state",res.state)
    set_string("/gramps/researcher/country",res.country)
    set_string("/gramps/researcher/postal",res.postal)
    set_string("/gramps/researcher/phone",res.phone)
    set_string("/gramps/researcher/email",res.email)
    sync()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def save_config_color(name,color):
    set_int("/gramps/color/" + name + ".r",color[0])
    set_int("/gramps/color/" + name + ".g",color[1])
    set_int("/gramps/color/" + name + ".b",color[2])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

def get_config_text(panel,key):
    return get_string("/gramps/%s/%s" % (panel,key))

def get_config_bool(panel,key):
    return get_bool("/gramps/%s/%s" % (panel,key))

def get_config_int(panel,key):
    return get_int("/gramps/%s/%s" % (panel,key))

ext_items = []

class ConfigWidget:
    def __init__(self,panel,key,label,default):
        self.p = panel
        self.k = key
        self.l = label
        self.w = None
        self.d = default
        self.tag = "/gramps/%s/%s" % (panel,key)
        
    def set(self):
        pass

class ConfigEntry(ConfigWidget):

    def get_widgets(self):
        l = gtk.GtkLabel(self.l)
        l.show()
        self.w = gtk.GtkEntry()
        self.w.show()
        
        val = get_string(self.tag)
        if val == None:
            self.w.set_text(self.d)
        else:
            self.w.set_text(val)
        return [l,self.w]

    def set(self):
        val = self.w.get_text()
        set_string(self.tag,val)

class ConfigInt(ConfigWidget):

    def get_widgets(self):
        l = gtk.GtkLabel(self.l)
        l.show()
        self.w = gtk.GtkSpinButton(digits=0)
        self.w.show()
        
        val = get_int(self.tag)
        if val == None:
            self.w.set_value(int(self.d))
        else:
            self.w.set_value(val)
        return [l,self.w]

    def set(self):
        val = self.w.get_value_as_int()
        set_int(self.tag,val)

class ConfigCheckbox(ConfigWidget):
    
    def get_widgets(self):
        self.w = gtk.GtkCheckButton(self.l)
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
        
def add_text(category,panel,frame,config_tag,label,default):
    ext_items.append(category,panel,frame,ConfigEntry(panel,config_tag,label,default))

def add_int(category,panel,frame,config_tag,label,default):
    ext_items.append(category,panel,frame,ConfigInt(panel,config_tag,label,default))

def add_checkbox(category,panel,frame,config_tag,label,default):
    ext_items.append(category,panel,frame,ConfigCheckbox(panel,config_tag,label,default))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GrampsPreferences:
    def __init__(self,db):
        self.db = db
        self.top = libglade.GladeXML(const.prefsFile,"preferences")
        self.top.signal_autoconnect({
            "on_close_clicked" : self.on_close_clicked,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_apply_clicked" : self.on_propertybox_apply,
            "on_help_clicked" : self.on_propertybox_help,
            "on_color_toggled" : self.on_color_toggled,
            "on_color_set" : self.on_color_set,
            "on_object_toggled" : self.on_object_toggled
            })

        self.window = self.top.get_widget("preferences")
        self.apply = self.top.get_widget("apply")
        self.tree = self.top.get_widget("tree")
        self.panel = self.top.get_widget("panel")
        self.build_tree()
        self.build()
        self.build_ext()
        self.apply.set_sensitive(0)

    def build_tree(self):
        self.tree.show()
        for (name,list) in panellist:
            item = gtk.GtkTreeItem(name)
            item.show()
            item.connect("select",self.select,0)
            self.tree.append(item)
            subtree = gtk.GtkTree()
            subtree.show()
            item.set_subtree(subtree)
            for (subname,tab) in list:
                newitem = gtk.GtkTreeItem(subname)
                newitem.show()
                newitem.connect("select",self.select,tab)
                subtree.append(newitem)
        
    def build(self):
        auto = self.top.get_widget("autoload")
        asave_int = self.top.get_widget("autosave_interval")
        vis = self.top.get_widget("gid_visible")
        idedit = self.top.get_widget("gid_edit")
        index_vis = self.top.get_widget("show_child_id")
        tabs = self.top.get_widget("usetabs")
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
        detail = self.top.get_widget("showdetail")
        display_attr_obj = self.top.get_widget("attr_display")
        display_altnames = self.top.get_widget("display_altnames")

        auto.set_active(autoload)
        asave_int.set_value(int(autosave_int))
        detail.set_active(show_detail)
        tabs.set_active(usetabs)
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
        vis.set_active(id_visible)
        idedit.set_active(id_edit)
        index_vis.set_active(index_visible)

        self.top.get_widget("iprefix").set_text(iprefix)
        self.top.get_widget("oprefix").set_text(oprefix)
        self.top.get_widget("fprefix").set_text(fprefix)
        self.top.get_widget("sprefix").set_text(sprefix)
        self.top.get_widget("pprefix").set_text(pprefix)
        
        if status_bar == 0:
            self.top.get_widget("stat1").set_active(1)
        elif status_bar == 1:
            self.top.get_widget("stat2").set_active(1)
        else:
            self.top.get_widget("stat3").set_active(1)

        if toolbar == 0:
            self.top.get_widget("tool1").set_active(1)
        elif toolbar == 1:
            self.top.get_widget("tool2").set_active(1)
        else:
            self.top.get_widget("tool3").set_active(1)

        display_attr_obj.set_active(display_attr)
        self.top.get_widget("attr_name").set_text(attr_name)
        
        display_altnames.set_active(hide_altnames)

        paper_obj = self.top.get_widget("paper_size")
        menu = gtk.GtkMenu()
        choice = 0
        for index in range(0,len(PaperMenu.paper_sizes)):
            name = PaperMenu.paper_sizes[index].get_name()
            if name == paper_preference:
                choice = index
            item = gtk.GtkMenuItem(name)
            item.set_data(DATA,name)
            item.connect("activate", self.on_format_toggled)
            item.show()
            menu.append(item)
        menu.set_active(choice)
        paper_obj.set_menu(menu)

        lastnamegen_obj = self.top.get_widget("lastnamegen")
        menu = gtk.GtkMenu()
        choice = 0
        for index in range(0,len(_surname_styles)):
            name = _surname_styles[index]
            item = gtk.GtkMenuItem(name)
            item.set_data(DATA,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            menu.append(item)
        menu.set_active(lastnamegen)
        lastnamegen_obj.set_menu(menu)

        output_obj = self.top.get_widget("output_format")
        menu = gtk.GtkMenu()
        choice = 0

        choice = 0
        index = 0
        for name in const.output_formats:
            if name == output_preference:
                choice = index
            item = gtk.GtkMenuItem(name)
            item.set_data(DATA,name)
            item.connect("activate", self.on_format_toggled)
            item.show()
            menu.append(item)
            index = index + 1
        menu.set_active(choice)
        output_obj.set_menu(menu)

        date_option = self.top.get_widget("date_format")
        date_menu = gtk.GtkMenu()
        for index in range(0,len(_date_format_list)):
            item = gtk.GtkMenuItem(_date_format_list[index])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            date_menu.append(item)
        date_menu.set_active(get_format_code())
        date_option.set_menu(date_menu)

        date_entry = self.top.get_widget("date_entry_format")
        date_menu = gtk.GtkMenu()
        for index in range(0,len(_date_entry_list)):
            item = gtk.GtkMenuItem(_date_entry_list[index])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            date_menu.append(item)
        date_menu.set_active(Date.entryCode)
        date_entry.set_menu(date_menu)

        name_option = self.top.get_widget("name_format")
        name_menu = gtk.GtkMenu()
        for index in range(0,len(_name_format_list)):
            name_tuple = _name_format_list[index]
            item = gtk.GtkMenuItem(name_tuple[0])
            item.set_data(INDEX,index)
            item.connect("activate", self.on_format_toggled)
            item.show()
            name_menu.append(item)
        name_menu.set_active(_name_format)
        name_option.set_menu(name_menu)

        self.top.get_widget("resname").set_text(owner.getName())
        self.top.get_widget("resaddr").set_text(owner.getAddress())
        self.top.get_widget("rescity").set_text(owner.getCity())
        self.top.get_widget("resstate").set_text(owner.getState())
        self.top.get_widget("rescountry").set_text(owner.getCountry())
        self.top.get_widget("respostal").set_text(owner.getPostalCode())
        self.top.get_widget("resphone").set_text(owner.getPhone())
        self.top.get_widget("resemail").set_text(owner.getEmail())

        cwidget = self.top.get_widget(ODDFGCOLOR)
        cwidget.set_i16(ListColors.oddfg[0],ListColors.oddfg[1],\
                        ListColors.oddfg[2],0xffff)

        cwidget = self.top.get_widget(ODDBGCOLOR)
        cwidget.set_i16(ListColors.oddbg[0],ListColors.oddbg[1],\
                        ListColors.oddbg[2],0xffff)
        
        cwidget = self.top.get_widget(EVENFGCOLOR)
        cwidget.set_i16(ListColors.evenfg[0],ListColors.evenfg[1],\
                        ListColors.evenfg[2],0xffff)
        
        cwidget = self.top.get_widget(EVENBGCOLOR)
        cwidget.set_i16(ListColors.evenbg[0],ListColors.evenbg[1],\
                        ListColors.evenbg[2],0xffff)
        
        cwidget = self.top.get_widget(ANCESTORFGCOLOR)
        cwidget.set_i16(ListColors.ancestorfg[0],ListColors.ancestorfg[1],\
                        ListColors.ancestorfg[2],0xffff)
        
        self.top.get_widget("enableColors").set_active(ListColors.get_enable())
        self.top.get_widget(ODDFGCOLOR).set_sensitive(ListColors.get_enable())
        self.top.get_widget(ODDBGCOLOR).set_sensitive(ListColors.get_enable())
        self.top.get_widget(EVENBGCOLOR).set_sensitive(ListColors.get_enable())
        self.top.get_widget(EVENFGCOLOR).set_sensitive(ListColors.get_enable())
        self.top.get_widget(ANCESTORFGCOLOR).set_sensitive(ListColors.get_enable())
        
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
            item = gtk.GtkTreeItem(c)
            item.show()
            item.expand()
            item.connect('select',self.select,0)
            self.tree.append(item)
            subtree = gtk.GtkTree()
            subtree.show()
            item.set_subtree(subtree)
            for panel in self.c[c].keys():
                newitem = gtk.GtkTreeItem(panel)
                newitem.show()
                newitem.expand()
                newitem.connect('select',self.select,next_panel)
                next_panel = next_panel + 1
                subtree.append(newitem)
                box = gtk.GtkVBox()
                box.show()
                col = 0
                panel_label = gtk.GtkLabel("")
                panel_label.show()
                self.panel.append_page(box,panel_label)
                for frame in self.c[c][panel].keys():
                    pairs = self.c[c][panel][frame]
                    fr = gtk.GtkFrame(frame)
                    fr.show()
                    box.pack_start(fr,GTK.FALSE,GTK.FALSE)
                    table = gtk.GtkTable(len(pairs),2)
                    table.show()
                    fr.add(table)
                    for wobj in pairs:
                        w = wobj.get_widgets()
                        if len(w) == 2:
                            table.attach(w[0],0,1,col,col+1,GTK.FILL,GTK.SHRINK,5,5)
                            table.attach(w[1],1,2,col,col+1,GTK.FILL|GTK.EXPAND,GTK.SHRINK,5,5)
                        else:
                            table.attach(w[0],0,2,col,col+1,GTK.FILL|GTK.EXPAND,GTK.SHRINK,5,5)
                        col = col + 1
            
    def select(self,obj,data):
        self.panel.set_page(data)

    def on_propertybox_help(self,obj):
        import gnome.help
        gnome.help.display('gramps-manual','prefs.html')

    def on_close_clicked(self,obj):
        utils.destroy_passed_object(self.window)
    
    def on_ok_clicked(self,obj):
        self.on_propertybox_apply(obj)
        utils.destroy_passed_object(self.window)

    def on_propertybox_apply(self,obj):
        global nameof
        global owner
        global usetabs
        global uselds
        global autocomp
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
        global id_visible
        global id_edit
        global index_visible
        global status_bar
        global toolbar
        global display_attr
        global attr_name
        global hide_altnames
        global paper_preference
        global output_preference
        global show_detail
        global report_dir
        global web_dir
        global db_dir
        global lastnamegen
    
        show_detail = self.top.get_widget("showdetail").get_active()
        autoload = self.top.get_widget("autoload").get_active()
        autosave_int = self.top.get_widget("autosave_interval").get_value_as_int()
        display_attr = self.top.get_widget("attr_display").get_active()
        attr_name = string.strip(self.top.get_widget("attr_name").get_text())
        usetabs = self.top.get_widget("usetabs").get_active()
        uselds = self.top.get_widget("uselds").get_active()
        autocomp = self.top.get_widget("autocomp").get_active()
        mediaref = self.top.get_widget("mediaref").get_active()
        localprop = self.top.get_widget("localprop").get_active()
        globalprop = self.top.get_widget("globalprop").get_active()
        calendar = self.top.get_widget("calendar").get_active()
        usevc = self.top.get_widget("use_vc").get_active()
        vc_comment = self.top.get_widget("vc_comment").get_active()
        uncompress = self.top.get_widget("uncompress").get_active()
        id_visible = self.top.get_widget("gid_visible").get_active()
        id_edit = self.top.get_widget("gid_edit").get_active()
        index_visible = self.top.get_widget("show_child_id").get_active()
        hide_altnames = self.top.get_widget("display_altnames").get_active()
        paper_obj = self.top.get_widget("paper_size").get_menu().get_active()
        output_obj = self.top.get_widget("output_format").get_menu().get_active()
        
        if self.top.get_widget("stat1").get_active():
            status_bar = 0
        elif self.top.get_widget("stat2").get_active():
            status_bar = 1
        else:
            status_bar = 2

        if self.top.get_widget("tool1").get_active():
            toolbar = 0
        elif self.top.get_widget("tool2").get_active():
            toolbar = 1
        else:
            toolbar = 2

        iprefix = self.top.get_widget("iprefix").get_text()
        if iprefix == "":
            iprefix = "I"
        sprefix = self.top.get_widget("sprefix").get_text()
        if sprefix == "":
            sprefix = "S"
        oprefix = self.top.get_widget("oprefix").get_text()
        if oprefix == "":
            oprefix = "O"
        fprefix = self.top.get_widget("fprefix").get_text()
        if fprefix == "":
            fprefix = "F"
        pprefix = self.top.get_widget("pprefix").get_text()
        if pprefix == "":
            pprefix = "P"

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
    
        set_bool("/gramps/config/UseTabs",usetabs)
        set_bool("/gramps/config/UseLDS",uselds)
        set_bool("/gramps/config/DisableAutoComplete",not autocomp)
        set_bool("/gramps/config/MakeReference",mediaref)
        set_bool("/gramps/config/DisplayGlobal",globalprop)
        set_bool("/gramps/config/DisplayLocal",localprop)
        set_bool("/gramps/config/ShowCalendar",calendar)
        set_bool("/gramps/config/UseVersionControl",usevc)
        set_bool("/gramps/config/UseComment",vc_comment)
        set_bool("/gramps/config/DontCompressXML",uncompress)
        set_bool("/gramps/config/IdVisible",id_visible)
        set_bool("/gramps/config/IdEdit",id_edit)
        set_bool("/gramps/config/IndexVisible",index_visible)
        set_bool("/gramps/config/ShowDetail",show_detail)
        set_int("/gramps/config/StatusBar",status_bar)
        set_int("/gramps/config/ToolBar",toolbar+1)
        set_bool("/gramps/config/DisplayAttr",display_attr)
        set_string("/gramps/config/DisplayAttrName",attr_name)
        set_string("/gramps/config/paperPreference",paper_preference)
        set_string("/gramps/config/outputPreference",output_preference)
        set_bool("/gramps/config/autoLoad",autoload)
        set_int("/gramps/config/autoSaveInterval",autosave_int)
        
        if autosave_int != 0:
            utils.enable_autosave(None,autosave_int)
        else:
            utils.disable_autosave()
        
        set_bool("/gramps/config/DisplayAltNames",hide_altnames)
        set_string("/gramps/config/ReportDirectory",report_dir)
        set_string("/gramps/config/WebsiteDirectory",web_dir)
        set_string("/gramps/config/DbDirectory",db_dir)
        set_string("/gramps/config/iprefix",iprefix)
        set_string("/gramps/config/fprefix",fprefix)
        set_string("/gramps/config/pprefix",pprefix)
        set_string("/gramps/config/oprefix",oprefix)
        set_string("/gramps/config/sprefix",sprefix)
        
        # search for the active date format selection
        format_menu = self.top.get_widget("date_format").get_menu()
        active = format_menu.get_active().get_data(INDEX)
        
        set_format_code(active)
        set_int("/gramps/config/dateFormat",active)
        
        format_menu = self.top.get_widget("date_entry_format").get_menu()
        entry_active = format_menu.get_active().get_data(INDEX)
        
        Date.entryCode = entry_active
        set_int("/gramps/config/dateEntry",entry_active)
        
        # get the name format
        
        format_menu = self.top.get_widget("name_format").get_menu()
        active_name = format_menu.get_active().get_data(INDEX)
        
        name_tuple = _name_format_list[active_name]
        nameof = name_tuple[1]
        set_int("/gramps/config/nameFormat",active_name)
        
        format_menu = self.top.get_widget("lastnamegen").get_menu()
        lastnamegen = format_menu.get_active().get_data(DATA)
        set_int("/gramps/config/surnameGuessing",lastnamegen)
        
        name = self.top.get_widget("resname").get_text()
        addr = self.top.get_widget("resaddr").get_text()
        city = self.top.get_widget("rescity").get_text()
        state = self.top.get_widget("resstate").get_text()
        country = self.top.get_widget("rescountry").get_text()
        postal = self.top.get_widget("respostal").get_text()
        phone = self.top.get_widget("resphone").get_text()
        email = self.top.get_widget("resemail").get_text()
        
        ListColors.set_enable(self.top.get_widget("enableColors").get_active())
        set_bool("/gramps/color/enableColors",ListColors.get_enable())
        
        ListColors.oddfg = self.top.get_widget(ODDFGCOLOR).get_i16()
        ListColors.oddbg = self.top.get_widget(ODDBGCOLOR).get_i16()
        ListColors.evenfg = self.top.get_widget(EVENFGCOLOR).get_i16()
        ListColors.evenbg = self.top.get_widget(EVENBGCOLOR).get_i16()
        ListColors.ancestorfg = self.top.get_widget(ANCESTORFGCOLOR).get_i16()
        
        save_config_color(ODDFGCOLOR,ListColors.oddfg)
        save_config_color(ODDBGCOLOR,ListColors.oddbg)
        save_config_color(EVENFGCOLOR,ListColors.evenfg)
        save_config_color(EVENBGCOLOR,ListColors.evenbg)
        save_config_color(ANCESTORFGCOLOR,ListColors.ancestorfg)
        
        owner.set(name,addr,city,state,country,postal,phone,email)
        store_researcher(owner)
        
        self.db.set_iprefix(iprefix)
        self.db.set_fprefix(fprefix)
        self.db.set_sprefix(sprefix)
        self.db.set_oprefix(oprefix)
        self.db.set_pprefix(pprefix)
        
        for o in self.ext_list:
            o.set()

        # update the config file
        
        sync()
        _callback()

    def on_object_toggled(self,obj):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        self.apply.set_sensitive(1)

    def on_format_toggled(self,obj):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        self.apply.set_sensitive(1)

    def on_color_toggled(self,obj):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        active = self.top.get_widget("enableColors").get_active()
        self.top.get_widget(ODDFGCOLOR).set_sensitive(active)
        self.top.get_widget(ODDBGCOLOR).set_sensitive(active)
        self.top.get_widget(EVENFGCOLOR).set_sensitive(active)
        self.top.get_widget(EVENBGCOLOR).set_sensitive(active)
        self.top.get_widget(ANCESTORFGCOLOR).set_sensitive(active)
        self.apply.set_sensitive(1)

    def on_color_set(self,obj,r,g,b,a):
        """Called by the elements on the property box to set the changed flag,
        so that the property box knows to set the Apply button"""
        self.apply.set_sensitive(1)
        
#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    GrampsPreferences(db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_config_color(name,defval):
    r = get_int("/gramps/color/" + name + ".r")
    g = get_int("/gramps/color/" + name + ".g")
    b = get_int("/gramps/color/" + name + ".b")
    if r == None:
        return defval
    else:
        return (r,g,b)

def get_sort_cols(name,col,dir):
    c = get_int("/gramps/sort/%s_col" % name)
    if c == None:
        c = col
    d = get_int("/gramps/sort/%s_dir" % name)
    if d == None:
        d = dir
    return (c,d)

def save_sort_cols(name,col,dir):
    set_int("/gramps/sort/%s_col" % name, col)
    set_int("/gramps/sort/%s_dir" % name, dir)
    sync()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def druid_cancel_clicked(obj,a):
    utils.destroy_passed_object(obj)


