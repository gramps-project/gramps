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
usetabs       = 0
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
calendar      = 0
paper_preference = None
output_preference = None
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
ODDFGCOLOR    = "oddForeground"
ODDBGCOLOR    = "oddBackground"
EVENFGCOLOR   = "evenForeground"
EVENBGCOLOR   = "evenBackground"
ANCESTORFGCOLOR = "ancestorForeground"
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
    global owner
    global usetabs
    global calendar
    global usevc
    global iprefix
    global fprefix
    global pprefix
    global oprefix
    global sprefix
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
    global report_dir
    global web_dir
    global db_dir
    global status_bar

    _callback = call
    lastfile = get_string("/gramps/data/LastFile")
    usetabs = get_bool("/gramps/config/UseTabs")
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
    display_attr = get_bool("/gramps/config/DisplayAttr")
    attr_name = get_string("/gramps/config/DisplayAttrName")
    
    hide_altnames = get_bool("/gramps/config/DisplayAltNames")
    autoload = get_bool("/gramps/config/autoLoad")
    dateFormat = get_int("/gramps/config/dateFormat")
    dateEntry = get_int("/gramps/config/dateEntry")
    paper_preference = get_string("/gramps/config/paperPreference")
    output_preference = get_string("/gramps/config/outputPreference")
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
    if mediaref == None:
        mediaref = 1
    if globalprop == None:
        globalprop = 1
    if localprop == None:
        localprop =1 
    if usetabs == None:
        usetabs = 0
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
    if hide_altnames == None:
        hide_altnames = 0
    if dateFormat == None:
        dateFormat = 0
    if dateEntry == None:
        dateEntry = 0

    set_format_code(dateFormat)
    Date.entryCode = dateEntry

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
def on_propertybox_help(obj,page):
    import gnome.help

    gnome.help.display('gramps-manual','prefs.html')
    
#-------------------------------------------------------------------------
#
# Apply values set in the property box.  For simplicity, only apply the
# values when the page is -1 (the box has been closed).
#
#-------------------------------------------------------------------------
def on_propertybox_apply(obj,page):
    global nameof
    global owner
    global usetabs
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
    global display_attr
    global attr_name
    global hide_altnames
    global paper_preference
    global output_preference
    global show_detail
    global report_dir
    global web_dir
    global db_dir

    if page != -1:
        return
    
    show_detail = prefsTop.get_widget("showdetail").get_active()
    autoload = prefsTop.get_widget("autoload").get_active()
    display_attr = prefsTop.get_widget("attr_display").get_active()
    attr_name = string.strip(prefsTop.get_widget("attr_name").get_text())
    usetabs = prefsTop.get_widget("usetabs").get_active()
    mediaref = prefsTop.get_widget("mediaref").get_active()
    localprop = prefsTop.get_widget("localprop").get_active()
    globalprop = prefsTop.get_widget("globalprop").get_active()
    calendar = prefsTop.get_widget("calendar").get_active()
    usevc = prefsTop.get_widget("use_vc").get_active()
    vc_comment = prefsTop.get_widget("vc_comment").get_active()
    uncompress = prefsTop.get_widget("uncompress").get_active()
    id_visible = prefsTop.get_widget("gid_visible").get_active()
    id_edit = prefsTop.get_widget("gid_edit").get_active()
    index_visible = prefsTop.get_widget("show_child_id").get_active()
    hide_altnames = prefsTop.get_widget("display_altnames").get_active()
    paper_obj = prefsTop.get_widget("paper_size").get_menu().get_active()
    output_obj = prefsTop.get_widget("output_format").get_menu().get_active()

    if prefsTop.get_widget("stat1").get_active():
        status_bar = 0
    elif prefsTop.get_widget("stat2").get_active():
        status_bar = 1
    else:
        status_bar = 2

    iprefix = prefsTop.get_widget("iprefix").get_text()
    if iprefix == "":
        iprefix = "I"
    sprefix = prefsTop.get_widget("sprefix").get_text()
    if sprefix == "":
        sprefix = "S"
    oprefix = prefsTop.get_widget("oprefix").get_text()
    if oprefix == "":
        oprefix = "O"
    fprefix = prefsTop.get_widget("fprefix").get_text()
    if fprefix == "":
        fprefix = "F"
    pprefix = prefsTop.get_widget("pprefix").get_text()
    if pprefix == "":
        pprefix = "P"

    dbdir_temp = prefsTop.get_widget("dbdir").get_full_path(1)
    if dbdir_temp != None and os.path.isdir(dbdir_temp):
        db_dir = os.path.normpath(dbdir_temp) + os.sep

    repdir_temp = prefsTop.get_widget("repdir").get_full_path(1)
    if repdir_temp != None and os.path.isdir(repdir_temp):
        report_dir = os.path.normpath(repdir_temp) + os.sep

    webdir_temp = prefsTop.get_widget("htmldir").get_full_path(1)
    if webdir_temp != None and os.path.isdir(webdir_temp):
        web_dir = os.path.normpath(webdir_temp) + os.sep

    paper_preference = paper_obj.get_data(DATA)
    output_preference = output_obj.get_data(DATA)
    
    set_bool("/gramps/config/UseTabs",usetabs)
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
    set_bool("/gramps/config/DisplayAttr",display_attr)
    set_string("/gramps/config/DisplayAttrName",attr_name)
    set_string("/gramps/config/paperPreference",paper_preference)
    set_string("/gramps/config/outputPreference",output_preference)
    set_bool("/gramps/config/autoLoad",autoload)
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
    
    format_menu = prefsTop.get_widget("date_format").get_menu()
    active = format_menu.get_active().get_data(INDEX)

    set_format_code(active)
    set_int("/gramps/config/dateFormat",active)

    format_menu = prefsTop.get_widget("date_entry_format").get_menu()
    entry_active = format_menu.get_active().get_data(INDEX)

    Date.entryCode = entry_active
    set_int("/gramps/config/dateEntry",entry_active)

    # get the name format

    format_menu = prefsTop.get_widget("name_format").get_menu()
    active_name = format_menu.get_active().get_data(INDEX)

    name_tuple = _name_format_list[active_name]
    nameof = name_tuple[1]
    set_int("/gramps/config/nameFormat",active_name)

    name = prefsTop.get_widget("resname").get_text()
    addr = prefsTop.get_widget("resaddr").get_text()
    city = prefsTop.get_widget("rescity").get_text()
    state = prefsTop.get_widget("resstate").get_text()
    country = prefsTop.get_widget("rescountry").get_text()
    postal = prefsTop.get_widget("respostal").get_text()
    phone = prefsTop.get_widget("resphone").get_text()
    email = prefsTop.get_widget("resemail").get_text()

    ListColors.set_enable(prefsTop.get_widget("enableColors").get_active())
    set_bool("/gramps/color/enableColors",ListColors.get_enable())
    
    ListColors.oddfg = prefsTop.get_widget(ODDFGCOLOR).get_i16()
    ListColors.oddbg = prefsTop.get_widget(ODDBGCOLOR).get_i16()
    ListColors.evenfg = prefsTop.get_widget(EVENFGCOLOR).get_i16()
    ListColors.evenbg = prefsTop.get_widget(EVENBGCOLOR).get_i16()
    ListColors.ancestorfg = prefsTop.get_widget(ANCESTORFGCOLOR).get_i16()

    save_config_color(ODDFGCOLOR,ListColors.oddfg)
    save_config_color(ODDBGCOLOR,ListColors.oddbg)
    save_config_color(EVENFGCOLOR,ListColors.evenfg)
    save_config_color(EVENBGCOLOR,ListColors.evenbg)
    save_config_color(ANCESTORFGCOLOR,ListColors.ancestorfg)

    owner.set(name,addr,city,state,country,postal,phone,email)
    store_researcher(owner)
    
    db = obj.get_data("db")
    db.set_iprefix(iprefix)
    db.set_fprefix(fprefix)
    db.set_sprefix(sprefix)
    db.set_oprefix(oprefix)
    db.set_pprefix(pprefix)

    # update the config file
    
    sync()
    _callback()

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
# Called by the elements on the property box to set the changed flag,
# so that the property box knows to set the Apply button
#
#-------------------------------------------------------------------------
def on_object_toggled(obj):
    obj.changed()

#-------------------------------------------------------------------------
#
# Called by the elements on the property box to set the changed flag,
# so that the property box knows to set the Apply button
#
#-------------------------------------------------------------------------
def on_format_toggled(obj):
    obj.get_data(OBJECT).changed()

#-------------------------------------------------------------------------
#
# Called by the elements on the property box to set the changed flag,
# so that the property box knows to set the Apply button
#
#-------------------------------------------------------------------------
def on_color_toggled(obj):
    active = prefsTop.get_widget("enableColors").get_active()
    prefsTop.get_widget(ODDFGCOLOR).set_sensitive(active)
    prefsTop.get_widget(ODDBGCOLOR).set_sensitive(active)
    prefsTop.get_widget(EVENFGCOLOR).set_sensitive(active)
    prefsTop.get_widget(EVENBGCOLOR).set_sensitive(active)
    prefsTop.get_widget(ANCESTORFGCOLOR).set_sensitive(active)
    obj.changed()

#-------------------------------------------------------------------------
#
# Called by the elements on the property box to set the changed flag,
# so that the property box knows to set the Apply button
#
#-------------------------------------------------------------------------
def on_color_set(obj,r,g,b,a):
    obj.changed()

#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    global prefsTop

    prefsTop = libglade.GladeXML(const.configFile,"propertybox")
    prefsTop.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_propertybox_apply" : on_propertybox_apply,
        "on_propertybox_help" : on_propertybox_help,
        "on_color_toggled" : on_color_toggled,
        "on_color_set" : on_color_set,
        "on_object_toggled" : on_object_toggled
        })

    pbox = prefsTop.get_widget("propertybox")
    pbox.set_data("db",db)
    auto = prefsTop.get_widget("autoload")
    vis = prefsTop.get_widget("gid_visible")
    idedit = prefsTop.get_widget("gid_edit")
    index_vis = prefsTop.get_widget("show_child_id")
    tabs = prefsTop.get_widget("usetabs")
    mr = prefsTop.get_widget("mediaref")
    mc = prefsTop.get_widget("mediacopy")
    dg = prefsTop.get_widget("globalprop")
    dl = prefsTop.get_widget("localprop")
    cal = prefsTop.get_widget("calendar")
    vc = prefsTop.get_widget("use_vc")
    vcom = prefsTop.get_widget("vc_comment")
    compress = prefsTop.get_widget("uncompress")
    detail = prefsTop.get_widget("showdetail")
    display_attr_obj = prefsTop.get_widget("attr_display")
    display_altnames = prefsTop.get_widget("display_altnames")
    auto.set_active(autoload)
    detail.set_active(show_detail)
    tabs.set_active(usetabs)
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

    prefsTop.get_widget("iprefix").set_text(iprefix)
    prefsTop.get_widget("oprefix").set_text(oprefix)
    prefsTop.get_widget("fprefix").set_text(fprefix)
    prefsTop.get_widget("sprefix").set_text(sprefix)
    prefsTop.get_widget("pprefix").set_text(pprefix)
    
    if status_bar == 0:
        prefsTop.get_widget("stat1").set_active(1)
    elif status_bar == 1:
        prefsTop.get_widget("stat2").set_active(1)
    else:
        prefsTop.get_widget("stat3").set_active(1)

    display_attr_obj.set_active(display_attr)
    prefsTop.get_widget("attr_name").set_text(attr_name)
        
    display_altnames.set_active(hide_altnames)

    paper_obj = prefsTop.get_widget("paper_size")
    menu = gtk.GtkMenu()
    choice = 0
    for index in range(0,len(PaperMenu.paper_sizes)):
        name = PaperMenu.paper_sizes[index].get_name()
        if name == paper_preference:
            choice = index
        item = gtk.GtkMenuItem(name)
        item.set_data(OBJECT,pbox)
        item.set_data(DATA,name)
        item.connect("activate", on_format_toggled)
        item.show()
        menu.append(item)
    menu.set_active(choice)
    paper_obj.set_menu(menu)

    output_obj = prefsTop.get_widget("output_format")
    menu = gtk.GtkMenu()
    choice = 0

    choice = 0
    index = 0
    for name in const.output_formats:
        if name == output_preference:
            choice = index
        item = gtk.GtkMenuItem(name)
        item.set_data(OBJECT,pbox)
        item.set_data(DATA,name)
        item.connect("activate", on_format_toggled)
        item.show()
        menu.append(item)
        index = index + 1
    menu.set_active(choice)
    output_obj.set_menu(menu)

    date_option = prefsTop.get_widget("date_format")
    date_menu = gtk.GtkMenu()
    for index in range(0,len(_date_format_list)):
        item = gtk.GtkMenuItem(_date_format_list[index])
        item.set_data(INDEX,index)
        item.set_data(OBJECT,pbox)
        item.connect("activate", on_format_toggled)
        item.show()
        date_menu.append(item)
    date_menu.set_active(get_format_code())
    date_option.set_menu(date_menu)

    date_entry = prefsTop.get_widget("date_entry_format")
    date_menu = gtk.GtkMenu()
    for index in range(0,len(_date_entry_list)):
        item = gtk.GtkMenuItem(_date_entry_list[index])
        item.set_data(INDEX,index)
        item.set_data(OBJECT,pbox)
        item.connect("activate", on_format_toggled)
        item.show()
        date_menu.append(item)
    date_menu.set_active(Date.entryCode)
    date_entry.set_menu(date_menu)

    name_option = prefsTop.get_widget("name_format")
    name_menu = gtk.GtkMenu()
    for index in range(0,len(_name_format_list)):
        name_tuple = _name_format_list[index]
        item = gtk.GtkMenuItem(name_tuple[0])
        item.set_data(INDEX,index)
        item.set_data(OBJECT,pbox)
        item.connect("activate", on_format_toggled)
        item.show()
        name_menu.append(item)
    name_menu.set_active(_name_format)
    name_option.set_menu(name_menu)

    prefsTop.get_widget("resname").set_text(owner.getName())
    prefsTop.get_widget("resaddr").set_text(owner.getAddress())
    prefsTop.get_widget("rescity").set_text(owner.getCity())
    prefsTop.get_widget("resstate").set_text(owner.getState())
    prefsTop.get_widget("rescountry").set_text(owner.getCountry())
    prefsTop.get_widget("respostal").set_text(owner.getPostalCode())
    prefsTop.get_widget("resphone").set_text(owner.getPhone())
    prefsTop.get_widget("resemail").set_text(owner.getEmail())

    cwidget = prefsTop.get_widget(ODDFGCOLOR)
    cwidget.set_i16(ListColors.oddfg[0],ListColors.oddfg[1],\
                    ListColors.oddfg[2],0xffff)

    cwidget = prefsTop.get_widget(ODDBGCOLOR)
    cwidget.set_i16(ListColors.oddbg[0],ListColors.oddbg[1],\
                    ListColors.oddbg[2],0xffff)

    cwidget = prefsTop.get_widget(EVENFGCOLOR)
    cwidget.set_i16(ListColors.evenfg[0],ListColors.evenfg[1],\
                    ListColors.evenfg[2],0xffff)

    cwidget = prefsTop.get_widget(EVENBGCOLOR)
    cwidget.set_i16(ListColors.evenbg[0],ListColors.evenbg[1],\
                    ListColors.evenbg[2],0xffff)

    cwidget = prefsTop.get_widget(ANCESTORFGCOLOR)
    cwidget.set_i16(ListColors.ancestorfg[0],ListColors.ancestorfg[1],\
                    ListColors.ancestorfg[2],0xffff)

    prefsTop.get_widget("enableColors").set_active(ListColors.get_enable())
    prefsTop.get_widget(ODDFGCOLOR).set_sensitive(ListColors.get_enable())
    prefsTop.get_widget(ODDBGCOLOR).set_sensitive(ListColors.get_enable())
    prefsTop.get_widget(EVENBGCOLOR).set_sensitive(ListColors.get_enable())
    prefsTop.get_widget(EVENFGCOLOR).set_sensitive(ListColors.get_enable())
    prefsTop.get_widget(ANCESTORFGCOLOR).set_sensitive(ListColors.get_enable())

    prefsTop.get_widget("dbdir").gtk_entry().set_text(db_dir)
    prefsTop.get_widget("repdir").gtk_entry().set_text(report_dir)
    prefsTop.get_widget("htmldir").gtk_entry().set_text(web_dir)
        
    pbox.set_modified(0)
    pbox.show()

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



