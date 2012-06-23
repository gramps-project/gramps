#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 B. Malengier
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
General utility functions useful for the generic plugin system
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import locale
import sys
import os

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.plug._pluginreg import make_environment
import const
from gen.utils.file import get_unicode_path_from_file_chooser
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Local utility functions for gen.plug
#
#-------------------------------------------------------------------------
def gfloat(val):
    """Convert to floating number, taking care of possible locale differences.
    
    Useful for reading float values from text entry fields 
    while under non-English locale.
    """

    try:
        return float(val)
    except:
        try:
            return float(val.replace('.', ', '))
        except:
            return float(val.replace(', ', '.'))
    return 0.0

def gformat(val):
    """Performs ('%.3f' % val) formatting with the resulting string always 
    using dot ('.') as a decimal point.
    
    Useful for writing float values into XML when under non-English locale.
    """

    decimal_point = locale.localeconv()['decimal_point']
    return_val = "%.3f" % val
    return return_val.replace(decimal_point, '.')

def version_str_to_tup(sversion, positions):
    """
    Given a string version and positions count, returns a tuple of
    integers.

    >>> version_str_to_tup("1.02.9", 2)
    (1, 2)
    """
    try:
        tup = tuple(map(int, sversion.split(".")))
        tup += (0,) * (positions - len(tup))
    except:
        tup = (0,) * positions
    return tup[:positions]

class newplugin(object):
    """
    Fake newplugin.
    """
    def __init__(self):
        globals()["register_results"].append({})
    def __setattr__(self, attr, value):
        globals()["register_results"][-1][attr] = value

def register(ptype, **kwargs):
    """
    Fake registration. Side-effect sets register_results to kwargs.
    """
    retval = {"ptype": ptype}
    retval.update(kwargs)
    # Get the results back to calling function
    if "register_results" in globals():
        globals()["register_results"].append(retval)
    else:
        globals()["register_results"] = [retval]

class Zipfile(object):
    """
    Class to duplicate the methods of tarfile.TarFile, for Python 2.5.
    """
    def __init__(self, buffer):
        import zipfile
        self.buffer = buffer
        self.zip_obj = zipfile.ZipFile(buffer)

    def extractall(self, path, members=None):
        """
        Extract all of the files in the zip into path.
        """
        names = self.zip_obj.namelist()
        for name in self.get_paths(names):
            fullname = os.path.join(path, name)
            if not os.path.exists(fullname): 
                os.mkdir(fullname)
        for name in self.get_files(names):
            fullname = os.path.join(path, name)
            outfile = file(fullname, 'wb')
            outfile.write(self.zip_obj.read(name))
            outfile.close()

    def extractfile(self, name):
        """
        Extract a name from the zip file.

        >>> Zipfile(buffer).extractfile("Dir/dile.py").read()
        <Contents>
        """
        class ExtractFile(object):
            def __init__(self, zip_obj, name):
                self.zip_obj = zip_obj
                self.name = name
            def read(self):
                data = self.zip_obj.read(self.name)
                del self.zip_obj
                return data
        return ExtractFile(self.zip_obj, name)

    def close(self):
        """
        Close the zip object.
        """
        self.zip_obj.close()

    def getnames(self):
        """
        Get the files and directories of the zipfile.
        """
        return self.zip_obj.namelist()

    def get_paths(self, items):
        """
        Get the directories from the items.
        """
        return (name for name in items if self.is_path(name) and not self.is_file(name))

    def get_files(self, items):
        """
        Get the files from the items.
        """
        return (name for name in items if self.is_file(name))

    def is_path(self, name):
        """
        Is the name a path?
        """
        return os.path.split(name)[0]

    def is_file(self, name):
        """
        Is the name a directory?
        """
        return os.path.split(name)[1]

def load_addon_file(path, callback=None):
    """
    Load an addon from a particular path (from URL or file system).
    """
    import urllib
    import tarfile
    import cStringIO
    if (path.startswith("http://") or
        path.startswith("https://") or
        path.startswith("ftp://")):
        try:
            fp = urllib.urlopen(path)
        except:
            if callback:
                callback(_("Unable to open '%s'") % path)
            return
    else:
        try:
            fp = open(path)
        except:
            if callback:
                callback(_("Unable to open '%s'") % path)
            return
    try:
        buffer = cStringIO.StringIO(fp.read())
    except:
        if callback:
            callback(_("Error in reading '%s'") % path)
        return
    fp.close()
    # file_obj is either Zipfile or TarFile
    if path.endswith(".zip") or path.endswith(".ZIP"):
        file_obj = Zipfile(buffer)
    elif path.endswith(".tar.gz") or path.endswith(".tgz"):
        try:
            file_obj = tarfile.open(None, fileobj=buffer)
        except:
            if callback:
                callback(_("Error: cannot open '%s'") % path)
            return 
    else:
        if callback:
            callback(_("Error: unknown file type: '%s'") % path)
        return 
    # First, see what versions we have/are getting:
    good_gpr = set()
    for gpr_file in [name for name in file_obj.getnames() if name.endswith(".gpr.py")]:
        if callback:
            callback((_("Examining '%s'...") % gpr_file) + "\n")
        contents = file_obj.extractfile(gpr_file).read()
        # Put a fake register and _ function in environment:
        env = make_environment(register=register, 
                               newplugin=newplugin, 
                               _=lambda text: text)
        # clear out the result variable:
        globals()["register_results"] = []
        # evaluate the contents:
        try:
            exec(contents, env)
        except:
            if callback:
                msg = _("Error in '%s' file: cannot load.") % gpr_file
                callback("   " + msg + "\n")
            continue
        # There can be multiple addons per gpr file:
        for results in globals()["register_results"]:
            gramps_target_version = results.get("gramps_target_version", None)
            id = results.get("id", None)
            if gramps_target_version:
                vtup = version_str_to_tup(gramps_target_version, 2)
                # Is it for the right version of gramps?
                if vtup == const.VERSION_TUPLE[0:2]:
                    # If this version is not installed, or > installed, install it
                    good_gpr.add(gpr_file)
                    if callback:
                        callback("   " + (_("'%s' is for this version of Gramps.") % id)  + "\n")
                else:
                    # If the plugin is for another version; inform and do nothing
                    if callback:
                        callback("   " + (_("'%s' is NOT for this version of Gramps.") % id)  + "\n")
                        callback("   " + (_("It is for version %(v1)d.%(v2)d") % {
                                             'v1': vtup[0],
                                             'v2': vtup[1]}
                                          + "\n"))
                    continue
            else:
                # another register function doesn't have gramps_target_version
                if gpr_file in good_gpr:
                    s.remove(gpr_file)
                if callback:
                    callback("   " + (_("Error: missing gramps_target_version in '%s'...") % gpr_file)  + "\n")
    if len(good_gpr) > 0:
        # Now, install the ok ones
        file_obj.extractall(const.USER_PLUGINS)
        if callback:
            callback((_("Installing '%s'...") % path) + "\n")
        gpr_files = set([os.path.split(os.path.join(const.USER_PLUGINS, name))[0]
                         for name in good_gpr])
        for gpr_file in gpr_files:
            u_gpr_file = get_unicode_path_from_file_chooser(gpr_file)
            if callback:
                callback("   " + (_("Registered '%s'") % u_gpr_file) + "\n")
    file_obj.close()

#-------------------------------------------------------------------------
#
# OpenFileOrStdout class
#
#-------------------------------------------------------------------------
class OpenFileOrStdout:
    """Context manager to open a file or stdout for writing."""
    def __init__(self, filename):
        self.filename = filename
        self.filehandle = None

    def __enter__(self):
        if self.filename == '-':
            self.filehandle = sys.stdout
        else:
            self.filehandle = open(self.filename, 'w')
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filehandle and self.filename != '-':
            self.filehandle.close()
        return False

#-------------------------------------------------------------------------
#
# OpenFileOrStdin class
#
#-------------------------------------------------------------------------
class OpenFileOrStdin:
    """Context manager to open a file or stdin for reading."""
    def __init__(self, filename, add_mode=''):
        self.filename = filename
        self.mode = 'r%s' % add_mode
        self.filehandle = None

    def __enter__(self):
        if self.filename == '-':
            self.filehandle = sys.stdin
        else:
            self.filehandle = open(self.filename, self.mode)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename != '-':
            self.filehandle.close()
        return False

