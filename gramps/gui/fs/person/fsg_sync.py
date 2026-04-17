#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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

from __future__ import annotations

# Gramps
from gramps.gen.config import config
from gramps.gen.plug import Gramplet

# Mixins
from .mixins.helpers import AuthMixin
from .mixins.compare_gtk import CompareGtkMixin
from .mixins.sources_dialog import SourcesDialogMixin
from .mixins.source_import import SourceImportMixin
from gramps.gen.fs.person.mixins.cache import CacheMixin
from gramps.gen.fs.person.mixins.helpers import HelpersMixin


class FSG_Sync(
    AuthMixin,
    CompareGtkMixin,
    SourcesDialogMixin,
    SourceImportMixin,
    CacheMixin,
    HelpersMixin,
    Gramplet,
):
    CONFIG = config.register_manager("FSG_Sync")
    CONFIG.register("preferences.fs_username", "")
    CONFIG.register("preferences.fs_pass", "")
    CONFIG.register("preferences.fs_client_id", "")
    CONFIG.register("preferences.fs_image_download_dir", "")
    CONFIG.register("preferences.fs_web_compare_url", "")
    CONFIG.load()

    fs_Tree = None
    fs_TreeSearch = None
    FSID = None
    _cache = None
