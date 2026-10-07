#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""Check that the frozen pip can start and resolve a package before packaging."""

# -------------------------------------------------------------------------
# Python modules
# -------------------------------------------------------------------------
import logging
import subprocess
import sys

LOG = logging.getLogger(__name__)


def check_pip(executable: str) -> bool:
    """Reject failed pip processes as well as tracebacks in their output.

    :param executable: Path to the frozen pip executable.
    :returns: True only when both checks succeed.
    """
    for arguments in (
        ["--version"],
        ["install", "--dry-run", "--ignore-installed", "certifi"],
    ):
        try:
            result = subprocess.run(
                [executable, *arguments],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            LOG.error("Frozen pip check failed: %s", error)
            return False
        output = result.stdout + result.stderr
        LOG.info("Frozen pip %s: %s", " ".join(arguments), output.strip())
        if result.returncode != 0 or any(
            marker in output.lower()
            for marker in ("importerror", "modulenotfounderror", "traceback")
        ):
            LOG.error("Frozen pip check failed with exit code %s", result.returncode)
            return False
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(0 if check_pip(sys.argv[1]) else 1)
