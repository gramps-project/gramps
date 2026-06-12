#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Gramps Development Team
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Test-harness helper: probe whether the bsddb database backend is loadable.

The legacy-bsddb import tests in :mod:`gramps.plugins.test.imports_test` must
*skip* — not *fail* — when the bsddb backend cannot be loaded, on every
platform rather than only on Windows.  This helper answers the exact question
the plugin loader asks at ``gramps/plugins/db/bsddb/bsddb.py`` lines 32-35:
is :mod:`berkeleydb` (the maintained successor) importable, or failing that
:mod:`bsddb3` (deprecated since Python 3.6)?  If neither is, the backend is
unavailable and ``make_database("bsddb")`` would raise.
"""


def bsddb_backend_available():
    """Return ``True`` iff the bsddb backend is loadable on this platform.

    Mirrors the loader's probe order at ``gramps/plugins/db/bsddb/bsddb.py``
    lines 32-35 (try ``berkeleydb`` then ``bsddb3``) so the test harness's
    notion of "bsddb is available" matches what ``make_database("bsddb")``
    will actually find.  Any import error — a missing package or a failed
    shared library — counts as unavailable, exactly as the loader tolerates.
    """
    try:
        from berkeleydb.db import DB  # noqa: F401

        return True
    except Exception:
        pass
    try:
        from bsddb3.db import DB  # noqa: F401

        return True
    except Exception:
        pass
    return False
