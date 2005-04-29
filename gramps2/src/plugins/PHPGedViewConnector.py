#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham, Martin Hawlisch
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

"Download a GEDCOM file from a phpGedView server"


import urllib2
import gtk
import gtk.glade
import os
from random import randint
from tempfile import NamedTemporaryFile
from gettext import gettext as _

#
# Interface to phpGedView
#
# See http://phpgedview.sourceforge.net/racp.php
#
class PHPGedViewConnector:
    
    TYPE_INDI   = 1
    TYPE_FAM    = 2
    TYPE_SOUR   = 3
    TYPE_REPO   = 4
    TYPE_NOTE   = 5
    TYPE_OBJE   = 6
    TYPE_OTHER  = 7
    TYPE_ALL    = 99
    
    POS_NEW     = 1
    POS_FIRST   = 2
    POS_NEXT    = 3
    POS_PREV    = 4
    POS_LAST    = 5
    POS_ALL     = 6
    
    type_trans = {
        TYPE_INDI:  "INDI",
        TYPE_FAM:   "FAM",
        TYPE_SOUR:  "SOUR",
        TYPE_REPO:  "REPO",
        TYPE_NOTE:  "NOTE",
        TYPE_OBJE:  "OBJE",
        TYPE_OTHER: "OTHER",
        }
    pos_trans = {
        POS_NEW:    "new",
        POS_FIRST:  "first",
        POS_NEXT:   "next",
        POS_PREV:   "prev",
        POS_LAST:   "last",
        POS_ALL:    "all",
        }
    
    def __init__(self,url):
        self.url = url
        self.sessionname = None
        self.sessionid = None
        self.connected = False
    
    def get_version(self):
        response = self.fetch_url_to_array( [("action","version",),])
        print response
        if response and response[0] == "SUCCESS":
            version = response[1]
            return version
        return None

    def list_gedcoms(self):
        response = self.fetch_url_to_array( [("action","listgedcoms",),])
        print response
        if response and response[0] == "SUCCESS":
            gedcoms = []
            for i in range(1,len(response)):
                if not response[i].strip():
                    break
                gedcoms.append(response[i].split("\t"))
            return gedcoms
        return None
    
    
    def connect_to_gedcom(self, filename=None, username=None, password=None):
        params = []
        params.append( ("action","connect",))
        if file:
            params.append( ("ged",filename,))
        if username:
            params.append( ("username",username,))
        if password:
            params.append( ("password",password,))
        
        response = self.fetch_url_to_array( params)
        print response
        if response and response[0] == "SUCCESS":
            session = response[1].split("\t")
            self.sessionname = session[0]
            self.sessionid = session[1]
            self.connected = True
            return True
        return False

    def list_xrefs(self, type = TYPE_ALL, pos=POS_ALL, xref=None):
        print type
        result = []
        types = []
        if type == self.TYPE_ALL:
            for entry in self.type_trans.keys():
                types.append(entry)
        else:
            types.append(type)
        for entry in types:
            request = []
            request.append( ("action", "getxref"))
            request.append( ("type", self.type_trans[entry]))
            request.append( ("position", self.pos_trans[pos]))
            if xref:
                request.append( ("xref", xref))
            result_part = self.fetch_url_to_array( request)
            print result_part
            if result_part[0] == "SUCCESS":
                for x in range(1,len(result_part)):
                    txt = result_part[x]
                    if txt:
                        txt = txt.strip()
                        if len(txt) > 0:
                            result.append( txt)
                        else:
                            break
                    else:
                        break
        return result
    
    def get_record(self, xref):
        if not xref:
            return None
        result = []
        request = []
        request.append( ("action", "get"))
        request.append( ("xref", xref))
        result_part = self.fetch_url_to_array( request)
        print result_part
        if result_part[0] == "SUCCESS":
            for x in range(1,len(result_part)):
                txt = result_part[x].strip()
                if txt and txt != "":
                    result.append( txt)
        return result

    def get_variable(self, name="PEDIGREE_ROOT_ID"):
        if not name:
            return None
        result = []
        request = []
        request.append( ("action", "getvar"))
        request.append( ("var", var))
        result_part = self.fetch_url_to_array( request)
        print result_part
        if result_part[0] == "SUCCESS":
            for x in range(1,len(result_part)):
                txt = result_part[x].strip()
                if txt and txt != "":
                    result.append( txt)
        return result

    def fetch_url_to_array(self, params):
        request_url = self.url + "client.php?"
        for param in params:
            request_url += "%s=%s&" % (param)
        if self.sessionname and self.sessionid:
            request_url += "%s=%s&" % (self.sessionname,self.sessionid)
        print "fetching %s" % request_url
        request = urllib2.Request(request_url)
        request.add_header("User-Agent", "Mozilla 1.2 (Win 98 jp)")
        f = urllib2.urlopen(request)
        result = []
        line = f.readline()
        while line:
            result.append(line.strip())
            line = f.readline()
        if len(result) > 0:
           return result
        return None



#
# Wrapper that uses the PHPGedViewConnector to download
# the GEDCOM file and import it into the database.
#
class phpGedViewImporter:

    def __init__(self, database):
        self.db = database
        self.url = None
        self.connector = None
        
        glade_file = "%s/phpgedview.glade" % os.path.dirname(__file__)
        top = gtk.glade.XML(glade_file,'importer','gramps')
        self.url_entry = top.get_widget('url_entry')
        self.version_label = top.get_widget('version_label')
        self.version_label.set_text("")
        self.file_combo = top.get_widget('file_combo')
        self.file_combo.hide()
        self.username_entry = top.get_widget('username_entry')
        self.username_entry.hide()
        self.password_entry = top.get_widget('password_entry')
        self.password_entry.hide()
        self.ok_button = top.get_widget('ok_button')
        self.ok_button.connect("activate", self.on_next_pressed_cb)
        self.ok_button.connect("button_release_event", self.on_next_pressed_cb)
        self.progressbar = top.get_widget('progressbar')
        self.dialog = top.get_widget('importer')
        self.dialog.show()

    def update_progressbar(self,text,step=0,max=0):
        self.progressbar.set_text(text)
        if max > 0:
            self.progressbar.set_fraction( 1.0 * step / max)
        else:
            self.progressbar.set_fraction( 0.0)
        while gtk.events_pending():
            gtk.main_iteration()
        
    def on_next_pressed_cb(self, widget, event=None, data=None):
        if event:
            print event.type
        
        if not self.url or self.url != self.url_entry.get_text():
            # url entered the first time or url changed
            self.url = self.url_entry.get_text()
            self.validate_server()
        else:
            self.update_progressbar(_("Logging in..."))
            if self.connector.connect_to_gedcom(self.file_combo.get_active_text(), self.username_entry.get_text(), self.password_entry.get_text()):
                if self.file_combo.get_active_text():
                    gedname = self.file_combo.get_active_text()
                else:
                    gedname = "temp.ged"
                print "gedname"
                filenameparts = gedname.split(".")
                outfile = NamedTemporaryFile("w",-1,"."+filenameparts[1],filenameparts[0]+"_")
                print "WRITING TO: "+outfile.name
                outfile.write("0 HEAD\n")
                outfile.write("1 CHAR UTF-8\n")
                
                self.update_progressbar(_("Fetching index list..."))
                steps = (   PHPGedViewConnector.TYPE_INDI,
                            PHPGedViewConnector.TYPE_FAM,
                            PHPGedViewConnector.TYPE_SOUR,
                            PHPGedViewConnector.TYPE_REPO,
                            PHPGedViewConnector.TYPE_NOTE,
                            PHPGedViewConnector.TYPE_OBJE
                        )
                xref_list = []
                i = 0
                for type in steps:
                    self.update_progressbar( _("Fetching index list..."), i, len(steps))
                    xref_list += self.connector.list_xrefs( type)
                    i += 1
                self.update_progressbar( _("Fetching records..."))
                i = 0
                for xref in xref_list[:10]:
                    self.update_progressbar( _("Fetching records..."), i, len(xref_list))
                    record = self.connector.get_record(xref)
                    for r in record:
                        outfile.write(r+"\n")
                    outfile.flush()
                    i += 1

                outfile.flush()

                self.update_progressbar( _("Importing GEDCOM..."))
                
                import ReadGedcom
                ReadGedcom.importData(self.db, outfile.name)
                # done. bye.
                self.dialog.destroy()
                
            else:
                self.version_label.set_text(_("Error: login failed"))
        self.update_progressbar( _("done."))
        return 1
        
    def validate_server(self):
        try:
            self.update_progressbar(_("Connecting..."))
            self.connector = PHPGedViewConnector(self.url)
            self.update_progressbar(_("Get version..."))
            version = self.connector.get_version()
            self.version_label.set_text(_("Version %s") % version)
            self.update_progressbar(_("Reading file list..."))
            files = self.connector.list_gedcoms()
            list_store = self.file_combo.get_model()
            list_store.clear()
            for file in files:
                list_store.append([file[0],])
            self.file_combo.show()
            self.username_entry.show()
            self.password_entry.show()
            
        except (ValueError, urllib2.URLError), e:
            print e
            self.version_label.set_text(_("Error: Invalid URL"))
            self.version_label.set_text(_("Error: Unable to connect to phpGedView"))
        self.update_progressbar(_("done."))





#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool

def phpGedViewImporterCaller(database,active_person,callback,parent=None):
    phpGedViewImporter(database)

register_tool(
    phpGedViewImporterCaller,
    _("Import the gedcom from a phpGedView driven website"),
    category=_("Import"),
    description=_("phpGedView is an open source web application that generates dynamic webpages"
                    " out of a GEDCOM file. This plugin uses the gedcom access protocol to"
                    " retrieve the gedcom file from the webserver.")
    )



# for Testing
if __name__ == "__main__":
    
    phpGedViewImporter(None)
    gtk.main()
