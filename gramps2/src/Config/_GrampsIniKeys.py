#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005  Donald N. Allingham
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
Low-level handling of .ini keys. 
"""

import os
import time
import ConfigParser
import errno
import const

NL = "\n" # FIX: newlines on Mac/Windows, if different?

# the following table was generated from data/gramps.schemas

_ini_schema = {
 'behavior/autoload' : '0',
 'behavior/spellcheck' : '1',
 'behavior/betawarn' : '0',
 'behavior/welcome' : '100',
 'preferences/date-format' : '0',
 'preferences/dont-ask' : '0',
 'interface/defaultview' : '0',
 'interface/familyview' : '0',
 'interface/filter' : '0',
 'preferences/fprefix' : 'F%04d',
 'preferences/eprefix' : 'E%04d',
 'preferences/iprefix' : 'I%04d',
 'preferences/oprefix' : 'O%04d',
 'preferences/pprefix' : 'P%04d',
 'preferences/sprefix' : 'S%04d',
 'preferences/rprefix' : 'R%04d',
 'preferences/goutput-preference' : 'No default format',
 'preferences/output-preference' : 'No default format',
 'preferences/paper-preference' : 'Letter',
 'index-visible' : '0',
 'interface/index-visible' : '0',
 'paths/recent-file' : '',
 'paths/recent-import-dir' : '',
 'paths/recent-export-dir' : '',
 'behavior/make-reference' : '1',
 'behavior/media-global' : '1',
 'behavior/media-local' : '1',
 'preferences/name-format' : '0',
 'paths/report-directory' : './',
 'researcher/researcher-addr' : '',
 'researcher/researcher-city' : '',
 'researcher/researcher-country' : '',
 'researcher/researcher-email' : '',
 'researcher/researcher-name' : '',
 'researcher/researcher-phone' : '',
 'researcher/researcher-postal' : '',
 'researcher/researcher-state' : '',
 'behavior/show-calendar' : '0',
 'behavior/startup' : '0',
 'interface/size-checked' : '0',
 'interface/statusbar' : '1',
 'behavior/surname-guessing' : '0',
 'interface/toolbar' : '5',
 'interface/toolbar-on' : '1',
 'behavior/use-lds' : '0',
 'behavior/use-tips' : '0',
 'behavior/pop-plugin-status' : '0',
 'interface/view' : '1',
 'paths/website-directory' : './',
}


def make_bool(val):
    """ Function to turn strings into booleans. """
    # these are the possible strings that should be considered False
    if val.lower() in ["0", "false", "none", ""]:
        return False
    else:
        return True

class IniKeyClient:
    """ Class to emulate gconf's client """
    def __init__(self, filename = None):
        """ Constructor takes an optional filename """
        self.data = {}
        self.callbacks = {}
        self.filename = filename
        if self.filename and os.path.exists(filename):
            self.data = self.load_ini(self.filename)
    def notify_add(self, path, func):
        """
        I think that these are callbacks that get called when the keys
        are set.
        """
        parts = path.split("/") # FIX: make path-sep independent
        # /apps/gramps/section/key
        section = parts[-2]
        key = parts[-1]
        if section not in self.callbacks:
            self.callbacks[section] = {}
        self.callbacks[section][key] = func
    def load_ini(self, filename):
        """ Load .ini into dict of dicts, which it returns """
        cp = ConfigParser.ConfigParser()
        cp.read(filename)
        data = {}
        for sec in cp.sections():
            name = sec.lower()
            if not data.has_key(name):
                data[name] = {}
            for opt in cp.options(sec):
                data[name][opt.lower()] = cp.get(sec, opt).strip()
        return data
    def save_ini(self, filename = None):
        """
        Saves the current section/keys to a .ini file. Optional filename
        will override the default filename, if one.
        """
        if not filename:
            filename = self.filename
        if filename:
            try:
                head, tail = os.path.split( filename )
                os.makedirs( head )
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            fp = open(filename, "w")
            fp.write(";; Gramps key file" + NL)
            fp.write((";; Automatically created at %s" % time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
            sections = self.data.keys()
            sections.sort()
            for section in sections:
                fp.write(("[%s]" + NL) % section)
                keys = self.data[section].keys()
                keys.sort()
                for key in keys:
                    fp.write(("%s=%s" + NL)% (key, self.data[section][key]))
                fp.write(NL)
            fp.close()
        # else, no filename given
    def get_bool(self, section, key):
        """ Emulates gconf's client method """
        return make_bool(self.data[section][key])
    def get_string(self, section, key):
        """ Emulates gconf's client method """
        return self.data[section][key]
    def get_int(self, section, key):
        """ Emulates gconf's client method """
        if self.data[section][key].isdigit():
            return int(self.data[section][key])
        elif self.data[section][key].lower() in ["true"]:
            return 1
        else:
            return 0
    def set_bool(self, section, key, val):
        """ Emulates gconf's client method """
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = str(val)
        if section in self.callbacks and key in self.callbacks[section]:
            self.callbacks[section][key](self,0,self.data[section][key],None) 
    def set_string(self, section, key, val):
        """ Emulates gconf's client method """
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = val
        if section in self.callbacks and key in self.callbacks[section]:
            self.callbacks[section][key](self,0,self.data[section][key],None) 
    def set_int(self, section, key, val):
        """ Emulates gconf's client method """
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = str(val)
        if section in self.callbacks and key in self.callbacks[section]:
            self.callbacks[section][key](self,0,self.data[section][key],None) 
    def get_default_from_schema(self, section, key):
        try:
            return _ini_schema["%s/%s" % (section,key)]
        except:
            print "get_default_from_schema:", section, key
            return "0" # FIX: where does this get its defaults?
    def suggest_sync(self):
        self.save_ini() # save back to default file, if named

client = IniKeyClient(os.path.join(const.home_dir,"keys.ini"))

#-------------------------------------------------------------------------
#
# Functions to obtain values from .ini keys
#           and store values into .ini keys
#
# All gramps keys should be accessed through these functions!
#
#-------------------------------------------------------------------------

# interface keys
def get_default_view():
    return get_int("interface", "defaultview",(0,1))

def save_default_view(val):
    set_int("interface", "defaultview",val,(0,1))

def get_height():
    return get_int("interface", "height")

def save_height(val):
    set_int("interface", "height",val)

def get_width():
    return get_int("interface", "width")

def save_width(val):
    set_int("interface", "width",val)

def get_family_view():
    return get_int("interface", "familyview", (0,1))

def save_family_view(val):
    set_int("interface", "familyview",val, (0,1))

def get_family_details():
    return get_bool("/apps/gramps/preferences/family-details", (0,1))

def save_family_details(val):
    set_bool("/apps/gramps/preferences/family-details",val, (0,1))

def get_family_siblings():
    return get_bool("/apps/gramps/preferences/family-siblings",(0,1))

def save_family_siblings(val):
    set_bool("/apps/gramps/preferences/family-siblings",val,(0,1))

def get_filter():
    return get_bool("interface", "filter")

def save_filter(val):
    set_bool("interface", "filter",val)

def get_dont_ask():
    return get_bool("interface", "dont-ask")

def save_dont_ask(val):
    set_bool("interface", "dont-ask",val)

def get_index_visible():
    return get_bool("interface", "index-visible")

def save_index_visible(val):
    set_bool("interface", "index-visible",val)

def get_statusbar():
    return get_int("interface", "statusbar",(0,1,2))

def save_statusbar(val):
    set_int("interface", "statusbar",val,(0,1,2))

def get_toolbar():
    return get_int("interface", "toolbar",(0,1,2,3,5))

def save_toolbar(val):
    set_int("interface", "toolbar",val,(0,1,2,3,5))

def get_toolbar_on():
    return get_bool("interface", "toolbar-on")

def save_toolbar_on(val):
    set_bool("interface", "toolbar-on",val)

def get_view():
    return get_bool("interface", "view")

def save_view(val):
    set_bool("interface", "view",val)

# paths keys
def get_lastfile():
    return get_string("paths", "recent-file")

def save_last_file(val):
    set_string("paths", "recent-file",val)

def get_last_import_dir():
    return get_string("paths", "recent-import-dir")

def save_last_import_dir(val):
    set_string_as_path("paths", "recent-import-dir",val)

def get_last_export_dir():
    return get_string("paths", "recent-export-dir")

def save_last_export_dir(val):
    set_string_as_path("paths", "recent-export-dir",val)

def get_report_dir():
    return get_string("paths", "report-directory")

def save_report_dir(val):
    set_string_as_path("paths", "report-directory",val)

def get_web_dir():
    return get_string("paths", "website-directory")

def save_web_dir(val):
    set_string_as_path("paths", "website-directory",val)

# behavior keys
def get_startup():
    return get_int("behavior", "startup",(0,1))

def save_startup(val):
    set_int("behavior", "startup",val,(0,1))

def get_screen_size_checked():
    return get_bool("interface", "size-checked")

def save_screen_size_checked(val):
    set_bool("interface", "size-checked",val)

def get_autoload():
    return get_bool("behavior", "autoload")

def get_spellcheck():
    return get_bool("behavior", "spellcheck")

def save_autoload(val):
    set_bool("behavior", "autoload",val)

def save_spellcheck(val):
    set_bool("behavior", "spellcheck",val)

def get_betawarn():
    return get_bool("behavior", "betawarn")

def save_betawarn(val):
    set_bool("behavior", "betawarn",val)

def get_welcome():
    return get_bool("behavior", "welcome")

def save_welcome(val):
    set_bool("behavior", "welcome",val)

def get_media_reference():
    return get_bool("behavior", "make-reference")

def save_media_reference(val):
    set_bool("behavior", "make-reference",val)

def get_media_global():
    return get_bool("behavior", "media-global")

def save_media_global(val):
    set_bool("behavior", "media-global",val)

def get_media_local():
    return get_bool("behavior", "media-local")

def save_media_local(val):
    set_bool("behavior", "media-local",val)

def get_lastnamegen(_surname_styles=[]):
    return get_int("behavior", "surname-guessing",
                        range(len(_surname_styles)))

def save_lastnamegen(val,_surname_styles=[]):
    set_int("behavior", "surname-guessing",val,
                        range(len(_surname_styles)))

def get_uselds():
    return get_bool("behavior", "use-lds")

def save_uselds(val):
    set_bool("behavior", "use-lds",val)

def get_usetips():
    return get_bool("behavior", "use-tips")

def save_usetips(val):
    set_bool("behavior", "use-tips",val)

def get_pop_plugin_status():
    return get_bool("behavior", "pop-plugin-status")

def save_pop_plugin_status(val):
    set_bool("behavior", "pop-plugin-status",val)

# preferences keys
def get_person_id_prefix():
    return get_string("preferences", "iprefix")

def get_event_id_prefix():
    return get_string("preferences", "eprefix")

def save_iprefix(val):
    set_string_as_id_prefix("preferences", "iprefix",val)

def get_object_id_prefix():
    return get_string("preferences", "oprefix")

def save_oprefix(val):
    set_string_as_id_prefix("preferences", "oprefix",val)

def get_source_id_prefix():
    return get_string("preferences", "sprefix")

def save_sprefix(val):
    set_string_as_id_prefix("preferences", "sprefix",val)

def save_eprefix(val):
    set_string_as_id_prefix("preferences", "eprefix",val)

def get_place_id_prefix():
    return get_string("preferences", "pprefix")

def save_pprefix(val):
    set_string_as_id_prefix("preferences", "pprefix",val)

def get_family_id_prefix():
    return get_string("preferences", "fprefix")

def save_fprefix(val):
    set_string_as_id_prefix("preferences", "fprefix",val)

def get_repository_id_prefix():
    return get_string("preferences", "rprefix")

def save_rprefix(val):
    set_string_as_id_prefix("preferences", "rprefix",val)

def get_paper_preference():
    return get_string("preferences", "paper-preference")

def save_paper_preference(val):
    set_string("preferences", "paper-preference",val)

def get_output_preference():
    return get_string("preferences", "output-preference")

def save_output_preference(val):
    set_string("preferences", "output-preference",val)

def get_goutput_preference():
    return get_string("preferences", "goutput-preference")

def save_goutput_preference(val):
    set_string("preferences", "goutput-preference",val)

def get_use_tips():
    return get_bool("preferences", "use-tips")

def save_use_tips(val):
    set_bool("preferences", "use-tips",val)

def get_date_format(_date_format_list=[]):
    return get_int("preferences", "date-format",
                        range(len(_date_format_list)))

def save_date_format(val,_date_format_list=[]):
    set_int("preferences", "date-format",val,
                        range(len(_date_format_list)))

def get_name_format(_name_format_list):
    return get_int("preferences", "name-format",
                        range(len(_name_format_list)))

def save_name_format(val,_name_format_list):
    set_int("preferences", "name-format",val,
                        range(len(_name_format_list)))

# researcher keys
def get_researcher_name():
    return get_string("researcher", "researcher-name")

def save_researcher_name(val):
    set_string("researcher", "researcher-name",val)

def get_researcher_addr():
    return get_string("researcher", "researcher-addr")

def save_researcher_addr(val):
    set_string("researcher", "researcher-addr",val)

def get_researcher_city():
    return get_string("researcher", "researcher-city")

def save_researcher_city(val):
    set_string("researcher", "researcher-city",val)

def get_researcher_state():
    return get_string("researcher", "researcher-state")

def save_researcher_state(val):
    set_string("researcher", "researcher-state",val)

def get_researcher_country():
    return get_string("researcher", "researcher-country")

def save_researcher_country(val):
    set_string("researcher", "researcher-country",val)

def get_researcher_postal():
    return get_string("researcher", "researcher-postal")

def save_researcher_postal(val):
    set_string("researcher", "researcher-postal",val)

def get_researcher_phone():
    return get_string("researcher", "researcher-phone")

def save_researcher_phone(val):
    set_string("researcher", "researcher-phone",val)

def get_researcher_email():
    return get_string("researcher", "researcher-email")

def save_researcher_email(val):
    set_string("researcher", "researcher-email",val)

#-------------------------------------------------------------------------
#
# Low-level grabbing and saving keys with error checking.
#
#-------------------------------------------------------------------------
def get_bool(section, key):
    try:
        val = client.get_bool(section, key)
    except KeyError:
        val = None
    if val in (True,False):
        return val
    else:
        return make_bool(client.get_default_from_schema(section, key))

def set_bool(section, key,val):
    if val in (True,False):
        client.set_bool(section, key,val)

def get_int(section, key,correct_tuple=None):
    try:
        val = client.get_int(section, key)
    except KeyError:
        val = None
    if not correct_tuple or val in correct_tuple:
        return val
    else:
        return int(client.get_default_from_schema(section, key))

def set_int(section, key,val,correct_tuple=None):
    if not correct_tuple or val in correct_tuple:
        client.set_int(section, key,val)

def get_string(section, key,test_func=None):
    try:
        val = client.get_string(section, key)
    except KeyError:
        val = ""
    if not test_func or test_func(val):
        return val
    else:
        return client.get_default_from_schema(section, key)

def set_string(section, key,val,test_func=None):
    if not test_func or test_func(val):
        client.set_string(section, key,val)

def set_string_as_path(section, key,val):
    if not val:
        val = client.get_default_from_schema(section, key)
    else:
        val = os.path.normpath(val) + os.sep
    client.set_string(section, key,val)

def set_string_as_id_prefix(section, key,val):
    if not val:
        val = client.get_default_from_schema(section, key)
    else:
        try:
            junk = val % 1
        except:
            val = client.get_default_from_schema(section, key)
    client.set_string(section, key,val)

def sync():
    client.suggest_sync()

if __name__ == "__main__":
    print "Testing..."
    client.filename = "test1.ini"
    val = "test"
    print "get_default_view()", get_default_view()
    save_default_view(val)
    print "get_family_view()", get_family_view()
    save_family_view(val)
    print "get_filter()", get_filter()
    save_filter(val)
    print "get_dont_ask()", get_dont_ask()
    save_dont_ask(val)
    print "get_index_visible()", get_index_visible()
    save_index_visible(val)
    print "get_statusbar()", get_statusbar()
    save_statusbar(val)
    print "get_toolbar()", get_toolbar()
    save_toolbar(val)
    print "get_toolbar_on()", get_toolbar_on()
    save_toolbar_on(val)
    print "get_view()", get_view()
    save_view(val)
    print "get_lastfile()", get_lastfile()
    save_last_file(val)
    print "get_last_import_dir()", get_last_import_dir()
    save_last_import_dir(val)
    print "get_last_export_dir()", get_last_export_dir()
    save_last_export_dir(val)
    print "get_report_dir()", get_report_dir()
    save_report_dir(val)
    print "get_web_dir()", get_web_dir()
    save_web_dir(val)
    print "get_startup()", get_startup()
    save_startup(val)
    print "get_screen_size_checked()", get_screen_size_checked()
    save_screen_size_checked(val)
    print "get_autoload()", get_autoload()
    save_autoload(val)
    print "get_betawarn()", get_betawarn()
    save_betawarn(val)
    print "get_welcome()", get_welcome()
    save_welcome(val)
    print "get_media_reference()", get_media_reference()
    save_media_reference(val)
    print "get_media_global()", get_media_global()
    save_media_global(val)
    print "get_media_local()", get_media_local()
    save_media_local(val)
    print "get_lastnamegen(val)", get_lastnamegen(val)
    save_lastnamegen(val, val)
    print "get_uselds()", get_uselds()
    save_uselds(val)
    print "get_usetips()", get_usetips()
    save_usetips(val)
    print "get_pop_plugin_status()", get_pop_plugin_status()
    save_pop_plugin_status(val)
    print "get_person_id_prefix()", get_person_id_prefix()
    print "get_event_id_prefix()", get_event_id_prefix()
    save_iprefix(val)
    print "get_object_id_prefix()", get_object_id_prefix()
    save_oprefix(val)
    print "get_source_id_prefix()", get_source_id_prefix()
    save_sprefix(val)
    save_eprefix(val)
    print "get_place_id_prefix()", get_place_id_prefix()
    save_pprefix(val)
    print "get_family_id_prefix()", get_family_id_prefix()
    save_fprefix(val)
    print "get_repository_id_prefix()", get_repository_id_prefix()
    save_rprefix(val)
    print "get_paper_preference()", get_paper_preference()
    save_paper_preference(val)
    print "get_output_preference()", get_output_preference()
    save_output_preference(val)
    print "get_goutput_preference()", get_goutput_preference()
    save_goutput_preference(val)
    print "get_use_tips()", get_use_tips()
    save_use_tips(val)
    print "get_date_format(val)", get_date_format(val)
    save_date_format(val, val)
    print "get_name_format(val)", get_name_format(val)
    save_name_format(val, val)
    print "get_researcher_name()", get_researcher_name()
    save_researcher_name(val)
    print "get_researcher_addr()", get_researcher_addr()
    save_researcher_addr(val)
    print "get_researcher_city()", get_researcher_city()
    save_researcher_city(val)
    print "get_researcher_state()", get_researcher_state()
    save_researcher_state(val)
    print "get_researcher_country()", get_researcher_country()
    save_researcher_country(val)
    print "get_researcher_postal()", get_researcher_postal()
    save_researcher_postal(val)
    print "get_researcher_phone()", get_researcher_phone()
    save_researcher_phone(val)
    print "get_researcher_email()", get_researcher_email()
    save_researcher_email(val)
    print "Syncing..."
    sync()
    client = IniKeyClient("test1.ini")
    client.filename = "test2.ini"
    print "Syncing..."
    sync()
    client = IniKeyClient()
    def callback(client, id, data, args):
        print "it called back! new value is %s" % data
    print "Testing callbacks..."
    client.notify_add("/apps/gramps/section/key", callback)
    client.set_int("section", "key", 23)
    assert client.get_int("section", "key") == 23
    print "client.notify_add(): passed"
    client.filename = "test3.ini"
    print "Syncing..."
    sync()
    client = IniKeyClient("test3.ini")
    assert client.get_int("section", "key") == 23
    print "client.load_ini(): passed"
    print "-" * 50
    print "test1.ini and test2.ini should be identical, except for"
    print "maybe the time. test3.ini should have [section] key=23"
