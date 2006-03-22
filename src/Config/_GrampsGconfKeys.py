#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
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

"""
Low-level handling of gconf keys. 
"""

#-------------------------------------------------------------------------
#
# GConf
#
#-------------------------------------------------------------------------
# SUSE calls the gconf module "gnome.gconf"
try:
    import gconf
except ImportError:
    import gnome.gconf
    gconf = gnome.gconf

import gobject
import os
import Errors

client = gconf.client_get_default()
client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)


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

def get_height():
    return get_int("/apps/gramps/interface/height")

def save_height(val):
    set_int("/apps/gramps/interface/height",val)

def get_width():
    return get_int("/apps/gramps/interface/width")

def save_width(val):
    set_int("/apps/gramps/interface/width",val)

def get_family_view():
    return get_int("/apps/gramps/interface/familyview",(0,1))

def save_family_view(val):
    set_int("/apps/gramps/interface/familyview",val,(0,1))

def get_filter():
    return get_bool("/apps/gramps/interface/filter")

def save_filter(val):
    set_bool("/apps/gramps/interface/filter",val)

def get_dont_ask():
    return get_bool("/apps/gramps/interface/dont-ask")

def save_dont_ask(val):
    set_bool("/apps/gramps/interface/dont-ask",val)

def get_family_warn():
    return get_bool("/apps/gramps/interface/family-warn")

def save_family_warn(val):
    set_bool("/apps/gramps/interface/family-warn",val)

def get_index_visible():
    return get_bool("/apps/gramps/interface/index-visible")

def save_index_visible(val):
    set_bool("/apps/gramps/interface/index-visible",val)

def get_statusbar():
    return get_int("/apps/gramps/interface/statusbar",(0,1,2))

def save_statusbar(val):
    set_int("/apps/gramps/interface/statusbar",val,(0,1,2))

def get_toolbar():
    return get_int("/apps/gramps/interface/toolbar",(-1,0,1,2,3))

def save_toolbar(val):
    set_int("/apps/gramps/interface/toolbar",val,(-1,0,1,2,3))

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

def get_last_import_dir():
    return get_string("/apps/gramps/paths/recent-import-dir")

def save_last_import_dir(val):
    set_string_as_path("/apps/gramps/paths/recent-import-dir",val)

def get_last_export_dir():
    return get_string("/apps/gramps/paths/recent-export-dir")

def save_last_export_dir(val):
    set_string_as_path("/apps/gramps/paths/recent-export-dir",val)

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

def get_screen_size_checked():
    return get_bool("/apps/gramps/interface/size-checked")

def save_screen_size_checked(val):
    set_bool("/apps/gramps/interface/size-checked",val)

def get_autoload():
    return get_bool("/apps/gramps/behavior/autoload")

def get_spellcheck():
    return get_bool("/apps/gramps/behavior/spellcheck")

def save_autoload(val):
    set_bool("/apps/gramps/behavior/autoload",val)

def save_spellcheck(val):
    set_bool("/apps/gramps/behavior/spellcheck",val)

def get_betawarn():
    return get_bool("/apps/gramps/behavior/betawarn")

def save_betawarn(val):
    set_bool("/apps/gramps/behavior/betawarn",val)

def get_welcome():
    return get_int("/apps/gramps/behavior/welcome")

def save_welcome(val):
    set_int("/apps/gramps/behavior/welcome",val)

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

def get_lastnamegen(_surname_styles=[]):
    return get_int("/apps/gramps/behavior/surname-guessing",
                        range(len(_surname_styles)))

def save_lastnamegen(val,_surname_styles=[]):
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

def get_pop_plugin_status():
    return get_bool("/apps/gramps/behavior/pop-plugin-status")

def save_pop_plugin_status(val):
    set_bool("/apps/gramps/behavior/pop-plugin-status",val)

# preferences keys
def get_person_id_prefix():
    return get_string("/apps/gramps/preferences/iprefix")

def get_event_id_prefix():
    return get_string("/apps/gramps/preferences/eprefix")

def save_iprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/iprefix",val)

def get_object_id_prefix():
    return get_string("/apps/gramps/preferences/oprefix")

def save_oprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/oprefix",val)

def get_source_id_prefix():
    return get_string("/apps/gramps/preferences/sprefix")

def save_sprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/sprefix",val)

def save_eprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/eprefix",val)

def get_place_id_prefix():
    return get_string("/apps/gramps/preferences/pprefix")

def save_pprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/pprefix",val)

def get_family_id_prefix():
    return get_string("/apps/gramps/preferences/fprefix")

def save_fprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/fprefix",val)

def get_repository_id_prefix():
    return get_string("/apps/gramps/preferences/rprefix")

def save_rprefix(val):
    set_string_as_id_prefix("/apps/gramps/preferences/rprefix",val)

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

def get_date_format(date_format_list):
    return get_int("/apps/gramps/preferences/date-format",
                        range(len(date_format_list)))

def save_date_format(val,date_format_list):
    set_int("/apps/gramps/preferences/date-format",val,
                        range(len(date_format_list)))

def get_name_format(_name_format_list):
    return get_int("/apps/gramps/preferences/name-format",
                        range(len(_name_format_list)))

def save_name_format(val,_name_format_list):
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

def get_family_details():
    return get_bool("/apps/gramps/preferences/family-details")

def save_family_details(val):
    set_bool("/apps/gramps/preferences/family-details",val)

def get_family_siblings():
    return get_bool("/apps/gramps/preferences/family-siblings")

def save_family_siblings(val):
    set_bool("/apps/gramps/preferences/family-siblings",val)

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
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_bool()

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
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_int()

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
        val = client.get_default_from_schema(key)
        if val == None:
            raise Errors.GConfSchemaError("No default value for key "+key)
        return val.get_string()

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

def sync():
    client.suggest_sync()
