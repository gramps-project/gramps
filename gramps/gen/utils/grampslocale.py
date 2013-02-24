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
from ..const import ROOT_DIR
from ..constfunc import mac, UNITYPE

class GrampsLocale(locale):
"""
Encapsulate a locale
"""
    def __init__(self):
        def _get_prefix(self):
            """
            Find the root path for share/locale
            """
            if sys.platform == "win32":
                if sys.prefix == os.path.dirname(os.getcwd()):
                    return sys.prefix
                else:
                    return os.path.join(os.path.dirname(__file__), os.pardir)
            elif  sys.platform == "darwin" and sys.prefix != sys.exec_prefix:
                return sys.prefix
            else:
                return os.path.join(os.path.dirname(__file__), os.pardir)

        def _init_gettext(self):
            """
            Set up the gettext domain
            """
#the order in which bindtextdomain on gettext and on locale is called
#appears important, so we refrain from doing first all gettext.
#
#setup_gettext()
            gettext.bindtextdomain(self.localedomain, self.localedir)
            try:
                locale.setlocale(locale.LC_ALL,'')
            except:
                logging.warning(_("WARNING: Setting locale failed. Please fix"
                                  " the LC_* and/or the LANG environment "
                                  "variables to prevent this error"))
                try:
        # It is probably not necessary to set the locale to 'C'
        # because the locale will just stay at whatever it was,
        # which at startup is "C".
        # however this is done here just to make sure that the locale
        # functions are working
                    locale.setlocale(locale.LC_ALL,'C')
                except:
                    logging.warning(_("ERROR: Setting the 'C' locale didn't "
                                      "work either"))
        # FIXME: This should propagate the exception,
        # if that doesn't break Gramps under Windows
                    raise

            gettext.textdomain(slef.localedomain)
            if sys.version_info[0] < 3:
                gettext.install(self.localedomain, localedir=None, unicode=1) #None is sys default locale
            else:
                gettext.install(self.localedomain, localedir=None) #None is sys default locale

            if hasattr(os, "uname"):
                operating_system = os.uname()[0]
            else:
                operating_system = sys.platform

            if win(): # Windows
                setup_windows_gettext()
            elif operating_system == 'FreeBSD':
                try:
                    gettext.bindtextdomain(self.localedomain, self.localedir)
                except locale.Error:
                    logging.warning('No translation in some Gtk.Builder strings, ')
            elif operating_system == 'OpenBSD':
                pass
            else: # normal case
                try:
                    locale.bindtextdomain(self.localedomain, self.localedir)
                    #locale.textdomain(self.localedomain)
                except locale.Error:
                    logging.warning('No translation in some Gtk.Builder strings, ')

        prefixdir = self._get_prefix()
        if "GRAMPSI18N" in os.environ:
            if os.path.exists(os.environ["GRAMPSI18N"]):
                self.localedir = os.environ["GRAMPSI18N"]
            else:
                self.localedir = None
        elif os.path.exists( os.path.join(ROOT_DIR, "lang") ):
            self.localedir = os.path.join(ROOT_DIR, "lang")
        elif os.path.exists(os.path.join(prefixdir, "share/locale")):
            self.localedir = os.path.join(prefixdir, "share/locale")
        else:
            self.lang = os.environ.get('LANG', 'en')
        if self.lang and self.lang[:2] == 'en':
            pass # No need to display warning, we're in English
        else:
            logging.warning('Locale dir does not exist at ' +
                            os.path.join(prefixdir, "share/locale"))
            logging.warning('Running python setup.py install --prefix=YourPrefixDir might fix the problem')
        self.localedir = None

        self.localedomain = 'gramps'

        if mac():
            from . import maclocale
            maclocale.mac_setup_localization(self.localedir, self.localedomain)
        else:
            self.lang = ' '
            try:
                self.lang = os.environ["LANG"]
            except KeyError:
                self.lang = locale.getlocale()[0]
            if not self.lang:
                try:
                    self.lang = locale.getdefaultlocale()[0] + '.UTF-8'
                except TypeError:
                    logging.warning('Unable to determine your Locale, using English')
                self.lang = 'en.UTF-8'

        os.environ["LANG"] = self.lang
        os.environ["LANGUAGE"] = self.lang
        self._init_gettext()

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------
  
    def get_localedomain(self):
        """
        Get the LOCALEDOMAIN used for the Gramps application.
        """
        return self.localedomain

    def get_addon_translator(self, filename=None, domain="addon",
                             languages=None):
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

        if not isinstance(path, UNITYPE) == str:
            from .file import get_unicode_path_from_env_var
            path = get_unicode_path_from_env_var(path)
            if languages:
                addon_translator = gettext.translation(domain,
                                                       os.path.join(path, "locale"),
                                                       languages=languages,
                                                       fallback=True)
            else:
                addon_translator = gettext.translation(domain,
                                                       os.path.join(path, "locale"),
                                                       fallback=True)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator # with a language fallback

    def get_available_translations(self):
        """
        Get a list of available translations.

        :returns: A list of translation languages.
        :rtype: unicode[]

        """
        languages = ["en"]

        if slef.localedir is None:
            return languages

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(self.localedir, langdir, 
                                       "LC_MESSAGES", "%s.mo" % self.localedomain )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def trans_objclass(self, objclass_str):
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
