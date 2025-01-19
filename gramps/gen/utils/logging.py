#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Doug Blank <doug.blank@gmail.com>
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
Logging utilities
"""

import logging
from typing import Any, Set

LOGGER = logging.getLogger(".")
LOG_ONCE_CACHE: Set[str] = set()


def log_once_at_level(
    logging_level: int, message: str, *args: Any, **kwargs: Any
) -> None:
    """
    Log the given message once at the given level then at the DEBUG
    level on further calls.

    This is a global setting, removed with
    remove_log_once_at_level(MESSAGE)
    """
    global LOG_ONCE_CACHE

    if message not in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(message)
        LOGGER.log(logging_level, message, *args, **kwargs)
    else:
        LOGGER.debug(message, *args, **kwargs)


def remove_log_once_at_level(message: str) -> None:
    """
    Clears the specified message from the global
    log-once-per-session cache, enabling it to be logged at the
    original level again when ``log_once_at_level()`` is subsequently
    called.
    """
    global LOG_ONCE_CACHE

    LOG_ONCE_CACHE.discard(message)
