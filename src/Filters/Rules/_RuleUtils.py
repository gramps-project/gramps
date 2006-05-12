#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

import RelLib

#-------------------------------------------------------------------------
#
# Useful functions used by some rules
#
#-------------------------------------------------------------------------
def date_cmp(rule,value):
    sd = rule.get_start_date()
    s = rule.get_modifier()
    od = value.get_start_date()
    cmp_rule = (sd[2],sd[1],sd[0])
    cmp_value = (od[2],od[1],od[0])
    if s == RelLib.Date.MOD_BEFORE:
        return  cmp_rule > cmp_value
    elif s == RelLib.Date.MOD_AFTER:
        return cmp_rule < cmp_value
    else:
        return cmp_rule == cmp_value

def loose_date_cmp(rule,value):
    sd = rule.get_start_date()
    s = rule.get_modifier()
    od = value.get_start_date()
    cmp_rule = (sd[2],sd[1],sd[0])
    cmp_value = (od[2],od[1],od[0])

    if s == RelLib.Date.MOD_BEFORE:
        return  cmp_rule > cmp_value
    elif s == RelLib.Date.MOD_AFTER:
        return cmp_rule < cmp_value
    elif cmp_rule[0] and not cmp_rule[1] and not cmp_rule[2]:
        return cmp_rule[0] == cmp_value[0]
    elif cmp_rule[0] and cmp_rule[1] and not cmp_rule[2]:
        return cmp_rule[0:2] == cmp_value[0:2]
    else:
        return cmp_rule == cmp_value
