#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014-2017  Nick Hall
# Copyright (C) 2019       Paul Culley
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

# ---------------------------------------------------------------
#
# Python imports
#
# ---------------------------------------------------------------
import os
import orjson

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
import gramps.gen.lib as lib
from ..lib.json_utils import data_to_object, object_to_string
from ..config import config
from ..utils.location import get_location_list
from ..lib import PlaceGroupType as P_G
from ..lib import PlaceHierType
from ..const import PLACE_FORMATS
from ..const import GRAMPS_LOCALE as glocale


_ = glocale.translation.gettext


PFVERS = 1  # Place Format Version, change if incompatible with older


# -------------------------------------------------------------------------
#
# PlaceFormat class
#
# -------------------------------------------------------------------------
class PlaceFormat:
    """
    This class stores the basic information about the place format
    """

    def __init__(self, name, language="", reverse=False, rules=None):
        self.name = name  # str name of format
        self.language = language  # Language desired of format
        self.reverse = reverse  # Order of place title names is reversed
        if rules is None:
            rules = []
        self.rules = rules  # list of rules for the format
        self.version = PFVERS  # detects if the format or rule is different

    def get_object_state(self):
        """
        Get the current object state as a dictionary.

        :returns: Returns a dictionary of attributes that represent the state
                  of the object.
        :rtype: dict
        """
        attr_dict = dict(
            (key, value)
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        attr_dict["_class"] = self.__class__.__name__
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using information provided in the given
        dictionary.

        :param attr_dict: A dictionary of attributes that represent the state of
                          the object.
        :type attr_dict: dict
        """
        self.__dict__.update(attr_dict)


# -------------------------------------------------------------------------
#
# PlaceRule class
#
# -------------------------------------------------------------------------
class PlaceRule:
    """
    This class stores the place format rules.
    """

    V_NONE = 0  # visibility of item; None
    V_STNUM = 1  # visibility of street/number; visible, street first
    V_NUMST = 2  # visibility of street/number; visible, number first
    V_ALL = 3  # visibility of item; All
    V_SMALL = 4  # visibility of item; Only smallest of group or type
    V_LARGE = 5  # visibility of item; Only largest of group or type
    T_GRP = 0  # What does rule work with; Place Group
    T_TYP = 1  # What does rule work with; Place Type
    T_ST_NUM = 2  # What does rule work with; Street and number
    A_NONE = -2  # indicates no abbrev, val is added to PlaceAbbrevType
    A_FIRST = -3  # indicates first abbrev, val is added to PlaceAbbrevType

    VIS_MAP = {
        V_NONE: _("Hidden"),
        V_SMALL: _("Show Smallest"),
        V_LARGE: _("Show Largest"),
        V_ALL: _("Show All"),
        V_STNUM: _("Street Number"),
        V_NUMST: _("Number Street"),
    }

    def __init__(self, where, r_type, r_value, vis, abb, hier):
        """Place Format Rule"""
        self.hier = hier  # PlaceHierType of format
        self.where = where  # None, or place handle
        self.where_id = None  # the place gramps_id
        self.where_title = None  # the place title
        self.type = r_type  # on of T_ group, type, or street/num
        self.value = r_value  # int, PlaceType group or type number
        self.vis = vis  # int, one of the V_ values above
        self.abb = abb  # PlaceAbbrevType with extra values, A_NONE, A_FIRST

    def get_object_state(self):
        """
        Get the current object state as a dictionary.

        :returns: Returns a dictionary of attributes that represent the state
                  of the object.
        :rtype: dict
        """
        attr_dict = dict(
            (key, value)
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        attr_dict["_class"] = self.__class__.__name__
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using information provided in the given
        dictionary.

        :param attr_dict: A dictionary of attributes that represent the state of
                          the object.
        :type attr_dict: dict
        """
        self.__dict__.update(attr_dict)


# enable db to unserialize our classes
lib.__dict__["PlaceFormat"] = PlaceFormat
lib.__dict__["PlaceRule"] = PlaceRule


# -------------------------------------------------------------------------
#
# PlaceDisplay class
#
# -------------------------------------------------------------------------
class PlaceDisplay:
    """
    This is the place title display and format storage class.
    """

    def __init__(self):
        self.place_formats = []
        # initialize the default format
        _pf = PlaceFormat(_("Full"))
        self.place_formats.append(_pf)

    def display_event(self, _db, event, fmt=-1):
        """
        This displays an event's place title according to the specified
        format.
        """
        if not event:
            return ""
        place_handle = event.get_place_handle()
        if place_handle:
            place = _db.get_place_from_handle(place_handle)
            return self.display(_db, place, event.get_date_object(), fmt)
        return ""

    def display(self, _db, place, date=None, fmt=-1):
        """
        This is the place title display routine.  It displays a place title
        according to the format and rules defined in PlaceFormat.
        """
        if not place:
            return ""
        if not config.get("preferences.place-auto"):
            return place.title
        if fmt == -1:
            fmt = config.get("preferences.place-format")
            if fmt > len(self.place_formats) - 1:
                config.set("preferences.place-format", 0)
        if fmt > len(self.place_formats) - 1:
            fmt = 0
        _pf = self.place_formats[fmt]
        # sort the rules by hierarchy so we can do one hierarchy at a time
        hiers = [PlaceHierType()]
        rulesets = [[]]
        for rule in _pf.rules:
            for hier, rules in zip(hiers, rulesets):
                if hier == rule.hier:
                    rules.append(rule)
                    break
            else:
                hiers.append(rule.hier)
                rulesets.append([rule])
        lang = _pf.language

        # process each hierarchy, starting with ADMIN
        title = names = ""
        for hier, rules in zip(hiers, rulesets):

            all_places = get_location_list(_db, place, date, lang, hier=hier)

            # Apply format to place list
            # if ADMIN, start with everything shown, otherwise nothing shown
            # val[0] is the place name
            if hier == PlaceHierType.ADMIN:
                places = [val[0] for val in all_places]
            else:
                places = [None] * len(all_places)
            for rule in rules:
                if rule.where:
                    # this rule applies to a specific place
                    for plac in all_places:
                        if plac[2] == rule.where:  # test if handles match
                            break  # rule is good for this place
                    else:  # no match found for handle
                        continue  # skip this rule
                first = False
                if rule.type == PlaceRule.T_GRP:
                    # plac[4] and rule.value are PlaceGroupType
                    if rule.vis == PlaceRule.V_LARGE:
                        # go from largest down
                        for indx in range(len(all_places) - 1, -1, -1):
                            plac = all_places[indx]
                            # plac[4] is a PlaceGroupType
                            if plac[4] == rule.value:
                                # match on group
                                if first:  # If we found first one already
                                    places[indx] = None  # remove this one
                                else:
                                    first = True
                                    self._show(plac, rule, places, indx)
                    else:
                        # work from smallest up
                        for indx, plac in enumerate(all_places):
                            if plac[4] == rule.value:
                                # match on group
                                if rule.vis == PlaceRule.V_SMALL:
                                    if first:  # If we found first one already
                                        places[indx] = None  # remove this one
                                    else:
                                        first = True
                                        self._show(plac, rule, places, indx)
                                elif rule.vis == PlaceRule.V_ALL:
                                    self._show(plac, rule, places, indx)
                                else:  # rule.vis == PlaceRule.V_NONE:
                                    places[indx] = None  # remove this one
                elif rule.type == PlaceRule.T_TYP:
                    # plac[1] and rule.value are PlaceType
                    if rule.vis == PlaceRule.V_LARGE:
                        # go from largest down
                        for indx in range(len(all_places) - 1, -1, -1):
                            plac = all_places[indx]
                            if plac[1].is_same(rule.value):
                                # match on ptype
                                if first:  # If we found first one already
                                    places[indx] = None  # remove this one
                                else:
                                    first = True
                                    self._show(plac, rule, places, indx)
                    else:
                        # work from smallest up
                        for indx, plac in enumerate(all_places):
                            if plac[1].is_same(rule.value):
                                # match on group
                                if rule.vis == PlaceRule.V_SMALL:
                                    if first:  # If we found first one already
                                        places[indx] = None  # remove this one
                                    else:
                                        first = True
                                        self._show(plac, rule, places, indx)
                                elif rule.vis == PlaceRule.V_ALL:
                                    self._show(plac, rule, places, indx)
                                else:  # rule.vis == PlaceRule.V_NONE:
                                    places[indx] = None  # remove this one
                else:
                    # we have a rule about street/number
                    _st = _num = None
                    for indx, plac in enumerate(all_places):
                        # plac[1] is PlaceType
                        p_type = plac[1].pt_id
                        if (
                            p_type == "Street" or p_type == "Number"
                        ) and rule.vis == PlaceRule.V_NONE:
                            places[indx] = None  # remove this one
                        elif p_type == "Street":
                            _st = indx
                            places[indx] = plac[0]
                        elif p_type == "Number":
                            _num = indx
                            places[indx] = plac[0]
                    if _st is not None and _num is not None:
                        if (rule.vis == PlaceRule.V_NUMST and _num < _st) or (
                            rule.vis == PlaceRule.V_STNUM and _num > _st
                        ):
                            continue  # done with rule
                        # need to swap final names
                        street = places[_st]
                        places[_st] = places[_num]
                        places[_num] = street

            # For the ADMIN hierarchy, make sure that the smallest place is
            # included for places not deeply enclosed.
            if hier == PlaceHierType.ADMIN:
                s_groups = [P_G.PLACE, P_G.UNPOP, P_G.NONE, P_G.BUILDING]
                if places[0] is None and all_places[0][4] not in s_groups:
                    places[0] = all_places[0][0]

            names = ""
            for indx in (
                range(len(all_places) - 1, -1, -1)
                if _pf.reverse
                else range(len(all_places))
            ):
                name = places[indx]
                if name is not None:
                    names += (_(", ") + name) if names else name
            if title and names:
                title += _("; ")
            title += names

        return title

    @staticmethod
    def _show(place, rule, places, indx):
        """
        Place is to be shown, but need to deal with abbreviations.
        place is a tuple of place to show
        rule.abb is the selected abbreviation instruction
        places is list of place tuples to show
        """
        do_abb = int(rule.abb)
        name, dummy_type, dummy_hndl, abblist, _group = place
        if do_abb == PlaceRule.A_FIRST:
            if abblist:
                name = abblist[0].get_value()
        elif do_abb != PlaceRule.A_NONE:
            for abb in abblist:
                if rule.abb == abb.get_type():
                    name = abb.get_value()
        places[indx] = name

    def get_formats(self):
        """return the available formats as a list"""
        return self.place_formats

    def set_formats(self, formats):
        """set a list of place formats"""
        self.place_formats = formats

    def load_formats(self, formats):
        """
        :param formats: json string containing list of formats from db metadata.
        :type formats: string.

        load formats obtained from db, and from the saved json file.

        If the current session has no user formats, we will load the last
        saved json formats to form an initial format set.

        If the current session already has user formats, from a prior opened
        db, we will keep them to form an initial format set.

        If the newly opened db making this call has a named format we will
        not change it, and update the session to use it.

        If the current contents of place formats from this session has new user
        formats, they will end up in the db.
        """
        formats = data_to_object(formats)
        if len(self.place_formats) == 1 and os.path.exists(PLACE_FORMATS):
            try:
                with open(PLACE_FORMATS, "r", encoding="utf8") as _fp:
                    txt = _fp.read()
                    load_formats = data_to_object(orjson.loads(txt))
            except BaseException:
                print(_("Error in '%s' file: cannot load.") % PLACE_FORMATS)
            for indx, fmt in enumerate(load_formats):
                # if not right version, just drop the format
                if not hasattr(fmt, "version") or fmt.version != PFVERS or not indx:
                    continue
                self.place_formats.append(fmt)
        for indx, fmt in enumerate(formats):
            # if not right version, just drop the format
            if not hasattr(fmt, "version") or fmt.version != PFVERS or not indx:
                continue
            for index in range(len(self.place_formats)):
                if fmt.name == self.place_formats[index].name:
                    self.place_formats[index] = fmt
                    break
            else:
                self.place_formats.append(fmt)

    def save_formats(self):
        """this saves the current format set to the json file.  Saving to the
        db is done elsewhere.
        """
        if len(self.place_formats) > 1:
            txt = object_to_string(self.place_formats)
            try:
                with open(PLACE_FORMATS, "w", encoding="utf8") as _fp:
                    _fp.write(txt)
                return txt
            except BaseException:
                print(_("Failure writing %s") % PLACE_FORMATS)


displayer = PlaceDisplay()
