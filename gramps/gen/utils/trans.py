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

# $Id$

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
import logging

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..const import PREFIXDIR, ROOT_DIR
from ..constfunc import mac
#-------------------------------------------------------------------------
#
# Public Constants
#
#-------------------------------------------------------------------------
if "GRAMPSI18N" in os.environ:
    LOCALEDIR = os.environ["GRAMPSI18N"]
elif os.path.exists( os.path.join(ROOT_DIR, "lang") ):
    LOCALEDIR = os.path.join(ROOT_DIR, "lang")
elif os.path.exists(os.path.join(PREFIXDIR, "share/locale")):
    LOCALEDIR = os.path.join(PREFIXDIR, "share/locale")
else: 
    lang = os.environ.get('LANG', 'en')
    if lang and lang[:2] == 'en':
        pass # No need to display warning, we're in English
    else:
        logging.warning('Locale dir does not exist at ' + 
                        os.path.join(PREFIXDIR, "share/locale"))
        logging.warning('Running ./configure --prefix=YourPrefixDir might fix the problem') 
    LOCALEDIR = None

LOCALEDOMAIN = 'gramps'

if mac():
    import mactrans
    mactrans.mac_setup_localization(LOCALEDIR, LOCALEDOMAIN)
else:
    lang = ' '
    try:
        lang = os.environ["LANG"]
    except KeyError:
        lang = locale.getlocale()[0]
        if not lang:
            try:
                lang = locale.getdefaultlocale()[0] + '.UTF-8'
            except TypeError:
                logging.warning('Unable to determine your Locale, using English')
                lang = 'en.UTF-8'

    os.environ["LANG"] = lang
    os.environ["LANGUAGE"] = lang

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
        logging.warning('Failed to bind text domain, Gtk.Builder() has no translation')
    
    #following installs _ as a python function, we avoid this as this module is
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
    Glade had a Gtk.glade.bindtextdomain() function to define the directory
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

    # 0. See if there is a libintl-8.dll in working directory
    intl_path = os.path.join(os.getcwd(), 'libintl-8.dll') 
    if os.path.isfile(intl_path) and not LOCALEDIR is None:
        libintl = init_windows_gettext(intl_path)
        return

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
    except KeyError:
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
    logging.warning("Translation might not be complete/not working for",\
           locale.getlocale()[0])
    

def get_localedomain():
    """
    Get the LOCALEDOMAIN used for the Gramps application.
    """
    return LOCALEDOMAIN

def get_addon_translator(filename=None, domain="addon", languages=None):
    """
    Get a translator for an addon. 

       filename - filename of a file in directory with full path, or
                  None to get from running code
       domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
       languages - a list of languages to force
       returns  - a gettext.translation object

    Example:
       _ = get_addon_translator(languages=["fr_BE.utf8"]).gettext

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
    # Check if path is of type str. Do import and conversion if so.
    # The import cannot be done at the top as that will conflict with the translation system.
    if type(path) == str:
        from file import get_unicode_path_from_env_var
        path = get_unicode_path_from_env_var(path)
    if languages:
        addon_translator = gettext.translation(domain, os.path.join(path,"locale"),
                                               languages=languages,
                                               fallback=True)
    else:
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
        
def trans_objclass(objclass_str):
    """
    Translates objclass_str into "... %s", where objclass_str
    is 'Person', 'person', 'Family', 'family', etc.
    """
    from ..ggettext import gettext as _
    objclass = objclass_str.lower() 
    if objclass == "person":
        return _("the person")
    elif objclass == "family":
        return _("the family")
    elif objclass == "place":
        return _("the place")
    elif objclass == "event":
        return _("the event")
    elif objclass == "repository":
        return _("the repository")
    elif objclass == "note":
        return _("the note")
    elif objclass in ["media", "mediaobject"]:
        return _("the media")
    elif objclass == "source":
        return _("the source")
    elif objclass == "filter":
        return _("the filter")
    else:
        return _("See details")
