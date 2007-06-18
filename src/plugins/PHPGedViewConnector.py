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


import httplib
import urllib2
import gtk
import gtk.glade
import os
from random import randint
from tempfile import NamedTemporaryFile
from tempfile import mkstemp
from gettext import gettext as _
from PluginUtils import register_tool
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
    
    def __init__(self,url,progressbar_cb=None):
        self.url = url
        self.sessionname = None
        self.sessionid = None
        self.connected = False
        self.progressbar_cb = progressbar_cb
    
    def update_progressbar(self,text=None,pos=0,max=0):
        if self.progressbar_cb:
            self.progressbar_cb(text,pos,max)
            
    def get_version(self):
        response = self.fetch_url_to_array( [("action","version",),])
        if response and response[0] == "SUCCESS":
            version = response[1]
            return version
        return None

    def list_gedcoms(self):
        response = self.fetch_url_to_array( [("action","listgedcoms",),])
        if response and response[0] == "SUCCESS":
            gedcoms = []
            for i in range(1,len(response)):
                if not response[i].strip():
                    break
                gedcoms.append(response[i].split("\t"))
            return gedcoms
        return None
    
    
    def connect_to_gedcom(self, filename=None, username=None, password=None):
        self.gedname = None
        params = []
        params.append( ("action","connect",))
        if filename:
            params.append( ("ged",filename,))
        if username:
            params.append( ("username",username,))
        if password:
            params.append( ("password",password,))
        
        response = self.fetch_url_to_array( params)
        if response and response[0] == "SUCCESS":
            session = response[1].split("\t")
            self.sessionname = session[0]
            self.sessionid = session[1]
            self.connected = True
            if filename:
                self.gedname = filename
            return True
        return False

    def list_xrefs(self, type = TYPE_ALL, pos=POS_ALL, xref=None):
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
    
    def get_records(self, xref):
        if not xref or len(xref) == 0:
            return None
        
        # merge xref list to a semicolon separated string
        xref_str = ""
        try:
            for x in xref:
                xref_str += x+";"
        except TypeError:
            xref_str = xref
        
        result = []
        request = []
        request.append( ("action", "get"))
        request.append( ("xref", xref_str))
        result_part = self.fetch_url_to_array( request)
        #print result_part
        if result_part[0] == "SUCCESS":
            for x in range(1,len(result_part)):
                txt = result_part[x].strip()
                if txt and txt != "":
                    result.append( txt)
        return result

    def fetch_full_gedcom( self, outfile=None):
        print outfile
        if outfile is None:
            gedname = self.gedname
            if not gedname:
                gedname = "temp.ged"
            filenameparts = gedname.split(".")
            (outfiled,outfilename) = mkstemp("."+filenameparts[1],filenameparts[0]+"_")
            outfile = os.fdopen(outfiled,"w")
        else:
            outfilename = outfile.name
        print outfile
        
        outfile.write("0 HEAD\n")
        outfile.write("1 SOUR phpGedView\n")
        outfile.write("2 VERS %s\n" % self.get_version())
        outfile.write("2 NAME phpGedView\n")
        outfile.write("2 DATA %s\n" % self.url)
        outfile.write("1 CHAR UTF-8\n")
        outfile.write("1 GEDC\n")
        outfile.write("2 VERS 5.5\n")
        outfile.write("2 FORM LINEAGE-LINKED\n")
        outfile.write("1 NOTE Dowloaded using GRAMPS PHPGedViewConnector\n")
        
        self.update_progressbar(_("Fetching index list..."))
        steps = (   self.TYPE_INDI,
                    self.TYPE_FAM,
                    self.TYPE_SOUR,
                    self.TYPE_REPO,
                    self.TYPE_NOTE,
                    self.TYPE_OBJE
                )
        xref_list = []
        i = 0
        for type in steps:
            self.update_progressbar( _("Fetching index list..."), i, len(steps))
            xref_list += self.list_xrefs( type)
            i += 1
        self.update_progressbar( _("Fetching records..."))
        i = 0
        junk_size = 100
        for i in range(len(xref_list)/junk_size+1):
            self.update_progressbar( _("Fetching records..."), i*junk_size, len(xref_list))
            record = self.get_records(xref_list[i*junk_size:(i+1)*junk_size])
            if record:
                for r in record:
                    outfile.write(r+"\n")
            outfile.flush()
            i += 1

        outfile.write("0 TRLR\n")
        outfile.flush()
        outfile.close()
        return outfilename


    def get_variable(self, name="PEDIGREE_ROOT_ID"):
        if not name:
            return None
        result = []
        request = []
        request.append( ("action", "getvar"))
        request.append( ("var", name))
        result_part = self.fetch_url_to_array( request)
        if result_part[0] == "SUCCESS":
            for x in range(1,len(result_part)):
                txt = result_part[x].strip()
                if txt and txt != "":
                    result.append( txt)
        return result

    def fetch_url_to_array(self, params):
        request_url = self.url + "gdbi.php?"
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

    def filter_url(self, url):
        if url[:7] != "http://":
            url = "http://"+url
        if url[-1:] != "/":
            url = url + "/"
        print url
        return url

    def update_progressbar(self,text,step=0,max=0):
        self.progressbar.set_text(text)
        if max > 0:
            self.progressbar.set_fraction( 1.0 * step / max)
        else:
            self.progressbar.set_fraction( 0.0)
        while gtk.events_pending():
            gtk.main_iteration()
        
    def on_next_pressed_cb(self, widget, event=None, data=None):
        import ReadGedcom
        if event:
            print event.type
        
        if not self.url or self.url != self.url_entry.get_text():
            # url entered the first time or url changed
            self.url = self.filter_url( self.url_entry.get_text())
            if self.validate_server():
                self.url_entry.set_text( self.url)
        else:
            self.update_progressbar(_("Logging in..."))
            if self.connector.connect_to_gedcom(self.file_combo.get_active_text(), self.username_entry.get_text(), self.password_entry.get_text()):

                self.update_progressbar( _("Fetching GEDCOM..."))
                
                fn = self.connector.fetch_full_gedcom()
                
                self.update_progressbar( _("Importing GEDCOM..."))

                ReadGedcom.importData(self.db, fn)
                # done. bye.
                self.dialog.destroy()
                
            else:
                self.version_label.set_text(_("Error: login failed"))
        self.update_progressbar( _("done."))
        return 1
        
    def validate_server(self):
        try:
            self.update_progressbar(_("Connecting..."))
            self.connector = PHPGedViewConnector(self.url,self.update_progressbar)
            self.update_progressbar(_("Get version..."))
            version = self.connector.get_version()
            if version:
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
                return True
            
        except (ValueError, urllib2.URLError, httplib.InvalidURL), e:
            print e
            self.version_label.set_text(_("Error: Invalid URL"))
        self.update_progressbar(_("done."))
        return False



# TODO: This should go into PHPGedViewConnector
def filter_url( url):
    url = url.split("?")[0]     # strip params
    if url[-1:] == "/":         # strip trailing slash
        url = url[:-1]
    if url[-4:] in (".php",".htm") or url[-5:] in (".html"):      # strip script name
        idx = url.rfind("/")
        if idx > 1:
            url = url[:idx]
    if url[:7] != "http://":    # add protocol
        url = "http://"+url
    if url[-1:] != "/":         # readd trailing slash
        url = url + "/"
    return url


## # for Testing
## if __name__ == "__main__":
##     def dummy_progress( text,pos=0,max=0):
##         if max > 0:
##             percent = pos*100/max
##             print "%s: %d%%" % (text,percent)
##         else:
##             print text
    
##     try:
##         f = open("/tmp/sites.txt")
##         l = f.readline()
##         while l:
##             l = filter_url(l.strip())
##             print l
##             try:
##                 c = PHPGedViewConnector(l,dummy_progress)
##                 c.connect_to_gedcom()
##                 v = c.get_version()
##                 if v:
##                     print("%s\t\t%s" % (v,l))
##                     c.fetch_full_gedcom()
##             except KeyboardInterrupt:
##                 exit
##             l = f.readline()
##     except IOError:
##         phpGedViewImporter(None)
##         gtk.main()

## else:
##     #-------------------------------------------------------------------------
##     #
##     #
##     #
##     #-------------------------------------------------------------------------
##     def phpGedViewImporterCaller(database,active_person,callback,parent=None):
##         phpGedViewImporter(database)
    
##     register_tool(
##         phpGedViewImporterCaller,
##         _("Import the gedcom from a phpGedView driven website"),
##         category=_("Import"),
##         description=_("phpGedView is an open source web application that generates dynamic webpages"
##                         " out of a GEDCOM file. This plugin uses the gedcom access protocol to"
##                         " retrieve the gedcom file from the webserver.")
##         )
