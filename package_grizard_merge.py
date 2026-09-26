#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Build the standalone ``GrizardMerge.zip`` addon package.

Collects the Grizard backend, GUI, and tool modules scattered across
``gramps/gen/grizard``, ``gramps/gui/grizard``, and ``gramps/plugins/tool``
into a single flat ``GrizardDataMerge/`` addon directory inside a zip file,
rewriting the ``gramps.gen.grizard`` / ``gramps.gui.grizard`` absolute
imports and intra-package relative imports to flat sibling imports so the
bundle loads under Gramps' plugin importer (which imports the tool module
top-level via ``__import__`` with the addon directory on ``sys.path``).
Also embeds the standalone addon registration file
``GrizardDataMerge/GrizardDataMerge.gpr.py`` (mirroring the ``grizardmerge``
entry in ``gramps/plugins/tool/tools.gpr.py``). Newlines are normalized to
LF so the output is identical regardless of the checkout's line-ending
setting.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import argparse
import logging
import re
import zipfile
from pathlib import Path

LOG = logging.getLogger(__name__)

PACKAGE = "GrizardDataMerge"

GPR_FILENAME = "GrizardDataMerge.gpr.py"

# Standalone addon registration file, written into the bundle as
# ``GrizardDataMerge/GrizardDataMerge.gpr.py``. Mirrors the ``grizardmerge``
# entry in ``gramps/plugins/tool/tools.gpr.py`` but uses hardcoded values
# instead of the shared ``MODULE_VERSION`` / ``TOOLS_HELP`` constants, which
# are not available to a standalone addon directory. ``{target}`` is filled
# in from ``--gramps-target`` at build time. Status is STABLE (not UNSTABLE)
# so release/frozen Gramps installs keep the plugin: release builds run with
# ``stable_only=True`` and silently drop UNSTABLE plugins at scan time.
GPR_TEMPLATE = """\
# Grizard Data Merge addon registration.
from gramps.gen.plug._pluginreg import TOOL, TOOL_DBPROC, TOOL_MODE_GUI, STABLE
from gramps.gen.const import URL_MANUAL_PAGE, GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

register(
    TOOL,
    id="grizardmerge",
    name=_("Grizard Data Merge"),
    description=_(
        "Loads a GEDCOM file and finds people that may "
        "represent the same person for merging."
    ),
    version="0.1.0",
    gramps_target_version="{target}",
    status=STABLE,
    fname="grizardmerge.py",
    authors=["Kevin White"],
    authors_email=["gocaveman@gmail.com"],
    category=TOOL_DBPROC,
    toolclass="GrizardMergeTool",
    optionclass="GrizardMergeToolOptions",
    tool_modes=[TOOL_MODE_GUI],
    help_url=URL_MANUAL_PAGE + "_-_Navigation#Tools",
)
"""

DEFAULT_GRAMPS_TARGET = "6.0"

# Map of archive member name -> source file relative to the repo root.
SOURCES: dict[str, str] = {
    "gedcom.py": "gramps/gen/grizard/gedcom.py",
    "grizard.py": "gramps/gen/grizard/grizard.py",
    "grizardcompare.py": "gramps/gui/grizard/grizardcompare.py",
    "grizardlauncher.py": "gramps/gui/grizard/grizardlauncher.py",
    "grizardmerge.py": "gramps/plugins/tool/grizardmerge.py",
    "grizardmergedialog.py": "gramps/gui/grizard/grizardmergedialog.py",
}

# Grizard sibling modules bundled flat in the addon directory. Gramps loads
# the tool module top-level (``__import__("grizardmerge")`` with the addon
# directory on ``sys.path``), so intra-bundle imports must be flat as well:
# both ``gramps.gen.grizard.X`` / ``gramps.gui.grizard.X`` absolute imports
# and ``.X`` relative imports become ``X`` sibling imports.
SIBLINGS = (
    "gedcom",
    "grizard",
    "grizardcompare",
    "grizardlauncher",
    "grizardmerge",
    "grizardmergedialog",
)

# Absolute imports that must become flat sibling imports in the bundle.
# Order matters: longest prefixes first.
REWRITES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"from\s+gramps\.gen\.grizard\.gedcom\s+import\b"),
        "from gedcom import",
    ),
    (
        re.compile(r"from\s+gramps\.gen\.grizard\.grizard\s+import\b"),
        "from grizard import",
    ),
    (
        re.compile(r"from\s+gramps\.gui\.grizard\.grizardcompare\s+import\b"),
        "from grizardcompare import",
    ),
    (
        re.compile(
            r"from\s+gramps\.gui\.grizard\.grizardlauncher\s+import\b" r"(?!\s*\()",
        ),
        "from grizardlauncher import",
    ),
    (
        re.compile(r"from\s+gramps\.gui\.grizard\.grizardmergedialog\s+import\b"),
        "from grizardmergedialog import",
    ),
    (
        re.compile(
            r"from\s+\.(gedcom|grizard|grizardcompare|grizardlauncher|"
            r"grizardmerge|grizardmergedialog)\s+import\b"
        ),
        r"from \1 import",
    ),
)


def rewrite_imports(text: str) -> str:
    """Rewrite Grizard imports to flat sibling imports."""
    for pattern, replacement in REWRITES:
        text = pattern.sub(replacement, text)
    return text


def rewrite_imports_bytes(data: bytes) -> bytes:
    """Rewrite Grizard imports, normalizing to LF newlines."""
    lines = data.decode("utf-8").splitlines(keepends=False)
    rewritten = [rewrite_imports(line) for line in lines]
    return ("\n".join(rewritten) + "\n").encode("utf-8")


def build_gpr(gramps_target: str) -> bytes:
    """Render the standalone addon registration file."""
    return GPR_TEMPLATE.format(target=gramps_target).encode("utf-8")


def build_zip(repo_root: Path, output: Path, gramps_target: str) -> Path:
    """Build the ``GrizardMerge.zip`` bundle next to this script."""
    members: dict[str, bytes] = {}
    for member, source in SOURCES.items():
        path = repo_root / source
        if not path.is_file():
            raise FileNotFoundError(f"Missing source file: {path}")
        text = path.read_bytes()
        members[member] = rewrite_imports_bytes(text)
        LOG.debug("Added %s (%d bytes)", source, len(members[member]))
    output.unlink(missing_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(PACKAGE + "/", b"")
        archive.writestr(PACKAGE + "/__init__.py", b"")
        archive.writestr(f"{PACKAGE}/{GPR_FILENAME}", build_gpr(gramps_target))
        for member in sorted(members):
            archive.writestr(f"{PACKAGE}/{member}", members[member])
    LOG.info("Wrote %s (%d bytes)", output, output.stat().st_size)
    return output


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build the standalone GrizardMerge.zip addon package."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "GrizardMerge.zip",
        help="Destination zip file (default: GrizardMerge.zip next to the script).",
    )
    parser.add_argument(
        "--gramps-target",
        default=DEFAULT_GRAMPS_TARGET,
        help=(
            "Gramps target version written into gramps_target_version "
            f"(default: {DEFAULT_GRAMPS_TARGET}). Must match the major.minor "
            "of the Gramps install or scan_dir() drops the plugin."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Build the bundle and report the result."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parent
    output: Path = args.output
    if not output.is_absolute():
        output = repo_root / output
    try:
        built = build_zip(repo_root, output, args.gramps_target)
    except FileNotFoundError as error:
        LOG.error("%s", error)
        return 1
    print(str(built))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
