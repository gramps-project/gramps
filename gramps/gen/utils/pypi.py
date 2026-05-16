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
Stdlib-only wheel installer for PyPI packages.

Downloads and installs wheels from PyPI into a target directory using only the
Python standard library.  No pip, no certifi, no external dependencies.  SSL
uses the system trust store via ssl.create_default_context().

This installer is used in two distinct situations:

* **Frozen bundles** (cx_Freeze Windows AIO, macOS .app): pip is not available
  as a subprocess.  Both pure-Python and compiled wheels are supported; the
  compiled-wheel path selects the best wheel for the current Python version and
  platform (Windows ``win_amd64``/``win_arm64``/``win32``; macOS
  ``macosx_X_Y_arm64|x86_64|universal2``).

* **Source / snap / flatpak installs**: pip is available and is used instead
  (see ``gramps/gui/plug/_windows.py``).  ``install_package()`` is not called
  in this code path.

Limitations:
  - No version-conflict resolution across the full dependency graph.
    Direct dependencies of the requested package are installed; transitive
    conflicts are not detected.
  - No support for VCS URLs, local paths, or extras.
  - Compiled wheels are only matched for Windows and macOS; Linux manylinux/
    musllinux selection is not implemented (use pip on Linux instead).
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
import platform
import re
import ssl
import sys
import urllib.request
import zipfile

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

LOG = logging.getLogger(__name__)

_PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
_PURE_TAGS = {"py3-none-any", "py2.py3-none-any"}

# Cached result of _compatible_tags() so it is only computed once.
_COMPAT_TAGS: tuple[set[str], set[str], set[str]] | None = None


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
    """
    Return an SSL context that trusts the system certificate store.

    On macOS the standard Python.org installer does not wire OpenSSL to the
    macOS Keychain, so ``ssl.create_default_context()`` alone cannot verify
    PyPI's certificate.  If the ``certifi`` package is importable its CA
    bundle is used instead, which resolves the issue transparently.
    """
    try:
        import certifi  # optional; absent in frozen bundles without certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _ssl_cert_hint(exc: Exception) -> str:
    """
    Return a platform-specific hint when *exc* looks like an SSL cert error.

    Returns an empty string for non-SSL errors.
    """
    cause = getattr(exc, "reason", exc)
    if not (
        isinstance(cause, ssl.SSLError) and "CERTIFICATE_VERIFY_FAILED" in str(cause)
    ):
        return ""
    if platform.system() == "Darwin":
        return _(
            "\n\nOn macOS, Python may not have access to the system SSL "
            "certificates.  Try one of the following:\n"
            "  1. python.org installer: run 'Install Certificates.command' "
            "in your Python installation folder "
            "(e.g. /Applications/Python 3.x/).\n"
            "  2. pyenv / Homebrew / non-system Python: set the SSL_CERT_FILE "
            "environment variable before starting Gramps:\n"
            "       export SSL_CERT_FILE=/etc/ssl/cert.pem\n"
            "  3. Install the certifi package:  pip install certifi"
        )
    return _(
        "\n\nSSL certificate verification failed.  This is common with "
        "non-system Python installations (pyenv, conda) whose bundled "
        "OpenSSL does not know where system certificates are stored.  "
        "Try one of the following:\n"
        "  1. Install the certifi package:  pip install certifi\n"
        "  2. Set SSL_CERT_FILE to your system CA bundle before starting "
        "Gramps, e.g.:\n"
        "       export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt  "
        "(Debian/Ubuntu)\n"
        "       export SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt    "
        "(RHEL/Fedora)"
    )


def _compatible_tags() -> tuple[set[str], set[str], set[str]]:
    """
    Return (python_tags, abi_tags, platform_tags) for the running interpreter.

    Used to select compiled wheels on platforms where pip is unavailable
    (cx_Freeze Windows AIO, macOS .app bundles).  On Linux the caller should
    prefer pip; bare ``linux_{arch}`` tags are included only as a fallback.
    """
    global _COMPAT_TAGS
    if _COMPAT_TAGS is not None:
        return _COMPAT_TAGS

    major = sys.version_info.major
    minor = sys.version_info.minor

    # All cp3X tags for X <= current minor (covers abi3 wheels declaring an
    # older minimum CPython version), plus generic py3 / py2.py3 tags.
    py_tags: set[str] = {f"py{major}", "py3", "py2.py3"}
    for m in range(2, minor + 1):
        py_tags.add(f"cp{major}{m}")
        py_tags.add(f"py{major}{m}")

    abi_tags: set[str] = {f"cp{major}{minor}", "abi3", "none"}

    # "any" is always compatible — covers pure-Python wheels on every platform.
    plat_tags: set[str] = {"any"}
    system = platform.system()
    machine = platform.machine()

    if system == "Windows":
        if machine == "AMD64":
            plat_tags.add("win_amd64")
        elif machine == "ARM64":
            plat_tags.add("win_arm64")
        else:
            plat_tags.add("win32")

    elif system == "Darwin":
        try:
            ver_str = platform.mac_ver()[0]  # e.g. "14.4.0"
            parts = ver_str.split(".")
            cur_major = int(parts[0])
            cur_minor = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            # mac_ver() can return an empty string in some environments
            # (Docker, certain CI setups).  Fall back to pure wheels only.
            LOG.warning(
                "Could not determine macOS version from platform.mac_ver(); "
                "compiled wheels will not be matched."
            )
            cur_major = cur_minor = 0
        if cur_major >= 10:
            # universal2 wheels run on both arm64 and x86_64.
            archs = {machine, "universal2"}
            for arch in archs:
                for maj in range(10, cur_major + 1):
                    minor_start = 4 if maj == 10 else 0
                    minor_end = cur_minor + 1 if maj == cur_major else 16
                    for mn in range(minor_start, minor_end):
                        plat_tags.add(f"macosx_{maj}_{mn}_{arch}")

    else:
        # Linux fallback: bare linux tag.  Callers should use pip instead for
        # manylinux/musllinux support on non-frozen Linux installs.
        plat_tags.add(f"linux_{machine}")

    _COMPAT_TAGS = (py_tags, abi_tags, plat_tags)
    return _COMPAT_TAGS


def _is_compatible_wheel(file_info: dict) -> bool:
    """
    Return True if *file_info* describes a wheel compatible with the current
    Python interpreter and platform.

    Handles multi-tag filenames (dot-joined fields, e.g.
    ``macosx_11_0_arm64.macosx_10_12_universal2``) by treating each
    dot-separated token as an alternative; a wheel matches when at least one
    token from each of the three tag fields is in the compatible set.
    """
    filename = file_info.get("filename", "")
    if not filename.endswith(".whl"):
        return False
    parts = filename[:-4].split("-")
    if len(parts) < 5:
        return False
    # Dot-joined multi-tags: any token matching is sufficient.
    whl_py = set(parts[-3].split("."))
    whl_abi = set(parts[-2].split("."))
    whl_plat = set(parts[-1].split("."))
    compat_py, compat_abi, compat_plat = _compatible_tags()
    return bool(whl_py & compat_py and whl_abi & compat_abi and whl_plat & compat_plat)


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
            + _ssl_cert_hint(exc)
        ) from exc
    return json.loads(data)


def _version_sort_key(version: str) -> tuple[int, ...]:
    """
    Return a numeric sort key for a version string.

    Splits on dots and dashes and converts leading digit runs to ints so that
    ``"1.10"`` sorts after ``"1.9"``.  Not fully PEP 440 compliant (pre-release
    suffixes sort as zero) but sufficient for picking the newest release.
    """
    parts = []
    for segment in re.split(r"[.\-]", version):
        if not segment:
            continue
        m = re.match(r"^(\d+)", segment)
        parts.append(int(m.group(1)) if m else 0)
    return tuple(parts)


def _pick_wheel(meta: dict, package: str) -> dict:
    """
    Return the file entry for the best wheel in *meta* for the current platform.

    Preference order: pure-Python wheel from the latest release, then a
    platform-compatible compiled wheel from the latest release, then the same
    two searches across older releases.

    :raises PyPIInstallError: if no compatible wheel is found.
    """
    # 1. Pure wheel in latest release.
    for file_info in meta.get("urls", []):
        if _is_pure_wheel(file_info):
            return file_info
    # 2. Compiled wheel matching the current platform in latest release.
    for file_info in meta.get("urls", []):
        if _is_compatible_wheel(file_info):
            return file_info
    # urls only covers the latest release; search all releases newest-first.
    sorted_releases = sorted(
        meta.get("releases", {}).items(),
        key=lambda item: _version_sort_key(item[0]),
        reverse=True,
    )
    for _version, files in sorted_releases:
        # 3. Pure wheel in older release.
        for file_info in files:
            if _is_pure_wheel(file_info):
                return file_info
        # 4. Compiled wheel in older release.
        for file_info in files:
            if _is_compatible_wheel(file_info):
                return file_info
    raise PyPIInstallError(
        _("No compatible wheel found for '%s' on this platform.") % package
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


def _top_level_names(whl_zip: zipfile.ZipFile) -> list[str]:
    """
    Return the top-level importable package names listed in ``top_level.txt``.

    Reads the ``*.dist-info/top_level.txt`` entry from a wheel zip if present.
    Returns an empty list when the file is absent (common for modern wheels that
    match their PyPI name exactly).
    """
    path = next((n for n in whl_zip.namelist() if n.endswith("/top_level.txt")), None)
    if path is None:
        return []
    return [
        line.strip()
        for line in whl_zip.read(path).decode("utf-8", errors="replace").splitlines()
        if line.strip()
    ]


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
    try:
        data = _fetch_url(url)
    except Exception as exc:
        raise PyPIInstallError(
            _("Failed to download '%s': %s") % (filename, exc) + _ssl_cert_hint(exc)
        ) from exc

    if expected_sha256:
        _verify_sha256(data, expected_sha256, filename)

    with zipfile.ZipFile(io.BytesIO(data)) as whl:
        # Some packages have a PyPI name that differs from their importable
        # name (e.g. "Pillow" imports as "PIL").  top_level.txt lists the
        # actual importable names; if any are already present, skip extraction.
        for top_name in _top_level_names(whl):
            try:
                importlib.import_module(top_name)
                LOG.debug(
                    "'%s' already importable as '%s', skipping.", package, top_name
                )
                return
            except ImportError:
                pass
        wheel_meta = _wheel_metadata(whl)
        whl.extractall(target)

    installed.append(package)
    LOG.info("Installed '%s'.", package)

    # Install unconditional direct dependencies
    for dep in _direct_dependencies(wheel_meta):
        _install_one(dep, target, installed, seen)
