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
# Functions to obtain values from gconf keys
#           and store values into gconf keys
#
# All gramps keys should be accessed through these functions!
#
#-------------------------------------------------------------------------

# interface keys
def get_default_view():
    return get_int("/apps/gramps/interface/defaultview",(0,1))

def save_default_view(val):
    set_int("/apps/gramps/interface/defaultview",val,(0,1))

def get_family_view():
    return get_int("/apps/gramps/interface/familyview",(0,1))

def save_family_view(val):
    set_int("/apps/gramps/interface/familyview",val,(0,1))

def get_filter():
    return get_bool("/apps/gramps/interface/filter")

def save_filter(val):
    set_bool("/apps/gramps/interface/filter",val)

def get_index_visible():
    return get_bool("/apps/gramps/interface/index-visible")

def save_index_visible(val):
    set_bool("/apps/gramps/interface/index-visible",val)

def get_statusbar():
    return get_int("/apps/gramps/interface/statusbar",(0,1,2))

def save_statusbar(val):
    set_int("/apps/gramps/interface/statusbar",val,(0,1,2))

def get_toolbar():
    return get_int("/apps/gramps/interface/toolbar",(0,1,2,3,5))

def save_toolbar(val):
    set_int("/apps/gramps/interface/toolbar",val,(0,1,2,3,5))

def get_toolbar_on():
    return get_bool("/apps/gramps/interface/toolbar-on")

def save_toolbar_on(val):
    set_bool("/apps/gramps/interface/toolbar-on",val)

def get_view():
    return get_bool("/apps/gramps/interface/view")

def save_view(val):
    set_bool("/apps/gramps/interface/view",val)

# paths keys
def get_lastfile():
    return get_string("/apps/gramps/paths/recent-file")

def save_last_file(val):
    set_string("/apps/gramps/paths/recent-file",val)

def get_report_dir():
    return get_string("/apps/gramps/paths/report-directory")

def save_report_dir(val):
    set_string_as_path("/apps/gramps/paths/report-directory",val)

def get_web_dir():
    return get_string("/apps/gramps/paths/website-directory")

def save_web_dir(val):
    set_string_as_path("/apps/gramps/paths/website-directory",val)

# behavior keys
def get_startup():
    return get_int("/apps/gramps/behavior/startup",(0,1))

def save_startup(val):
    set_int("/apps/gramps/behavior/startup",val,(0,1))

def get_autoload():
    return get_bool("/apps/gramps/behavior/autoload")

def save_autoload(val):
    set_bool("/apps/gramps/behavior/autoload",val)

def get_betawarn():
    return get_bool("/apps/gramps/behavior/betawarn")

def save_betawarn(val):
    set_bool("/apps/gramps/behavior/betawarn",val)

def get_index_visible():
    return client.get_bool("/apps/gramps/index-visible")

def get_media_reference():
    return get_bool("/apps/gramps/behavior/make-reference")

def save_media_reference(val):
    set_bool("/apps/gramps/behavior/make-reference",val)

def get_media_global():
    return get_bool("/apps/gramps/behavior/media-global")

def save_media_global(val):
    set_bool("/apps/gramps/behavior/media-global",val)

def get_media_local():
    return get_bool("/apps/gramps/behavior/media-local")

def save_media_local(val):
    set_bool("/apps/gramps/behavior/media-local",val)

def get_calendar():
    return get_bool("/apps/gramps/behavior/show-calendar")

def save_calendar(val):
    set_bool("/apps/gramps/behavior/show-calendar",val)

def get_lastnamegen():
    return get_int("/apps/gramps/behavior/surname-guessing",
                        range(len(_surname_styles)))

def save_lastnamegen(val):
    set_int("/apps/gramps/behavior/surname-guessing",val,
                        range(len(_surname_styles)))

def get_uselds():
    return get_bool("/apps/gramps/behavior/use-lds")

def save_uselds(val):
    set_bool("/apps/gramps/behavior/use-lds",val)

def get_usetips():
    return get_bool("/apps/gramps/behavior/use-tips")

def save_usetips(val):
    set_bool("/apps/gramps/behavior/use-tips",val)

# preferences keys
def get_iprefix():
    return get_string("/apps/gramps/preferences/iprefix")

def save_iprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/iprefix",val)

def get_oprefix():
    return get_string("/apps/gramps/preferences/oprefix")

def save_oprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/oprefix",val)

def get_sprefix():
    return get_string("/apps/gramps/preferences/sprefix")

def save_sprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/sprefix",val)

def get_pprefix():
    return get_string("/apps/gramps/preferences/pprefix")

def save_pprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/pprefix",val)

def get_fprefix():
    return get_string("/apps/gramps/preferences/fprefix")

def save_fprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/fprefix",val)

def get_paper_preference():
    return get_string("/apps/gramps/preferences/paper-preference")

def save_paper_preference(val):
    set_string("/apps/gramps/preferences/paper-preference",val)

def get_output_preference():
    return get_string("/apps/gramps/preferences/output-preference")

def save_output_preference(val):
    set_string("/apps/gramps/preferences/output-preference",val)

def get_goutput_preference():
    return get_string("/apps/gramps/preferences/goutput-preference")

def save_goutput_preference(val):
    set_string("/apps/gramps/preferences/goutput-preference",val)

def get_use_tips():
    return get_bool("/apps/gramps/preferences/use-tips")

def save_use_tips(val):
    set_bool("/apps/gramps/preferences/use-tips",val)

def get_date_entry():
    return get_int("/apps/gramps/preferences/date-entry",
                        range(len(_date_entry_list)))

def save_date_entry(val):
    set_int("/apps/gramps/preferences/date-entry",val,
                        range(len(_date_entry_list)))

def get_date_format():
    return get_int("/apps/gramps/preferences/date-format",
                        range(len(_date_format_list)))

def save_date_format(val):
    set_int("/apps/gramps/preferences/date-format",val,
                        range(len(_date_format_list)))

def get_name_format():
    return get_int("/apps/gramps/preferences/name-format",
                        range(len(_name_format_list)))

def save_name_format(val):
    set_int("/apps/gramps/preferences/name-format",val,
                        range(len(_name_format_list)))

# researcher keys
def get_researcher_name():
    return get_string("/apps/gramps/researcher/researcher-name")

def save_researcher_name(val):
    set_string("/apps/gramps/researcher/researcher-name",val)

def get_researcher_addr():
    return get_string("/apps/gramps/researcher/researcher-addr")

def save_researcher_addr(val):
    set_string("/apps/gramps/researcher/researcher-addr",val)

def get_researcher_city():
    return get_string("/apps/gramps/researcher/researcher-city")

def save_researcher_city(val):
    set_string("/apps/gramps/researcher/researcher-city",val)

def get_researcher_state():
    return get_string("/apps/gramps/researcher/researcher-state")

def save_researcher_state(val):
    set_string("/apps/gramps/researcher/researcher-state",val)

def get_researcher_country():
    return get_string("/apps/gramps/researcher/researcher-country")

def save_researcher_country(val):
    set_string("/apps/gramps/researcher/researcher-country",val)

def get_researcher_postal():
    return get_string("/apps/gramps/researcher/researcher-postal")

def save_researcher_postal(val):
    set_string("/apps/gramps/researcher/researcher-postal",val)

def get_researcher_phone():
    return get_string("/apps/gramps/researcher/researcher-phone")

def save_researcher_phone(val):
    set_string("/apps/gramps/researcher/researcher-phone",val)

def get_researcher_email():
    return get_string("/apps/gramps/researcher/researcher-email")

def save_researcher_email(val):
    set_string("/apps/gramps/researcher/researcher-email",val)

# Not exactly gconf keys, but the functions directly dependent on them
def get_nameof():
    return _name_format_list[get_name_format()][1]

def get_display_name():
    return _name_format_list[get_name_format()][2]

def get_display_surname():
    return _name_format_list[get_name_format()][3]

def get_toolbar_style():
    saved_toolbar = get_toolbar()
    if saved_toolbar in range(4):
        return saved_toolbar
    else:
        try:
            gnome_toolbar_str = client.get_string("/desktop/gnome/interface/toolbar_style")
            gnome_toolbar = eval("gtk.TOOLBAR_%s" % 
                        gnome_toolbar_str.replace('-','_').upper())
        except:
            gnome_toolbar = 2
        return gnome_toolbar

def set_calendar_date_format():
    Calendar.set_format_code(get_date_format())

def set_calendar_date_entry():
    Calendar.Calendar.ENTRYCODE = get_date_entry()

#-------------------------------------------------------------------------
#
# Low-level grabbing and saving keys with error checking.
#
#-------------------------------------------------------------------------
def get_bool(key):
    try:
        val = client.get_bool(key)
    except gobject.GError:
        val = None
    if val in (True,False):
        return val
    else:
        return client.get_default_from_schema(key).get_bool()

def set_bool(key,val):
    if val in (True,False):
        client.set_bool(key,val)

def get_int(key,correct_tuple=None):
    try:
        val = client.get_int(key)
    except gobject.GError:
        val = None
    if not correct_tuple or val in correct_tuple:
        return val
    else:
        return client.get_default_from_schema(key).get_int()

def set_int(key,val,correct_tuple=None):
    if not correct_tuple or val in correct_tuple:
        client.set_int(key,val)

def get_string(key,test_func=None):
    try:
        val = client.get_string(key)
    except gobject.GError:
        val = None
    if not test_func or test_func(val):
        return val
    else:
        return client.get_default_from_schema(key).get_string()

def set_string(key,val,test_func=None):
    if not test_func or test_func(val):
        client.set_string(key,val)

def set_string_as_path(key,val):
    if not val:
        val = client.get_default_from_schema(key).get_string()
    else:
        val = os.path.normpath(val) + os.sep
    client.set_string(key,val)

def set_string_as_id_prefix(key,val):
    if not val:
        val = client.get_default_from_schema(key).get_string()
    else:
        try:
            junk = val % 1
        except:
            val = client.get_default_from_schema(key).get_string()
    client.set_string(key,val)

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
        index_vis = self.top.get_widget("show_child_id")
        auto.set_active(get_autoload())
        auto.connect('toggled',lambda obj: save_autoload(obj.get_active()))

        lds = self.top.get_widget("uselds")
        lds.set_active(get_uselds())
        lds.connect('toggled',lambda obj: save_uselds(obj.get_active()))

        mr = self.top.get_widget("mediaref")
        mc = self.top.get_widget("mediacopy")
        if get_media_reference():
            mr.set_active(1)
        else:
            mc.set_active(1)
        mr.connect('toggled',lambda obj: save_media_reference(obj.get_active()))

        dg = self.top.get_widget("globalprop")
        dg.set_active(get_media_global())
        dg.connect('toggled',lambda obj: save_media_global(obj.get_active()))

        dl = self.top.get_widget("localprop")
        dl.set_active(get_media_local())
        dl.connect('toggled',lambda obj: save_media_local(obj.get_active()))

        cal = self.top.get_widget("calendar")
        cal.set_active(get_calendar())

        cal.connect('toggled',lambda obj: save_calendar(obj.get_active()))

        idedit = self.top.get_widget("gid_edit")
        idedit.set_active(get_id_edit())
        idedit.connect('toggled',lambda obj: save_id_edit(obj.get_active()))

        index_vis = self.top.get_widget("show_child_id")
        index_vis.set_active(get_index_visible())
        index_vis.connect('toggled',lambda obj: save_index_visible(obj.get_active()))

        ipr = self.top.get_widget("iprefix")
        ipr.set_text(get_iprefix())
        ipr.connect('changed',lambda obj: save_iprefix(obj.get_text()))
        opr = self.top.get_widget("oprefix")
        opr.set_text(get_oprefix())
        opr.connect('changed',lambda obj: save_oprefix(obj.get_text()))
        fpr = self.top.get_widget("fprefix")
        fpr.set_text(get_fprefix())
        fpr.connect('changed',lambda obj: save_fprefix(obj.get_text()))
        spr = self.top.get_widget("sprefix")
        spr.set_text(get_sprefix())
        spr.connect('changed',lambda obj: save_sprefix(obj.get_text()))
        ppr = self.top.get_widget("pprefix")
        ppr.set_text(get_pprefix())
        ppr.connect('changed',lambda obj: save_pprefix(obj.get_text()))

        sb2 = self.top.get_widget("stat2")
        sb3 = self.top.get_widget("stat3")
        if get_statusbar() == 0 or get_statusbar() == 1:
            sb2.set_active(1)
        else:
            sb3.set_active(1)
        sb2.connect('toggled',
                lambda obj: save_statusbar(2-obj.get_active()))

        toolbarmenu = self.top.get_widget("tooloptmenu")
        toolbarmenu.set_history(get_toolbar())
        toolbarmenu.connect('changed',lambda obj: save_toolbar(obj.get_history()))

        pvbutton = self.top.get_widget('pvbutton')
        fvbutton = self.top.get_widget('fvbutton')
        if get_default_view() == 0:
            pvbutton.set_active(1)
        else:
            fvbutton.set_active(1)
        fvbutton.connect('toggled',lambda obj: save_default_view(obj.get_active()))

        familyview1 = self.top.get_widget('familyview1')
        familyview2 = self.top.get_widget('familyview2')
        if get_family_view() == 0:
            familyview1.set_active(1)
        else:
            familyview2.set_active(1)
        familyview2.connect('toggled',lambda obj: save_family_view(obj.get_active()))

        usetips = self.top.get_widget('usetips')
        usetips.set_active(get_usetips())
        usetips.connect('toggled',lambda obj: save_usetips(obj.get_active()))

        paper_obj = self.top.get_widget("paper_size")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(PaperMenu.paper_sizes)):
            name = PaperMenu.paper_sizes[index].get_name()
            if name == get_paper_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            menu.append(item)
        menu.set_active(choice)
        paper_obj.set_menu(menu)
        paper_obj.connect("changed", 
                    lambda obj: save_paper_preference(obj.get_menu().get_active().get_data(DATA)))

        lastnamegen_obj = self.top.get_widget("lastnamegen")
        menu = gtk.Menu()
        choice = 0
        for index in range(0,len(_surname_styles)):
            name = _surname_styles[index]
            item = gtk.MenuItem(name)
            item.set_data(DATA,index)
            item.show()
            menu.append(item)
        menu.set_active(get_lastnamegen())
        lastnamegen_obj.set_menu(menu)
        lastnamegen_obj.connect("changed", 
                    lambda obj: save_lastnamegen(obj.get_menu().get_active().get_data(DATA)))

        self.osubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_text_doc_list():
            if name == get_output_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            self.osubmenu.append(item)
            index = index + 1
        self.osubmenu.set_active(choice)
        self.ofmt.set_menu(self.osubmenu)
        self.ofmt.connect("changed", 
                    lambda obj: save_output_preference(obj.get_menu().get_active().get_data(DATA)))

        self.gsubmenu = gtk.Menu()
        choice = 0
        index = 0
        for name in [ _("No default format") ] + Plugins.get_draw_doc_list():
            if name == get_goutput_preference():
                choice = index
            item = gtk.MenuItem(name)
            item.set_data(DATA,name)
            item.show()
            self.gsubmenu.append(item)
            index = index + 1
        self.gsubmenu.set_active(choice)
        self.gfmt.set_menu(self.gsubmenu)
        self.gfmt.connect("changed", 
                    lambda obj: save_goutput_preference(obj.get_menu().get_active().get_data(DATA)))

        date_option = self.top.get_widget("date_format")
        date_menu = gtk.Menu()
        for index in range(0,len(_date_format_list)):
            item = gtk.MenuItem(_date_format_list[index])
            item.set_data(INDEX,index)
            item.show()
            date_menu.append(item)
        date_menu.set_active(Calendar.get_format_code())
        date_option.set_menu(date_menu)
        date_option.connect("changed",
                    lambda obj: save_date_format(obj.get_menu().get_active().get_data(INDEX)))

        date_entry = self.top.get_widget("date_entry_format")
        date_menu = gtk.Menu()
        for index in range(0,len(_date_entry_list)):
            item = gtk.MenuItem(_date_entry_list[index])
            item.set_data(INDEX,index)
            item.show()
            date_menu.append(item)
        date_menu.set_active(Calendar.Calendar.ENTRYCODE)
        date_entry.set_menu(date_menu)
        date_entry.connect("changed", 
                    lambda obj: save_date_entry(obj.get_menu().get_active().get_data(INDEX)))

        name_option = self.top.get_widget("name_format")
        name_menu = gtk.Menu()
        for index in range(0,len(_name_format_list)):
            name_tuple = _name_format_list[index]
            item = gtk.MenuItem(name_tuple[0])
            item.set_data(INDEX,index)
            item.show()
            name_menu.append(item)
        name_menu.set_active(get_name_format())
        name_option.set_menu(name_menu)
        name_option.connect("changed", 
                    lambda obj: save_name_format(obj.get_menu().get_active().get_data(INDEX)))

        resname = self.top.get_widget("resname")
        resname.set_text(get_researcher_name())
        resname.connect('changed',lambda obj: save_researcher_name(obj.get_text()))
        resaddr = self.top.get_widget("resaddr")
        resaddr.set_text(get_researcher_addr())
        resaddr.connect('changed',lambda obj: save_researcher_addr(obj.get_text()))
        rescity = self.top.get_widget("rescity")
        rescity.set_text(get_researcher_city())
        rescity.connect('changed',lambda obj: save_researcher_city(obj.get_text()))
        resstate = self.top.get_widget("resstate")
        resstate.set_text(get_researcher_state())
        resstate.connect('changed',lambda obj: save_researcher_state(obj.get_text()))
        rescountry = self.top.get_widget("rescountry")
        rescountry.set_text(get_researcher_country())
        rescountry.connect('changed',lambda obj: save_researcher_country(obj.get_text()))
        respostal = self.top.get_widget("respostal")
        respostal.set_text(get_researcher_postal())
        respostal.connect('changed',lambda obj: save_researcher_postal(obj.get_text()))
        resphone = self.top.get_widget("resphone")
        resphone.set_text(get_researcher_phone())
        resphone.connect('changed',lambda obj: save_researcher_phone(obj.get_text()))
        resemail = self.top.get_widget("resemail")
        resemail.set_text(get_researcher_email())
        resemail.connect('changed',lambda obj: save_researcher_email(obj.get_text()))

        repdir = self.top.get_widget("repdir").gtk_entry()
        repdir.set_text(get_report_dir())
        repdir.connect('changed',lambda obj: save_report_dir(obj.get_text()))
        webdir = self.top.get_widget("htmldir").gtk_entry()
        webdir.set_text(get_web_dir())
        webdir.connect('changed',lambda obj: save_web_dir(obj.get_text()))

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
        for o in self.ext_list:
            o.set()

#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    GrampsPreferences(db)
