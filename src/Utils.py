#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
Non GUI/GTK related utility functions
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import locale
import logging
LOG = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gen.datehandler import codeset
from gen.config import config
from gen.constfunc import mac, win

#-------------------------------------------------------------------------
#
# modified flag
#
#-------------------------------------------------------------------------
_history_brokenFlag = 0

def history_broken():
    global _history_brokenFlag
    _history_brokenFlag = 1

def xml_lang():
    loc = locale.getlocale()
    if loc[0] is None:
        return ""
    else:
        return loc[0].replace('_', '-')

#-------------------------------------------------------------------------
#
# force_unicode
#
#-------------------------------------------------------------------------

def force_unicode(n):
    if not isinstance(n, unicode):
        return (unicode(n).lower(), unicode(n))
    else:
        return (n.lower(), n)

#-------------------------------------------------------------------------
#
# Clears the modified flag.  Should be called after data is saved.
#
#-------------------------------------------------------------------------
def clearHistory_broken():
    global _history_brokenFlag
    _history_brokenFlag = 0

def wasHistory_broken():
    return _history_brokenFlag

#-------------------------------------------------------------------------
#
# String Encoding functions
#
#-------------------------------------------------------------------------

def encodingdefs():
    """
    4 functions are defined to obtain a byte string that can be used as 
    sort key and is locale aware. Do not print the sortkey, it is a sortable
    string, but is not a human readable correct string!
    When gtk is defined, one can avoid some function calls as then the default
    python encoding is not ascii but utf-8, so use the gtk functions in those
    cases.
    
    conv_utf8_tosrtkey: convert a utf8 encoded string to sortkey usable string
    
    conv_unicode_tosrtkey:  convert a unicode object to sortkey usable string
    
    conv_utf8_tosrtkey_ongtk: convert a utf8 encoded string to sortkey usable 
    string when gtk is loaded or utf-8 is default python encoding
    
    conv_unicode_tosrtkey_ongtk:  convert a unicode object to sortkey usable 
    string when gtk is loaded or utf-8 is default python encoding
    """
    pass

if win():
    # python encoding is ascii, but C functions need to receive the 
    # windows codeset, so convert over to it
    conv_utf8_tosrtkey = lambda x: locale.strxfrm(x.decode("utf-8").encode(
                                                        codeset))
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode(codeset))
    #when gtk is imported the python defaultencoding is utf-8, 
    #so no need to specify it
    conv_utf8_tosrtkey_ongtk = lambda x: locale.strxfrm(unicode(x).encode(
                                                                    codeset))
    conv_unicode_tosrtkey_ongtk = lambda x: locale.strxfrm(x.encode(codeset,'replace'))
else:
    # on unix C functions need to receive utf-8. Default conversion would
    # use ascii, so it is needed to be explicit about the resulting encoding 
    conv_utf8_tosrtkey = lambda x: locale.strxfrm(x)
    conv_unicode_tosrtkey = lambda x: locale.strxfrm(x.encode("utf-8"))
    # when gtk loaded, default encoding (sys.getdefaultencoding ) is utf-8,
    # so default conversion happens with utf-8 
    conv_utf8_tosrtkey_ongtk = lambda x:  locale.strxfrm(x)
    conv_unicode_tosrtkey_ongtk = lambda x:  locale.strxfrm(x)


def title(n):
    return '<span weight="bold" size="larger">%s</span>' % n

def set_title_label(xmlobj, t):
    title_label = xmlobj.get_widget('title')
    title_label.set_text('<span weight="bold" size="larger">%s</span>' % t)
    title_label.set_use_markup(True)

from warnings import warn
def set_titles(window, title, t, msg=None):
    warn('The Utils.set_titles is deprecated. Use ManagedWindow methods')

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def profile(func, *args):
    import hotshot.stats

    prf = hotshot.Profile('mystats.profile')
    print "Start"
    prf.runcall(func, *args)
    print "Finished"
    prf.close()
    print "Loading profile"
    stats = hotshot.stats.load('mystats.profile')
    print "done"
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(100)
    stats.print_callers(100)
    
#-------------------------------------------------------------------------
#
# Config-based functions
#
#-------------------------------------------------------------------------
def get_researcher():
    """
    Return a new database owner with the default values from the config file.
    """
    name  = config.get('researcher.researcher-name')
    address  = config.get('researcher.researcher-addr')
    locality  = config.get('researcher.researcher-locality')
    city  = config.get('researcher.researcher-city')
    state  = config.get('researcher.researcher-state')
    country = config.get('researcher.researcher-country')
    post_code  = config.get('researcher.researcher-postal')
    phone = config.get('researcher.researcher-phone')
    email  = config.get('researcher.researcher-email')

    owner = gen.lib.Researcher()
    owner.set_name(name)
    owner.set_address(address)
    owner.set_locality(locality)
    owner.set_city(city)
    owner.set_state(state)
    owner.set_country(country)
    owner.set_postal_code(post_code)
    owner.set_phone(phone)
    owner.set_email(email)

    return owner
