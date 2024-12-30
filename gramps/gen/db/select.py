#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Doug Blank <doug.blank@gmail.com>
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

from gramps.gen.lib import (
    Citation,
    Event,
    Family,
    Media,
    Note,
    Person,
    Place,
    Repository,
    Source,
    Tag,
)


def sort_data(rows, specs):
    for key, reverse in reversed(specs):
        rows.sort(key=lambda item: item[key], reverse=reverse)
    return rows


def select_from_table(db, table_name, what, where, order_by, env):
    if order_by is None:
        yield from _select_from_table(db, table_name, what=what, where=where, env=env)
        return
    else:
        data = []

        for row in _select_from_table(db, table_name, what=what, where=where, env=env):
            if what is None:
                what_expr = ["person"]
            elif isinstance(what, str):
                what_expr = [what]
            else:
                what_expr = what
            data.append(dict(zip(what_expr, row)))

        specs = []
        for item in order_by:
            if isinstance(item, str):
                specs.append((item, False))
            else:
                specs.append((item[0], (False if item[1].lower() == "asc" else True)))

        for row in sort_data(data, specs):
            yield list(row.values())
        return


def _select_from_table(db, table_name, what, where, env):
    env = (
        env
        if env
        else {
            "Citation": Citation,
            "Event": Event,
            "Family": Family,
            "Media": Media,
            "Note": Note,
            "Person": Person,
            "Place": Place,
            "Repository": Repository,
            "Source": Source,
            "Tag": Tag,
        }
    )
    method = db._get_table_func(table_name.title(), "iter_func")
    for obj in method():
        env[table_name] = obj
        if where:
            where_value = eval(where, env)
        else:
            where_value = True

        if where_value:
            if what is None:
                what_value = table_name
            elif isinstance(what, str):
                what_value = eval(what, env)
            else:
                what_value = [eval(w, env) for w in what]

            yield what_value
