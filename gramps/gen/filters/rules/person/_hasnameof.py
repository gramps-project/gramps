#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .. import Rule
from ....lib.nameorigintype import NameOriginType

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels      =  [ _('Given name:'),
                    _('Full Family name:'),
                    _('person|Title:'),
                    _('Suffix:'),
                    _('Call Name:'),
                    _('Nick Name:'),
                    _('Prefix:'),
                    _('Single Surname:'),
                    _('Connector'),
                    _('Patronymic:'),
                    _('Family Nick Name:'),
                    _('Regular-Expression matching:')]
    name        = _('People with the <name>')
    description = _("Matches people with a specified (partial) name")
    category    = _('General filters')

    def prepare(self, db):
        if len(self.list) >= 12:
            self.regular_expression = bool(int(self.list[11]))
        else:
            self.regular_expression = False
        if self.regular_expression:
            self.firstn = self.list[0]
            self.lastn = self.list[1]
            self.title = self.list[2]
            self.suffix = self.list[3]
            self.calln = self.list[4]
            self.nick = self.list[5]
            self.famnick = self.list[10]
            #surname parts
            self.prefix = self.list[6]
            self.surn = self.list[7]
            self.con = self.list[8]
            self.patr = self.list[9]
        else:
            self.firstn = self.list[0].upper()
            self.lastn = self.list[1].upper()
            self.title = self.list[2].upper()
            self.suffix = self.list[3].upper()
            self.calln = self.list[4].upper()
            self.nick = self.list[5].upper()
            self.famnick = self.list[10].upper()
            #surname parts
            self.prefix = self.list[6].upper()
            self.surn = self.list[7].upper()
            self.con = self.list[8].upper()
            self.patr = self.list[9].upper()
        
    def apply(self, db, person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            val = 1
            valpref = 0
            if not self.prefix:
                valpref = 1
            valsurn = 0
            if not self.surn:
                valsurn = 1
            valcon = 0
            if not self.con:
                valcon = 1
            valpatr = 0
            if not self.patr:
                valpatr = 1
            if self.regular_expression:
                try:
                    if self.firstn and not re.match(self.firstn, name.get_first_name(), re.I|re.U|re.L):
                        val = 0
                    elif self.lastn and not re.match(self.lastn, name.get_surname(), re.I|re.U|re.L):
                        val = 0
                    elif self.suffix and not re.match(self.suffix, name.get_suffix(), re.I|re.U|re.L):
                        val = 0
                    elif self.title and not re.match(self.title, name.get_title(), re.I|re.U|re.L):
                        val = 0
                    elif self.calln and not re.match(self.calln, name.get_call_name(), re.I|re.U|re.L):
                        val = 0
                    elif self.nick and not re.match(self.nick, name.get_nick_name(), re.I|re.U|re.L):
                        val = 0
                    elif self.famnick and not re.match(self.famnick, name.get_family_nick_name(), re.I|re.U|re.L):
                        val = 0
                    else:
                        #obtain surnames
                        for surn in name.get_surname_list():
                            if self.prefix and re.match(self.prefix, surn.get_prefix(), re.I|re.U|re.L):
                                valpref = 1
                            if self.surn and re.match(self.surn, surn.get_surname(), re.I|re.U|re.L):
                                valsurn = 1
                            if self.con and re.match(self.con, surn.get_connector(), re.I|re.U|re.L):
                                valcon = 1
                            if self.patr and surn.get_origintype().value == NameOriginType.PATRONYMIC \
                                    and re.match(self.patr, surn.get_surname(), re.I|re.U|re.L):
                                valpatr = 1
                except re.error:
                    #indicate error in the pattern by matching everyone
                    return True
            else:
                if self.firstn and name.get_first_name().upper().find(self.firstn) == -1:
                    val = 0
                elif self.lastn and name.get_surname().upper().find(self.lastn) == -1:
                    val = 0
                elif self.suffix and name.get_suffix().upper().find(self.surn) == -1:
                    val = 0
                elif self.title and name.get_title().upper().find(self.title) == -1:
                    val = 0
                elif self.calln and name.get_call_name().upper().find(self.calln) == -1:
                    val = 0
                elif self.nick and name.get_nick_name().upper().find(self.nick) == -1:
                    val = 0
                elif self.famnick and name.get_family_nick_name().upper().find(self.famnick) == -1:
                    val = 0
                else:
                    #obtain surnames
                    for surn in name.get_surname_list():
                        if self.prefix and surn.get_prefix().upper().find(self.prefix) != -1:
                            valpref = 1
                        if self.surn and surn.get_surname().upper().find(self.surn) != -1:
                            valsurn = 1
                        if self.con and surn.get_connector().upper().find(self.con) != -1:
                            valcon = 1
                        if self.patr and surn.get_origintype().value == NameOriginType.PATRONYMIC \
                                and surn.get_surname().upper().find(self.patr) != -1:
                            valpatr = 1
            if val == 1 and valpref == 1 and valsurn == 1 and valcon == 1 and valpatr ==1:
                return True
        return False
