# -*- coding: utf-8 -*- 
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013  Vassilii Khachaturov
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
U.S. English date strings for display and parsing.
"""
from __future__ import print_function, unicode_literals

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateStrings")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    _ = lambda x: x
else:
    from gramps.gen.const import GRAMPS_LOCALE as glocale
    _ = lambda x: glocale.translation.sgettext(x)

#-------------------------------------------------------------------------
#
# DateStrings
#
#-------------------------------------------------------------------------
class DateStrings(object):
    """
    Base date display class. 
    """
    long_months_genitive = ( "", 
        _("genitive||January"), 
        _("genitive||February"), 
        _("genitive||March"), 
        _("genitive||April"), 
        _("genitive||May"), 
        _("genitive||June"), 
        _("genitive||July"), 
        _("genitive||August"), 
        _("genitive||September"), 
        _("genitive||October"), 
        _("genitive||November"), 
        _("genitive||December") )

    long_months_nominative = ( "", 
        _("nominative||January"), 
        _("nominative||February"), 
        _("nominative||March"), 
        _("nominative||April"), 
        _("nominative||May"), 
        _("nominative||June"), 
        _("nominative||July"), 
        _("nominative||August"), 
        _("nominative||September"), 
        _("nominative||October"), 
        _("nominative||November"), 
        _("nominative||December") )

    # TODO the above is just a proof of concept,
    # needs to be expanded with all the relevant strings...

if __name__ == '__main__':
    for i in range(1, 12):
       print (DateStrings.long_months_nominative[i], "\t", DateStrings.long_months_genitive[i])
