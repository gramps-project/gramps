#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
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

# $Id:TransUtils.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Provide translation assistance
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext
import sys
import os
import locale

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const

#-------------------------------------------------------------------------
#
# Public Constants
#
#-------------------------------------------------------------------------
if "GRAMPSI18N" in os.environ:
    LOCALEDIR = os.environ["GRAMPSI18N"]
elif os.path.exists( os.path.join(const.ROOT_DIR, "lang") ):
    LOCALEDIR = os.path.join(const.ROOT_DIR, "lang")
elif os.path.exists(os.path.join(const.PREFIXDIR, "share/locale")):
    LOCALEDIR = os.path.join(const.PREFIXDIR, "share/locale")
else: 
    print 'Locale dir does not exist at' + os.path.join(const.PREFIXDIR, "share/locale")
    print 'Running ./configure --prefix=YourPrefixDir might fix the problem' 
    LOCALEDIR = None

LOCALEDOMAIN = 'gramps'

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------
def setup_gettext():
    """
    Setup the gettext environment.

    :returns: Nothing.

    """
    gettext.bindtextdomain(LOCALEDOMAIN, LOCALEDIR)
    gettext.textdomain(LOCALEDOMAIN)
    try:
        locale.bindtextdomain(LOCALEDOMAIN, LOCALEDIR)
    except ValueError:
        print 'Failed to bind text domain, gtk.Builder() has no translation'
    
    #following installs _ as a python function, we avoid this as TransUtils is
    #used sometimes:
    #gettext.install(LOCALEDOMAIN, LOCALEDIR, unicode=1)
    
def find_intl(fname):
    """
    Routine for finding if fname is in path
    Returns path to fname or None
    """
    os_path = os.environ['PATH']
    for subpath in os_path.split(';'):
        path2file = subpath + '\\' + fname
        if os.path.isfile(path2file):
            return path2file
    return None

def test_trans(str2trans,libintl):
    """
    Routine to see if translation works
    Returns translated string
    """
    transstr = libintl.gettext(str2trans, LOCALEDOMAIN)
    return transstr

def init_windows_gettext(intl_path):
    """
    Help routine for loading and setting up libintl attributes
    Returns libintl
    """
    import ctypes
    libintl = ctypes.cdll.LoadLibrary(intl_path)
    libintl.bindtextdomain(LOCALEDOMAIN,
    LOCALEDIR.encode(sys.getfilesystemencoding()))
    libintl.textdomain(LOCALEDOMAIN)
    libintl.bind_textdomain_codeset(LOCALEDOMAIN, "UTF-8")
    libintl.gettext.restype = ctypes.c_char_p
    return libintl

def setup_windows_gettext():
    """
    Windows specific function for migrating from LibGlade to GtkBuilder
    Glade had a gtk.glade.bindtextdomain() function to define the directory
    where to look for translations (.mo-files). It is now replaced with call
    to locale.bindtextdomain() which exposes the C librarys gettext
    interface on systems that provide this interface.
    As MS Standard Runtime C library have not such interface call to
    Python's locale.bindtextdomain() is not supported on Windows systems.
    To get translation to work we must use gettext runtime library directly
    using ctypes.

    SEE: https://bugzilla.gnome.org/show_bug.cgi?id=574520

    NOTE: officially GTK is built in a way that allows deployment without
    gettext runtime library in addition to that for historic reason and
    compability libraries are built with MS name style convention like
    "intl.dll" but private builds may use posix/ld-linker tradition like
    "libintlX-X.dll" which in recent gettext version would be libintl-8.dll
    """

    str2translate = "Family Trees - Gramps"
    translated = ""
    # 1. See if there is a intl.dll in Windows/system
    os_path = os.environ['PATH']
    intl_path = 'c:\\WINDOWS\\system\\intl.dll'
    if os.path.isfile(intl_path) and not LOCALEDIR is None:
        libintl = init_windows_gettext(intl_path)
        # Now check for translation.
        translated = test_trans(str2translate,libintl)
        if str2translate != translated:
            #Translation complete
            return

    #2. See if there is a libintl-8.dll in the current path
    intl_path = find_intl('\\libintl-8.dll')
    if intl_path and not LOCALEDIR is None:
        libintl = init_windows_gettext(intl_path)
        # Now check for translation.
        translated = test_trans(str2translate,libintl)
        if str2translate != translated:
            #Translation complete
            return

    #3. See if there is another intl.dll in current path
    intl_path = find_intl('\\intl.dll')
    if intl_path and not LOCALEDIR is None:
        libintl = init_windows_gettext(intl_path)
        # Now check for translation.
        translated = test_trans(str2translate,libintl)
        if str2translate != translated:
            #Translation complete
            return
 
    # 4. If strings are equal, see if we have English as language
    lang = ' '
    try:
        lang = os.environ["LANG"]
    except:
        # if LANG is not set
        lang = locale.getlocale()[0]
        if not lang:
            # if lang is empty/None
            lang = locale.getdefaultlocale()[0]
    # See if lang begins with en_, English_ or english_
    enlang = lang.split('_')[0].lower()
    if enlang in ('en', 'english', 'c'):
        return

    # No complete/working translation found
    print "Translation might not be complete/not working for",\
           locale.getlocale()[0]
    

def get_localedomain():
    """
    Get the LOCALEDOMAIN used for the Gramps application.
    """
    return LOCALEDOMAIN

def get_addon_translator(filename=None, domain="addon"):
    """
    Get a translator for an addon. 

       filename - filename of a file in directory with full path, or
                  None to get from running code
       domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
       returns  - a gettext.translation object

    The return object has the following properties and methods:
      .gettext
      .info
      .lgettext
      .lngettext
      .ngettext
      .output_charset
      .plural
      .set_output_charset
      .ugettext
      .ungettext

    Assumes path/filename
            path/locale/LANG/LC_MESSAGES/addon.mo.
    """
    if filename is None:
        filename = sys._getframe(1).f_code.co_filename
    gramps_translator = gettext.translation(LOCALEDOMAIN, LOCALEDIR,
                                            fallback=True)
    path = os.path.dirname(os.path.abspath(filename))
    addon_translator = gettext.translation(domain, os.path.join(path,"locale"),
                                           fallback=True)
    gramps_translator.add_fallback(addon_translator)
    return gramps_translator # with a language fallback
    
def get_available_translations():
    """
    Get a list of available translations.

    :returns: A list of translation languages.
    :rtype: unicode[]
    
    """
    languages = ["en"]
    
    if LOCALEDIR is None:
        return languages

    for langdir in os.listdir(LOCALEDIR):
        mofilename = os.path.join( LOCALEDIR, langdir, 
                                   "LC_MESSAGES", "%s.mo" % LOCALEDOMAIN )
        if os.path.exists(mofilename):
            languages.append(langdir)

    languages.sort()

    return languages
