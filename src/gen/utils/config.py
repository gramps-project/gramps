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
Configuration based utilities
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gen.config import config

#-------------------------------------------------------------------------
#
# Configuration based utilities
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
