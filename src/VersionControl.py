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
# standard python modules
#
#-------------------------------------------------------------------------
import popen2
import os
import string
import shutil
import const
import Utils

from re import compile

#-------------------------------------------------------------------------
#
# GTK/GNOME
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# Attempt to load the gzip library (should be standard, but Slackware
# appears to have problems)
#
#-------------------------------------------------------------------------
try:
    import gzip
    _gzip_ok = 1
except:
    _gzip_ok = 0

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_revision_re = compile("revision\s+([\d\.]+)")
_date_re = compile("date:\s+([^;]+);\s+author:\s([^;]+);")
_sep = '-' * 10
_end = "=" * 10

class RevisionComment:

    def __init__(self,filename,save_file):
        self.filename = filename
        self.save = save_file
        self.top = libglade.GladeXML(const.revisionFile, "revcom")
        self.top.signal_autoconnect({
            "on_savecomment_clicked" : self.on_savecomment_clicked,
            })
        self.text = self.top.get_widget("text")
        self.win = self.top.get_widget("revcom")
        self.win.editable_enters(self.text)
        self.win.show()

    def on_savecomment_clicked(self,obj):
        comment = self.text.get_text()
        Utils.destroy_passed_object(self.win)
        self.save(self.filename,comment)
        

class RevisionSelect:

    def __init__(self,db,filename,vc,load,callback=None):
        self.db = db
        self.filename = filename
        self.vc = vc
        self.load = load
        self.callback = callback

        dialog = libglade.GladeXML(const.revisionFile, "revselect")
        dialog.signal_autoconnect({
            "destroy_passed_object" : self.on_cancel_clicked,
            "on_loadrev_clicked"    : self.on_loadrev_clicked,
            })

        self.revlist = dialog.get_widget("revlist")
        l = self.vc.revision_list()
        index = 0
        for f in l:
            self.revlist.append([f[0],f[1],f[3],f[2]])
            self.revlist.set_row_data(index,f[0])
            index = index + 1

    def on_cancel_clicked(self,obj):
        Utils.destroy_passed_object(obj)
        if self.callback:
            self.callback()

    def on_loadrev_clicked(self,obj):
        if len(self.revlist.selection) > 0:
            rev = self.revlist.get_row_data(self.revlist.selection[0])
            f = self.vc.get_version(rev)
            self.load(f,self.filename,rev)
            Utils.destroy_passed_object(obj)

class VersionControl:
    """Base class for revision control systems"""
    def __init__(self,wd):
        """Initializes a version control system

        wd - working directory"""
        pass

    def revision_list(self):
        """Returns a list of tuples indicating the available versions
        in the current revision control database. The tuple is in the
        form of three strings - (version,date,comment)."""
        return []

    def checkin(self,name,comment,binary):
        """Checks in a file into the revision control database

        name - file to check in
        comment - descriptive comment about the changes
        binary - true if the gramps database is compressed"""
        pass

    def set_tag(self,tag):
        """Sets the tag to the symbolic string"""
        pass
    
    def get_version(self,version):
        """Extracts a specfied version from the revision control database
        to the specified file

        version - string representing the version to extract
        target - file to extract to"""
        pass

class RcsVersionControl(VersionControl):
    """RCS (Revision Control System) based version control interface"""
    
    def __init__(self,wd):
        """Initializes the RCS database if it does not already exist.
        Sets the database to disable locking"""
        VersionControl.__init__(self,wd)
        self.wd = wd
        self.vfile = "%s/version,v" % wd
        self.tfile = "%s/version" % wd
        self.sym = {}
        if not os.path.exists(self.vfile):
            os.system('rcs -i -U -q -t-"GRAMPS database" %s' % self.vfile)
    
    def revision_list(self):
        "returns the list of revisions from an RCS file"
        rlist = []
        slog = 0
        sname = 0
        v = None
        l = []
        o = None
        d = None
        r,w = popen2.popen2("rlog %s" % self.vfile)

        for line in r.readlines():
            line = string.rstrip(line)
            
            if sname == 1:
                if line[0:3] == "key":
                    sname = 0
                    continue
                else:
                    s = string.split(string.strip(line),":")
                    print "%s - %s" % (s[0],s[1])
                    continue
            if line == "symbolic names:":
                sname = 1
                continue
            if slog:
                if line[0:10] == _sep or line[0:10] == _end:
                    slog = 0
                    rlist.append((v,d,string.join(l,'\n'),o))
                else:
                    l.append(line)
                continue
            g = _revision_re.match(line)
            if g:
                v = g.group(1)
                continue
            g = _date_re.match(line)
            if g:
                d = g.group(1)
                o = g.group(2)
                slog = 1
                l = []
       
        w.close()
        r.close()
        return rlist

    def checkin(self,name,comment,binary):
        "checks in the file to the version,v file"
        if os.path.exists(self.tfile):
            os.remove(self.tfile)
        if binary and _gzip_ok:
            ifile = gzip.open(name)
            ofile = open(self.tfile,"w")
            ofile.writelines(ifile.readlines())
            ifile.close()
            ofile.close()
        else:
            try:
                os.link(name,self.tfile)
            except OSError:
                shutil.copyfile(name,self.tfile)

        proc = popen2.Popen3("ci -u %s" % self.tfile,1)
        proc.tochild.write(comment)
        proc.tochild.close()
        status = proc.wait()
        del proc
        os.remove(self.tfile)
        return status
        
    def set_tag(self,tag):
        """Sets the tag to the symbolic string"""
        if tag != "":
            proc = popen2.Popen3("rcs -N%s: %s" % (tag,self.tfile),1)
            proc.tochild.write("")
            proc.tochild.close()
            status = proc.wait()
            del proc
        return status

    def get_version(self,version_id):
        """Extracts the requested version from the RCS database
        version_id - string containing the version to be extracted
        target - file to extract the file to."""
        r,w,e = popen2.popen3("co -p%s %s" % (version_id,self.vfile))
        return r

_version_control_list = [(RcsVersionControl, _("RCS"))]

def register_version_control(vc_class, description=None):
    """Registers a version control class with gramps

    vc_class - VersionControl derived class to register
    description - brief description of version control interface"""
    if description == None:
        description = _("No description")
    _version_control_list.append((vc_class,description))

def get_vc_list():
    """Returns a tuple representing the registered version control
    classes. The tuple is in the format of (class,description)"""
    return _version_control_list

