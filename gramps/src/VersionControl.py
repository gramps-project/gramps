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

import popen2
import re
import os
import string
import shutil
import intl
_ = intl.gettext

try:
    import gzip
    _gzip_ok = 1
except:
    _gzip_ok = 0

_revision_re = re.compile("revision\s+([\d\.]+)")
_date_re = re.compile("date:\s+([^;]+);")
_sep = '-' * 10
_end = "=" * 10


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

    def checkin(self,name,comment,binary,tag):
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
        r,w = popen2.popen2("rlog %s" % self.vfile)

        for line in r.readlines():
            line = string.rstrip(line)
            
            if sname == 1:
                if line[0:3] == "key":
                    sname = 0
                    continue;
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
                    rlist.append(v,d,string.join(l,'\n'))
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
                os.link("%s/%s" %(self.wd,name),self.tfile)
            except OSError:
                shutil.copyfile("%s/%s" %(self.wd,name),self.tfile)

        proc = popen2.Popen3("ci -u %s" % self.tfile,1)
        proc.tochild.write(comment)
        proc.tochild.close()
        status = proc.wait()
        del proc
        os.remove(self.tfile)
        if status != 0:
            return status
        
    def set_tag(self,tag):
        """Sets the tag to the symbolic string"""
        if tag != "":
            pproc = popen2.Popen3("rcs -N%s: %s" % (tag,self.tfile),1)
            proc.tochild.write(comment)
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

if __name__ == "__main__":
    import sys

    c = RcsVersionControl(os.getcwd())
    if sys.argv[1] == "log":
        for val in c.revision_list():
            print "%s - %s : %s" % val
    elif sys.argv[1] == "ci":
        c.checkin(sys.argv[2],"mycomment",0)
        for val in c.revision_list():
            print "%s - %s : %s" % val
    elif sys.argv[1] == "co":
        f = c.get_version(sys.argv[2])
        for l in f.readlines():
            print l
        f.close()
        

