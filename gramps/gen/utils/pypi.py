#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Doug Blank
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
Minimal pure-Python wheel installer for PyPI packages.

Installs pure-Python (py3-none-any) wheels from PyPI into a target directory
using only the Python standard library.  No pip, no certifi, no external
dependencies.  SSL uses the system trust store via ssl.create_default_context().

Limitations:
  - Pure-Python wheels only (tag ``py3-none-any`` or ``py2.py3-none-any``).
    Compiled extensions (.so / .pyd) are not supported.
  - No version-conflict resolution across the full dependency graph.
    Direct dependencies of the requested package are installed; transitive
    conflicts are not detected.
  - No support for VCS URLs, local paths, or extras.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import email.parser
import hashlib
import importlib
import io
import json
import logging
import ssl
import urllib.request
import zipfile

LOG = logging.getLogger(__name__)

_PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
_PURE_TAGS = {"py3-none-any", "py2.py3-none-any"}


# -------------------------------------------------------------------------
#
# PyPIInstaller
#
# -------------------------------------------------------------------------
class PyPIInstallError(Exception):
    """Raised when a package cannot be installed from PyPI."""


# -------------------------------------------------------------------------
#
# Internal helpers
#
# -------------------------------------------------------------------------
def _ssl_context() -> ssl.SSLContext:
    """Return an SSL context that trusts the system certificate store."""
    return ssl.create_default_context()


def _fetch_url(url: str) -> bytes:
    """Download *url* and return the raw bytes."""
    ctx = _ssl_context()
    with urllib.request.urlopen(url, context=ctx) as response:
        return response.read()


def _pypi_metadata(package: str) -> dict:
    """Return the PyPI JSON metadata dict for *package*."""
    url = _PYPI_JSON_URL.format(package=package)
    LOG.debug("Fetching PyPI metadata: %s", url)
    try:
        data = _fetch_url(url)
    except Exception as exc:
        raise PyPIInstallError(
            _("Cannot reach PyPI for package '%s': %s") % (package, exc)
        ) from exc
    return json.loads(data)


def _pick_wheel(meta: dict, package: str) -> dict:
    """
    Return the file entry for the best pure-Python wheel in *meta*.

    Prefers the latest release; falls back to any available pure wheel.

    :raises PyPIInstallError: if no pure-Python wheel is found.
    """
    for file_info in meta.get("urls", []):
        if _is_pure_wheel(file_info):
            return file_info
    # urls only covers the latest release; search all releases as fallback
    for _version, files in reversed(list(meta.get("releases", {}).items())):
        for file_info in files:
            if _is_pure_wheel(file_info):
                return file_info
    raise PyPIInstallError(
        _(
            "No pure-Python wheel found for '%s'. "
            "Compiled packages cannot be installed by this installer."
        )
        % package
    )


def _is_pure_wheel(file_info: dict) -> bool:
    """Return True if *file_info* describes a pure-Python wheel."""
    filename = file_info.get("filename", "")
    if not filename.endswith(".whl"):
        return False
    # Wheel filename: {name}-{ver}(-{build})?-{pyver}-{abi}-{plat}.whl
    parts = filename[:-4].split("-")
    if len(parts) < 5:
        return False
    tag = "-".join(parts[-3:])
    return tag in _PURE_TAGS


def _verify_sha256(data: bytes, expected: str, filename: str) -> None:
    """Raise PyPIInstallError if the SHA-256 of *data* does not match."""
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise PyPIInstallError(
            _("SHA-256 mismatch for '%s': expected %s, got %s")
            % (filename, expected, actual)
        )


def _wheel_metadata(whl_zip: zipfile.ZipFile) -> dict[str, str]:
    """
    Parse the METADATA file from a wheel zip and return a dict of headers.

    Multi-value headers (e.g. Requires-Dist) are returned as
    newline-joined strings; callers should split on ``\\n``.
    """
    metadata_path = next(
        (n for n in whl_zip.namelist() if n.endswith("/METADATA")), None
    )
    if metadata_path is None:
        return {}
    raw = whl_zip.read(metadata_path).decode("utf-8", errors="replace")
    parser = email.parser.HeaderParser()
    msg = parser.parsestr(raw)
    result: dict[str, str] = {}
    for key in set(msg.keys()):
        values = msg.get_all(key, [])
        result[key.lower()] = "\n".join(values)
    return result


def _direct_dependencies(wheel_meta: dict[str, str]) -> list[str]:
    """
    Return the list of direct dependency package names from wheel metadata.

    Only unconditional ``Requires-Dist`` entries are included — those with
    environment markers (``; extra ==`` or ``; sys_platform ==``) are skipped
    to keep the installer simple.
    """
    raw = wheel_meta.get("requires-dist", "")
    deps: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip conditional deps (extras and environment markers)
        if ";" in line:
            continue
        # Strip version specifier: "requests>=2.0" → "requests"
        name = line.split()[0].split(">")[0].split("<")[0].split("=")[0].split("!")[0]
        name = name.strip()
        if name:
            deps.append(name)
    return deps


# -------------------------------------------------------------------------
#
# Public API
#
# -------------------------------------------------------------------------
def install_package(package: str, target: str) -> list[str]:
    """
    Download and install *package* from PyPI into *target*.

    Also installs unconditional direct dependencies of *package* that are
    not already importable.  Returns a list of package names that were
    installed.

    Only pure-Python wheels (``py3-none-any``) are supported.

    :param package: PyPI package name (e.g. ``"pypdf"``).
    :param target: Filesystem path to install into (e.g. ``LIB_PATH``).
    :returns: List of package names that were installed.
    :raises PyPIInstallError: if the package or a dependency cannot be
        installed.
    """
    installed: list[str] = []
    _install_one(package, target, installed, set())
    return installed


def _install_one(
    package: str, target: str, installed: list[str], seen: set[str]
) -> None:
    """
    Recursively install *package* and its unconditional dependencies.

    *seen* prevents infinite loops in the (unlikely) case of circular deps.
    """
    canonical = package.lower().replace("-", "_")
    if canonical in seen:
        return
    seen.add(canonical)

    # Skip packages that are already importable
    try:
        importlib.import_module(canonical)
        LOG.debug("'%s' is already importable, skipping.", canonical)
        return
    except ImportError:
        pass

    LOG.info("Installing '%s' from PyPI into %s", package, target)
    meta = _pypi_metadata(package)
    file_info = _pick_wheel(meta, package)

    url = file_info["url"]
    filename = file_info["filename"]
    expected_sha256 = file_info.get("digests", {}).get("sha256", "")

    LOG.debug("Downloading %s", url)
    data = _fetch_url(url)

    if expected_sha256:
        _verify_sha256(data, expected_sha256, filename)

    with zipfile.ZipFile(io.BytesIO(data)) as whl:
        wheel_meta = _wheel_metadata(whl)
        whl.extractall(target)

    installed.append(package)
    LOG.info("Installed '%s'.", package)

    # Install unconditional direct dependencies
    for dep in _direct_dependencies(wheel_meta):
        _install_one(dep, target, installed, seen)
