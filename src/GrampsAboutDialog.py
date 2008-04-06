#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"About dialog"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

import logging
_LOG = logging.getLogger(".GrampsAboutDialog")

try:
    from xml.sax import make_parser, handler, SAXParseException
except:
    from _xmlplus.sax import make_parser, handler, SAXParseException


#-------------------------------------------------------------------------
#
# Gtk modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
from GrampsDisplay import url as display_url

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
AUTHORS_TITLE = _('==== Authors ====\n')
CONTRIB_TITLE = _('\n==== Contributors ====\n')

#-------------------------------------------------------------------------
#
# GrampsAboutDialog
#
#-------------------------------------------------------------------------
class GrampsAboutDialog(gtk.AboutDialog):
    """Create an About dialog with all fields set."""
    def __init__(self):
        """Setup all the fields shown in the About dialog."""
        gtk.AboutDialog.__init__(self)
        
        self.set_name(const.PROGRAM_NAME)
        self.set_version(const.VERSION)
        self.set_copyright(const.COPYRIGHT_MSG)
        self.set_artists([
            _("Much of GRAMPS' artwork is either from\n"
              "the Tango Project or derived from the Tango\n"
              "Project. This artwork is released under the\n"
              "Create Commons Attribution-ShareAlike 2.5\n"
              "license.")
          ])
        
        try:
            ifile = open(const.LICENSE_FILE, "r")
            self.set_license(ifile.read().replace('\x0c', ''))
            ifile.close()
        except:
            self.set_license("License file is missing")

        self.set_comments(_(const.COMMENTS))
        self.set_website_label(_('GRAMPS Homepage'))
        self.set_website(const.URL_HOMEPAGE)
        
        self.set_authors(_get_authors())
        
        # Only set translation credits if they are translated
        trans_credits = _(const.TRANSLATORS)
        if trans_credits != const.TRANSLATORS:
            self.set_translator_credits(trans_credits)
            
        self.set_documenters(const.DOCUMENTERS)
        self.set_logo(gtk.gdk.pixbuf_new_from_file(const.SPLASH))
        self.set_modal(True)

#-------------------------------------------------------------------------
#
# AuthorParser
#
#-------------------------------------------------------------------------
class AuthorParser(handler.ContentHandler):
    """Parse the 'authors.xml file to show in the About dialog."""
    def __init__(self, author_list, contributor_list):
        """Setup initial instance variable values."""
        handler.ContentHandler.__init__(self)
        
        self.author_list = author_list
        self.contributor_list = contributor_list
        
        # initialize all instance variables to make pylint happy
        self.uid = ""
        self.title = ""
        self.text = ""
        
    def startElement(self, tag, attrs):
        """
        """
        if tag == "author":
            self.uid = attrs['uid']
            self.title = attrs['title']
            self.text = ""
            
    def endElement(self, tag):
        """
        """
        if tag == "author":
            if (self.title == 'author' and
                self.text not in self.author_list):
                self.author_list.append(self.text.strip())
            elif (self.title == 'contributor' and
                  self.text not in self.contributor_list):
                self.contributor_list.append(self.text.strip())
        
    def characters(self, chunk):
        """
        """
        if chunk != '\n':
            self.text += chunk

#-------------------------------------------------------------------------
#
# _get_authors
#
#-------------------------------------------------------------------------
def _get_authors():
    """Return all the authors and contributors in a string.
    
    Parse the I{authors.xml} file if found, or return the default
    list from L{const} module in case of IO or parsing failure.
    
    """
    try:
        authors = []
        contributors = []
        
        parser = make_parser()
        parser.setContentHandler(AuthorParser(authors, contributors))
        
        authors_file = open(const.AUTHORS_FILE)
        parser.parse(authors_file)
        authors_file.close()
        
        authors_text = ([AUTHORS_TITLE] + authors +
                        [CONTRIB_TITLE] + contributors)
        
    except (IOError, OSError, SAXParseException):
        authors_text = const.AUTHORS

    return authors_text

#-------------------------------------------------------------------------
#
# _show_url
#
#-------------------------------------------------------------------------
def _show_url(dialog, link, prefix):
    """Show links in About dialog."""
    if prefix is not None:
        link = prefix + link
    display_url(link)

gtk.about_dialog_set_url_hook(_show_url, None)
gtk.about_dialog_set_email_hook(_show_url, 'mailto:')
