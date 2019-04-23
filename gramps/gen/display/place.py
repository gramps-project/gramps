#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014-2017  Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Class handling displaying of places.
"""

#---------------------------------------------------------------
#
# Python imports
#
#---------------------------------------------------------------
import os
import xml.dom.minidom

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..const import PLACE_FORMATS, GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ..config import config
from ..utils.location import get_location_list
from ..lib import PlaceType

#-------------------------------------------------------------------------
#
# PlaceFormat class
#
#-------------------------------------------------------------------------
class PlaceFormat:
    def __init__(self, name, levels, language, street, reverse):
        self.name = name
        self.levels = levels
        self.language = language
        self.street = street
        self.reverse = reverse


#-------------------------------------------------------------------------
#
# PlaceDisplay class
#
#-------------------------------------------------------------------------
class PlaceDisplay:

    def __init__(self):
        self.place_formats = []
        self.default_format = config.get('preferences.place-format')
        if os.path.exists(PLACE_FORMATS):
            try:
                self.load_formats()
                return
            except BaseException:
                print(_("Error in '%s' file: cannot load.") % PLACE_FORMATS)
        pf = PlaceFormat(_('Full'), ':', '', 0, False)
        self.place_formats.append(pf)

    def display_event(self, db, event, fmt=-1):
        if not event:
            return ""
        place_handle = event.get_place_handle()
        if place_handle:
            place = db.get_place_from_handle(place_handle)
            return self.display(db, place, event.get_date_object(), fmt)
        else:
            return ""

    def display(self, db, place, date=None, fmt=-1):
        if not place:
            return ""
        if not config.get('preferences.place-auto'):
            return place.title
        else:
            if fmt == -1:
                fmt = config.get('preferences.place-format')
            pf = self.place_formats[fmt]
            lang = pf.language
            all_places = get_location_list(db, place, date, lang)

            # Apply format string to place list
            index = _find_populated_place(all_places)
            places = []
            for slice in pf.levels.split(','):
                parts = slice.split(':')
                if len(parts) == 1:
                    offset = _get_offset(parts[0], index)
                    if offset is not None:
                        try:
                            places.append(all_places[offset])
                        except IndexError:
                            pass
                elif len(parts) == 2:
                    start = _get_offset(parts[0], index)
                    end = _get_offset(parts[1], index)
                    if start is None:
                        places.extend(all_places[:end])
                    elif end is None:
                        places.extend(all_places[start:])
                    else:
                        places.extend(all_places[start:end])

            if pf.street:
                types = [item[1] for item in places]
                try:
                    idx = types.index(PlaceType.NUMBER)
                except ValueError:
                    idx = None
                if idx is not None and len(places) > idx+1:
                    if pf.street == 1:
                        combined = (places[idx][0] + ' ' + places[idx+1][0],
                                    places[idx+1][1])
                    else:
                        combined = (places[idx+1][0] + ' ' + places[idx][0],
                                    places[idx+1][1])
                    places = places[:idx] + [combined] + places[idx+2:]

            names = [item[0] for item in places]
            if pf.reverse:
                names.reverse()

            # TODO for Arabic, should the next line's comma be translated?
            return ", ".join(names)

    def get_formats(self):
        return self.place_formats

    def set_formats(self, formats):
        self.place_formats = formats

    def load_formats(self):
        dom = xml.dom.minidom.parse(PLACE_FORMATS)
        top = dom.getElementsByTagName('place_formats')

        for fmt in top[0].getElementsByTagName('format'):
            name = fmt.attributes['name'].value
            levels = fmt.attributes['levels'].value
            language = fmt.attributes['language'].value
            street = int(fmt.attributes['street'].value)
            reverse = fmt.attributes['reverse'].value == 'True'
            pf = PlaceFormat(name, levels, language, street, reverse)
            self.place_formats.append(pf)

        dom.unlink()

    def save_formats(self):
        doc = xml.dom.minidom.Document()
        place_formats = doc.createElement('place_formats')
        doc.appendChild(place_formats)
        for fmt in self.place_formats:
            node = doc.createElement('format')
            place_formats.appendChild(node)
            node.setAttribute('name', fmt.name)
            node.setAttribute('levels', fmt.levels)
            node.setAttribute('language', fmt.language)
            node.setAttribute('street', str(fmt.street))
            node.setAttribute('reverse', str(fmt.reverse))
        with open(PLACE_FORMATS, 'w', encoding='utf-8') as f_d:
            doc.writexml(f_d, addindent='  ', newl='\n', encoding='utf-8')


def _get_offset(value, index):
    if index is not None and value.startswith('p'):
        try:
            offset = int(value[1:])
        except ValueError:
            offset = 0
        offset += index
    else:
        try:
            offset = int(value)
        except ValueError:
            offset = None
    return offset

def _find_populated_place(places):
    populated_place = None
    for index, item in enumerate(places):
        if int(item[1]) in [PlaceType.HAMLET, PlaceType.VILLAGE,
                            PlaceType.TOWN, PlaceType.CITY]:
            populated_place = index
    return populated_place

displayer = PlaceDisplay()
