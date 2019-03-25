#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2019-2016 Gramps Development Team
# Copyright (C) 2019      Paul Culley
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
""" Generic upgrade module for both bsddb and dbapi dbs """
#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import os
import time
import logging
#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from . import DbTxn, DBLOGNAME
from ..lib import AttributeType, Place, PlaceHierType, PlaceType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

LOG = logging.getLogger(DBLOGNAME)


def gramps_upgrade_20(self):
    """
    Place update.
    """
    self.set_total(self.get_number_of_places())
    with DbTxn(_("Upgrade"), self, batch=True) as trans:
        for handle in self.get_place_handles():
            data = self.get_raw_place_data(handle)
            (hndl, gramps_id, title, long, lat, placeref_list, name,
             alt_names, the_type, code, alt_loc, urls, media_list,
             citation_list, note_list, change, tag_list, private) = data
            new_prefs = []
            for pref in placeref_list:  # placeref_list
                (ref, date) = pref
                n_pref = (ref, date, [], (PlaceHierType.ADMIN, ''))
                new_prefs.append(n_pref)
            old_names = [name]  # old name
            old_names.extend(alt_names)  # old alt names
            new_names = []
            for nam in old_names:  # all old names
                (pname, date, lang) = nam
                n_name = (pname, date, lang, [], [])  # abbrev_list, cit_list
                new_names.append(n_name)
            # LocationType
            # date = cal, mod, qual, val, text, sort, ny
            mtdate = (0, 0, 0, (0, 0, 0, False), '', 0, 0)
            new_types = [((PlaceType.OLD_NEW[the_type[0]], the_type[1]),
                          mtdate,  # empty date
                          [])]     # add cit_list
            eventrefs = []
            if code:
                # attr = privacy, citation_list, note_list, the_type, value
                code_attr = (0, [], [], (AttributeType.POSTAL, ''), code)
                attrs = [code_attr]
            else:
                attrs = []
            new_place_data = (hndl, gramps_id, title, long, lat, new_prefs,
                              new_names, new_types, eventrefs, alt_loc, urls,
                              media_list, citation_list, note_list, change,
                              tag_list, private, attrs)
            # TODO we need a raw commit method for generic and bsddb
            # This will work until we change something within a Place...
            place = Place().unserialize(new_place_data)
            self.commit_place(place, trans)
            self.update()


def make_zip_backup(self, dirname):
    """ This backs up the db files so an upgrade can be (manually) undone.

    TODO The code was copied from the plugins.db.bsddb.write; we may want to
    remove it from there and reference this as a more generic location.
    """
    import zipfile
    # In Windows reserved characters is "<>:"/\|?*"
    reserved_char = r':,<>"/\|?* '
    replace_char = "-__________"
    title = self.get_dbname()
    trans = title.maketrans(reserved_char, replace_char)
    title = title.translate(trans)

    if not os.access(dirname, os.W_OK):
        LOG.warning("Can't write technical DB backup for %s", title)
        return
    (grampsdb_path, db_code) = os.path.split(dirname)
    dotgramps_path = os.path.dirname(grampsdb_path)
    zipname = title + time.strftime("_%Y-%m-%d_%H-%M-%S") + ".zip"
    zippath = os.path.join(dotgramps_path, zipname)
    with zipfile.ZipFile(zippath, 'w') as myzip:
        for filename in os.listdir(dirname):
            pathname = os.path.join(dirname, filename)
            myzip.write(pathname, os.path.join(db_code, filename))
    LOG.warning("If upgrade and loading the Family Tree works, you can "
                "delete the zip file at %s", zippath)
