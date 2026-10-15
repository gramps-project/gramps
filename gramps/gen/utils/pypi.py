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

* **Source / snap installs with pip**: pip is available and is used instead
  (see ``gramps/gui/plug/_windows.py``).  ``install_package()`` is not called
  in this code path.

* **Flatpak / pip-less environments**: Flathub and other sandboxed runtimes
  strip ``pip`` from the Python installation.  ``_pip_available()`` detects
  this and routes to ``install_package()`` exactly as for frozen bundles.

Limitations:
  - No support for VCS URLs or local paths.
  - Constraint gathering uses the *latest* release's dep list from the PyPI
    JSON API; if an older version is resolved, its actual transitive deps
    may differ slightly (tier-2 limitation).
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import ctypes
import email.parser
import functools
import hashlib
import importlib
import importlib.metadata
import io
import json
import logging
import os
import platform
import re
import ssl
import subprocess
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

# Mapping from Python import names to their PyPI distribution names.
# Many packages have an import name that differs from the PyPI package name.
# Addon authors declare requires_mod using the import name; this table lets
# install_package() and pip look up the correct installable name.
#
# Only add entries where the import name would either:
#  - return a 404 from PyPI (e.g. "cv2", "yaml"),
#  - resolve to a completely different package (e.g. "serial" → a JSON lib),
#  - or resolve to a dead/stub package with no wheels (e.g. "PIL", "sklearn").
#
# Do NOT add entries where the import name already maps correctly, even with
# different capitalisation — PyPI normalises case and underscores/hyphens.
_IMPORT_TO_PYPI: dict[str, str] = {
    # Image processing
    "PIL": "Pillow",
    "cv2": "opencv-python",
    # Data / science
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "dateutil": "python-dateutil",
    # Web / network
    "bs4": "beautifulsoup4",
    "serial": "pyserial",
    "usb": "pyusb",
    # Cryptography
    "nacl": "PyNaCl",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyOpenSSL",
    # GUI (unlikely in headless addons, but common mismatch)
    "wx": "wxPython",
}

# Architecture sets for manylinux legacy tag aliases (PEP 513/571/599).
_MANYLINUX1_ARCHS: frozenset[str] = frozenset({"x86_64", "i686"})
_MANYLINUX2010_ARCHS: frozenset[str] = frozenset({"x86_64", "i686"})
_MANYLINUX2014_ARCHS: frozenset[str] = frozenset(
    {"x86_64", "i686", "aarch64", "armv7l", "ppc64", "ppc64le", "s390x"}
)

# Compiled pattern for parsing a PEP 508 requirement string.
# Captures: name, optional extras (without brackets), version spec, optional marker.
_REQ_RE: re.Pattern[str] = re.compile(
    r"^\s*"
    r"(?P<name>[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"\s*(?:\[(?P<extras>[^\]]*)\])?\s*"
    r"(?P<spec>[^;]*)"
    r"(?:;\s*(?P<marker>.+))?"
    r"\s*$"
)

# Marker variables compared using version ordering rather than string ordering.
_VERSION_VARS: frozenset[str] = frozenset(
    {
        "python_version",
        "python_full_version",
        "implementation_version",
    }
)


# -------------------------------------------------------------------------
#
# Bundle detection
#
# -------------------------------------------------------------------------
def is_frozen() -> bool:
    """Return True when running inside a frozen bundle where sys.executable
    is not a usable Python interpreter for spawning pip.

    Most bundlers set sys.frozen, but some do not:
    - macOS .app packagers may leave sys.frozen unset; we detect them by
      checking whether sys.executable points into a .app bundle.
    - Windows bundlers such as Nuitka and PyOxidizer produce a named app
      binary (e.g. Gramps.exe) rather than a python*.exe interpreter; we
      detect those by checking the executable basename.
    """
    if getattr(sys, "frozen", False):
        return True
    exe = sys.executable or ""
    # macOS .app bundle: sys.executable is e.g. '/Foo.app' or
    # '/Foo.app/Contents/MacOS/Gramps'
    if exe.endswith(".app") or ".app/" in exe:
        return True
    # Windows bundle (Nuitka, PyOxidizer, …): sys.executable is the app
    # binary (Gramps.exe), not a python*.exe interpreter.
    if sys.platform == "win32":
        basename = os.path.basename(exe).lower()
        return not (basename.startswith("python") or basename.startswith("pypy"))
    return False


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


@functools.cache
def _glibc_version() -> tuple[int, int] | None:
    """Return ``(major, minor)`` of the system glibc, or ``None`` if not glibc.

    Tries the ctypes ``gnu_get_libc_version`` symbol first (most reliable),
    then falls back to ``platform.libc_ver()``.
    """
    # Primary: call gnu_get_libc_version() via ctypes.
    try:
        process_namespace = ctypes.CDLL(None)
        gnu_get_libc_version = process_namespace.gnu_get_libc_version
        gnu_get_libc_version.restype = ctypes.c_char_p
        ver_bytes = gnu_get_libc_version()
        if ver_bytes:
            parts = ver_bytes.decode("ascii").split(".")
            return int(parts[0]), int(parts[1])
    except Exception:
        pass
    # Fallback: platform.libc_ver() reads the libc binary.
    try:
        libc_name, libc_ver = platform.libc_ver()
        if libc_name == "glibc" and libc_ver:
            parts = libc_ver.split(".")
            return int(parts[0]), int(parts[1])
    except Exception:
        pass
    return None


@functools.cache
def _musl_version() -> tuple[int, int] | None:
    """Return ``(major, minor)`` of musl libc, or ``None`` if not a musl system.

    Detects musl by looking for its dynamic linker at
    ``/lib/ld-musl-{arch}.so.1`` and running it to parse the version line.
    """
    machine = platform.machine()
    # musl uses "arm" for all 32-bit ARM variants (armv7l, armv6l, …).
    musl_arch = "arm" if machine.startswith("armv") else machine
    candidate = f"/lib/ld-musl-{musl_arch}.so.1"
    if not os.path.exists(candidate):
        return None
    try:
        result = subprocess.run(
            [candidate],
            capture_output=True,
            text=True,
            timeout=3,
        )
        output = result.stdout + result.stderr
        m = re.search(r"Version\s+(\d+)\.(\d+)", output)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return None


def _manylinux_platform_tags(
    machine: str, glibc_major: int, glibc_minor: int
) -> set[str]:
    """Return all manylinux platform tags compatible with the given glibc version.

    Generates PEP 600 perennial tags (``manylinux_X_Y_{arch}`` for all Y the
    system satisfies) and the three legacy aliases where the architecture
    qualifies (manylinux1, manylinux2010, manylinux2014).

    :param machine: Value from ``platform.machine()``.
    :param glibc_major: Major version of the system glibc.
    :param glibc_minor: Minor version of the system glibc.
    :returns: Set of compatible manylinux platform tag strings.
    """
    tags: set[str] = set()
    if glibc_major != 2:
        # glibc 3 does not exist yet; nothing to generate.
        return tags
    # PEP 600: include manylinux_2_Y for every Y the system satisfies.
    # Oldest practical minimum is 2.5 (manylinux1).
    for mn in range(5, glibc_minor + 1):
        tags.add(f"manylinux_{glibc_major}_{mn}_{machine}")
    # Legacy aliases are only defined for specific architectures.
    if glibc_minor >= 5 and machine in _MANYLINUX1_ARCHS:
        tags.add(f"manylinux1_{machine}")
    if glibc_minor >= 12 and machine in _MANYLINUX2010_ARCHS:
        tags.add(f"manylinux2010_{machine}")
    if glibc_minor >= 17 and machine in _MANYLINUX2014_ARCHS:
        tags.add(f"manylinux2014_{machine}")
    return tags


def _compatible_tags() -> tuple[set[str], set[str], set[str]]:
    """
    Return (python_tags, abi_tags, platform_tags) for the running interpreter.

    Used to select compiled wheels on platforms where pip is unavailable
    (cx_Freeze Windows AIO, macOS .app bundles, Flatpak).
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
        # Linux: generate manylinux/musllinux tags when the libc version is
        # detectable; always include the bare linux_{arch} tag as a fallback.
        glibc = _glibc_version()
        if glibc is not None:
            plat_tags.update(_manylinux_platform_tags(machine, *glibc))
        musl = _musl_version()
        if musl is not None:
            musl_major, musl_minor = musl
            for mn in range(1, musl_minor + 1):
                plat_tags.add(f"musllinux_{musl_major}_{mn}_{machine}")
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


_FETCH_TIMEOUT = 30  # seconds; applied to both metadata and wheel downloads


def _fetch_url(url: str) -> bytes:
    """Download *url* and return the raw bytes.

    Raises ``urllib.error.URLError`` (or a subclass) on network error, and
    ``TimeoutError`` if the server does not respond within ``_FETCH_TIMEOUT``
    seconds.
    """
    ctx = _ssl_context()
    with urllib.request.urlopen(url, context=ctx, timeout=_FETCH_TIMEOUT) as resp:
        return resp.read()


@functools.cache
def _pypi_metadata(package: str) -> dict:
    """Return the PyPI JSON metadata dict for *package*.

    Results are cached per package name so that the gather pass and the
    install pass share the same response without a second network round-trip.
    """
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


# PEP 440 pre-release segment pattern: aN, bN, rcN directly after a digit;
# .devN, .alphaN, .betaN, .previewN with a separator prefix.
# Post-releases (.postN) are NOT pre-releases and must not be excluded.
_PRERELEASE_RE: re.Pattern[str] = re.compile(
    r"(?<=\d)(?:a|b|rc)\d+"  # aN / bN / rcN attached directly after a digit
    r"|[._-](?:dev|alpha|beta|preview)\d*",  # spelled-out forms with separator
    re.IGNORECASE,
)


def _is_prerelease(version: str) -> bool:
    """Return True if *version* is a PEP 440 pre-release or dev release.

    Recognises the suffixes ``aN``, ``bN``, ``rcN``, ``.devN``, ``.alphaN``,
    and ``.betaN``.  Post-releases (``.postN``) are *not* pre-releases.
    """
    return bool(_PRERELEASE_RE.search(version))


def _is_yanked(file_info: dict) -> bool:
    """Return True if the PyPI file entry is marked as yanked."""
    return bool(file_info.get("yanked", False))


def _requires_python_ok(file_info: dict) -> bool:
    """Return True if the wheel's ``requires_python`` is satisfied by the
    running interpreter, or if no ``requires_python`` field is present.

    Uses ``_satisfies_spec`` so the comparison is numeric, not lexicographic.
    """
    spec = file_info.get("requires_python") or ""
    if not spec:
        return True
    current = f"{sys.version_info.major}.{sys.version_info.minor}"
    return _satisfies_spec(current, spec)


def _pick_wheel(meta: dict, package: str, version: str | None = None) -> dict:
    """
    Return the file entry for the best wheel in *meta* for the current platform.

    When *version* is given only files listed under that release in
    ``meta["releases"]`` are searched.  Otherwise the preference order is:
    pure-Python wheel from the latest release, then a platform-compatible
    compiled wheel from the latest release, then the same two searches
    across older releases newest-first.

    Yanked files and files whose ``requires_python`` the running interpreter
    does not satisfy are skipped in all search paths.

    :param meta: PyPI JSON metadata dict for the package.
    :param package: Package name (used only in error messages).
    :param version: Exact version string to pin, or ``None`` for latest.
    :raises PyPIInstallError: if no compatible wheel is found.
    """
    if version is not None:
        candidates = [
            f
            for f in meta.get("releases", {}).get(version, [])
            if not _is_yanked(f) and _requires_python_ok(f)
        ]
        for file_info in candidates:
            if _is_pure_wheel(file_info):
                return file_info
        for file_info in candidates:
            if _is_compatible_wheel(file_info):
                return file_info
        raise PyPIInstallError(
            _("No compatible wheel found for '%s==%s' on this platform.")
            % (package, version)
        )
    # 1. Pure wheel in latest release.
    for file_info in meta.get("urls", []):
        if not _is_yanked(file_info) and _requires_python_ok(file_info):
            if _is_pure_wheel(file_info):
                return file_info
    # 2. Compiled wheel matching the current platform in latest release.
    for file_info in meta.get("urls", []):
        if not _is_yanked(file_info) and _requires_python_ok(file_info):
            if _is_compatible_wheel(file_info):
                return file_info
    # urls only covers the latest release; search all releases newest-first.
    sorted_releases = sorted(
        meta.get("releases", {}).items(),
        key=lambda item: _version_sort_key(item[0]),
        reverse=True,
    )
    for _ver, files in sorted_releases:
        candidates = [f for f in files if not _is_yanked(f) and _requires_python_ok(f)]
        # 3. Pure wheel in older release.
        for file_info in candidates:
            if _is_pure_wheel(file_info):
                return file_info
        # 4. Compiled wheel in older release.
        for file_info in candidates:
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


# -------------------------------------------------------------------------
#
# PEP 508 environment marker evaluation
#
# -------------------------------------------------------------------------


def _marker_env_vars() -> dict[str, str]:
    """Return the PEP 508 marker environment for the current interpreter."""
    return {
        "os_name": os.name,
        "sys_platform": sys.platform,
        "platform_machine": platform.machine(),
        "platform_python_implementation": platform.python_implementation(),
        "platform_release": platform.release(),
        "platform_system": platform.system(),
        "platform_version": platform.version(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "python_full_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        ),
        "implementation_name": sys.implementation.name,
        "implementation_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        ),
        "extra": "",
    }


def _tokenize_marker(s: str) -> list[str]:
    """
    Tokenize a PEP 508 marker string into a flat list of string tokens.

    Produces quoted string literals (with quotes retained), two-character
    operators (``>=``, ``<=``, ``==``, ``!=``, ``~=``), single-character
    operators (``<``, ``>``), the merged two-word operator ``"not in"``,
    parentheses, and identifier tokens (marker variable names and the
    keywords ``and``, ``or``, ``not``, ``in``).
    """
    tokens: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append(ch)
            i += 1
            continue
        if ch in ('"', "'"):
            j = i + 1
            while j < len(s) and s[j] != ch:
                j += 1
            tokens.append(s[i : j + 1])
            i = j + 1
            continue
        if i + 1 < len(s) and s[i : i + 2] in (">=", "<=", "==", "!=", "~="):
            tokens.append(s[i : i + 2])
            i += 2
            continue
        if ch in "<>":
            tokens.append(ch)
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < len(s) and (s[j].isalnum() or s[j] in "_-."):
                j += 1
            tokens.append(s[i:j])
            i = j
            continue
        i += 1
    # Merge a bare "not" immediately followed by "in" into the "not in" operator.
    out: list[str] = []
    k = 0
    while k < len(tokens):
        if tokens[k] == "not" and k + 1 < len(tokens) and tokens[k + 1] == "in":
            out.append("not in")
            k += 2
        else:
            out.append(tokens[k])
            k += 1
    return out


def _marker_cmp(lhs: str, op: str, rhs: str, use_version: bool) -> bool:
    """
    Compare *lhs* and *rhs* using *op* under PEP 508 marker semantics.

    When *use_version* is True the strings are parsed as dotted version
    numbers (via ``_version_sort_key``) and compared as tuples of ints;
    otherwise plain string comparison is used.
    """
    if use_version:
        lv: tuple[int, ...] = _version_sort_key(lhs)
        rv: tuple[int, ...] = _version_sort_key(rhs)
        if op == "==":
            return lv == rv
        if op == "!=":
            return lv != rv
        if op == ">=":
            return lv >= rv
        if op == "<=":
            return lv <= rv
        if op == ">":
            return lv > rv
        if op == "<":
            return lv < rv
        if op == "~=":
            if lv < rv:
                return False
            if len(rv) >= 2:
                upper = rv[:-1] + (rv[-2] + 1,)
                return lv < upper
            return True
        return False
    if op == "==":
        return lhs == rhs
    if op == "!=":
        return lhs != rhs
    if op == ">=":
        return lhs >= rhs
    if op == "<=":
        return lhs <= rhs
    if op == ">":
        return lhs > rhs
    if op == "<":
        return lhs < rhs
    if op == "in":
        return lhs in rhs
    if op == "not in":
        return lhs not in rhs
    return False


def _parse_marker_or(
    tokens: list[str], pos: int, env: dict[str, str]
) -> tuple[bool, int]:
    """Parse and evaluate an OR expression from *tokens* starting at *pos*."""
    left, pos = _parse_marker_and(tokens, pos, env)
    while pos < len(tokens) and tokens[pos] == "or":
        pos += 1
        right, pos = _parse_marker_and(tokens, pos, env)
        left = left or right
    return left, pos


def _parse_marker_and(
    tokens: list[str], pos: int, env: dict[str, str]
) -> tuple[bool, int]:
    """Parse and evaluate an AND expression from *tokens* starting at *pos*."""
    left, pos = _parse_marker_not(tokens, pos, env)
    while pos < len(tokens) and tokens[pos] == "and":
        pos += 1
        right, pos = _parse_marker_not(tokens, pos, env)
        left = left and right
    return left, pos


def _parse_marker_not(
    tokens: list[str], pos: int, env: dict[str, str]
) -> tuple[bool, int]:
    """Parse and evaluate a NOT expression or atom from *tokens* at *pos*."""
    if pos < len(tokens) and tokens[pos] == "not":
        pos += 1
        val, pos = _parse_marker_atom(tokens, pos, env)
        return not val, pos
    return _parse_marker_atom(tokens, pos, env)


def _parse_marker_atom(
    tokens: list[str], pos: int, env: dict[str, str]
) -> tuple[bool, int]:
    """
    Parse and evaluate an atomic marker expression starting at *pos*.

    An atom is either a parenthesised sub-expression or a comparison of
    the form ``marker_var OP marker_var``.
    """
    if pos < len(tokens) and tokens[pos] == "(":
        pos += 1
        val, pos = _parse_marker_or(tokens, pos, env)
        if pos < len(tokens) and tokens[pos] == ")":
            pos += 1
        return val, pos

    lhs_tok = tokens[pos]
    pos += 1
    op = tokens[pos]
    pos += 1
    rhs_tok = tokens[pos]
    pos += 1

    def resolve(tok: str) -> str:
        """Return the string value of a token — quoted literal or env variable."""
        if tok and tok[0] in ('"', "'"):
            return tok[1:-1]
        return env.get(tok, "")

    lhs_val = resolve(lhs_tok)
    rhs_val = resolve(rhs_tok)

    lhs_is_var = not (lhs_tok and lhs_tok[0] in ('"', "'"))
    rhs_is_var = not (rhs_tok and rhs_tok[0] in ('"', "'"))
    var_name = lhs_tok if lhs_is_var else (rhs_tok if rhs_is_var else "")
    use_version = var_name in _VERSION_VARS

    return _marker_cmp(lhs_val, op, rhs_val, use_version), pos


def _eval_marker(marker_str: str, extras: frozenset[str] = frozenset()) -> bool:
    """
    Evaluate a PEP 508 environment marker against the current environment.

    Returns True when the dep should be included.  *extras* is the set of
    extras being requested on the parent package; a marker of the form
    ``extra == "foo"`` is True only when ``"foo"`` is in *extras*.

    Returns True on any parse error so unrecognised markers never silently
    drop dependencies.
    """
    if not marker_str:
        return True
    env_base = _marker_env_vars()
    # Evaluate once per requested extra; include the dep if any eval is True.
    # When no extras are requested use a single iteration with extra="".
    eval_set: frozenset[str] = extras if extras else frozenset({"__none__"})
    for extra_val in eval_set:
        env = dict(env_base)
        env["extra"] = "" if extra_val == "__none__" else extra_val
        try:
            toks = _tokenize_marker(marker_str)
            result, pos = _parse_marker_or(toks, 0, env)
            if pos != len(toks):
                # Tokens left over — marker was not fully parsed.
                return True
            if result:
                return True
        except Exception:
            return True  # parse error → include dep to be safe
    return False


def _direct_dependencies(
    wheel_meta: dict[str, str],
    extras: frozenset[str] = frozenset(),
) -> list[tuple[str, str, frozenset[str]]]:
    """
    Return ``(name, version_spec, dep_extras)`` for each applicable dependency.

    Environment markers (``sys_platform``, ``python_version``, etc.) are
    evaluated against the current interpreter.  *extras* is the set of
    extras requested on the parent package; deps with ``extra == "foo"``
    markers are included only when ``"foo"`` is in *extras*.

    *dep_extras* carries any extras declared on the dependency itself
    (e.g. ``requests[security]>=2.0`` yields
    ``dep_extras=frozenset({"security"})``).  *version_spec* is the raw
    PEP 440 constraint string (e.g. ``">=2.0,<3"``), or an empty string
    when no constraint is declared.
    """
    raw = wheel_meta.get("requires-dist", "")
    deps: list[tuple[str, str, frozenset[str]]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _REQ_RE.match(line)
        if not m:
            continue
        name = m.group("name")
        extras_str = m.group("extras") or ""
        spec = (m.group("spec") or "").strip()
        marker = (m.group("marker") or "").strip()
        dep_extras = frozenset(e.strip() for e in extras_str.split(",") if e.strip())
        if marker and not _eval_marker(marker, extras):
            continue
        if name:
            deps.append((name, spec, dep_extras))
    return deps


def _gather_requirements(
    package: str,
    extras: frozenset[str],
    specs: dict[str, list[str]],
    seen: set[str],
) -> None:
    """
    Recursively collect version constraints for *package* and its transitive deps.

    Reads ``meta["info"]["requires_dist"]`` from the PyPI JSON API without
    downloading any wheel.  *specs* is mutated in-place: for each dependency
    that carries a version constraint, its canonical name is mapped to the
    accumulated list of constraint strings from all paths through the dep graph.

    Packages without any version constraint are not added to *specs*; the
    install pass will use the latest compatible wheel for those.

    :param package: Top-level package name to start from.
    :param extras: Extras active on *package*; gates ``extra == "..."`` markers.
    :param specs: Accumulated ``{canonical_name: [spec, ...]}`` mapping.
    :param seen: Canonical names already visited (prevents infinite loops).
    """
    canonical = package.lower().replace("-", "_")
    if canonical in seen:
        return
    seen.add(canonical)
    # If already importable, skip: the install pass will also skip it, so its
    # transitive constraints do not affect the resolution outcome.
    try:
        importlib.import_module(canonical)
        return
    except ImportError:
        pass
    try:
        meta = _pypi_metadata(package)
    except PyPIInstallError:
        return  # unreachable now; the install pass will surface the error
    for req_str in meta.get("info", {}).get("requires_dist") or []:
        m = _REQ_RE.match(req_str)
        if not m:
            continue
        name = m.group("name")
        if not name:
            continue
        spec = (m.group("spec") or "").strip()
        marker = (m.group("marker") or "").strip()
        dep_extras = frozenset(
            e.strip() for e in (m.group("extras") or "").split(",") if e.strip()
        )
        if marker and not _eval_marker(marker, extras):
            continue
        dep_canonical = name.lower().replace("-", "_")
        if spec:
            specs.setdefault(dep_canonical, []).append(spec)
        _gather_requirements(name, dep_extras, specs, seen)


def _find_satisfying_version(package: str, combined_spec: str) -> str | None:
    """
    Return the newest stable, non-yanked version of *package* satisfying
    *combined_spec*.

    Scans the ``releases`` dict in the PyPI JSON metadata newest-first,
    skipping pre-release versions (``aN``, ``bN``, ``rcN``, ``.devN``) and
    fully-yanked releases (all files for the version are yanked).  Returns
    ``None`` when no version satisfies the constraint or when PyPI is
    unreachable.

    :param package: PyPI package name to look up.
    :param combined_spec: Comma-joined PEP 440 constraints, e.g.
        ``">=1.0,<2.0"``.  An empty string matches any version.
    :returns: The newest satisfying version string, or ``None``.
    """
    try:
        meta = _pypi_metadata(package)
    except PyPIInstallError:
        return None
    releases = meta.get("releases", {})
    for ver in sorted(releases, key=_version_sort_key, reverse=True):
        if _is_prerelease(ver):
            continue
        files = releases[ver]
        if files and all(_is_yanked(f) for f in files):
            continue
        if _satisfies_spec(ver, combined_spec):
            return ver
    return None


def _satisfies_spec(installed_ver: str, spec: str) -> bool:
    """Return True if *installed_ver* satisfies every constraint in *spec*.

    Parses comma-separated PEP 440 operators (``>=``, ``<=``, ``==``,
    ``!=``, ``~=``, ``>``, ``<``).  Wildcard ``==X.Y.*`` / ``!=X.Y.*``
    forms are supported.  Version comparison uses ``_version_sort_key``;
    pre-release suffixes sort as zero, which is not fully PEP 440 compliant
    but sufficient for Gramps addon dependencies.
    """
    installed = _version_sort_key(installed_ver)
    for raw in re.split(r",\s*", spec.strip()):
        raw = raw.strip()
        if not raw:
            continue
        m = re.match(r"^(~=|>=|<=|!=|==|>|<)\s*(.+)$", raw)
        if not m:
            continue
        op, req_str = m.group(1), m.group(2).strip()
        required = _version_sort_key(req_str.rstrip(".*"))
        if op == ">=":
            if installed < required:
                return False
        elif op == "<=":
            if installed > required:
                return False
        elif op == ">":
            if installed <= required:
                return False
        elif op == "<":
            if installed >= required:
                return False
        elif op == "==":
            if req_str.endswith(".*"):
                n = len(required)
                if installed[:n] != required:
                    return False
            elif installed != required:
                return False
        elif op == "!=":
            if req_str.endswith(".*"):
                n = len(required)
                if installed[:n] == required:
                    return False
            elif installed == required:
                return False
        elif op == "~=":
            # ~=X.Y  means  >=X.Y and <(X+1)
            # ~=X.Y.Z means  >=X.Y.Z and <X.(Y+1)
            if installed < required:
                return False
            parts = list(required)
            if len(parts) >= 2:
                upper = tuple(parts[:-2] + [parts[-2] + 1])
                if installed >= upper:
                    return False
    return True


def _version_satisfies(canonical: str, spec: str) -> bool:
    """Return True if the installed version of *canonical* satisfies *spec*.

    Uses ``importlib.metadata`` to look up the installed distribution version.
    Tries both the canonical name (underscores) and the hyphenated form.
    Returns True when no dist-info is found (package importable but
    unregistered, e.g. a sys.path source install) to avoid spurious
    reinstalls.
    """
    if not spec:
        return True
    for name in (canonical, canonical.replace("_", "-")):
        try:
            installed_ver = importlib.metadata.version(name)
            return _satisfies_spec(installed_ver, spec)
        except importlib.metadata.PackageNotFoundError:
            continue
    # No dist-info — assume the constraint is satisfied.
    return True


# -------------------------------------------------------------------------
#
# Name resolution
#
# -------------------------------------------------------------------------
def resolve_pypi_name(import_name: str) -> str:
    """Return the PyPI distribution name for *import_name*.

    Addon ``requires_mod`` entries use Python import names (e.g. ``"PIL"``),
    but ``install_package()`` and pip need the PyPI distribution name (e.g.
    ``"Pillow"``).  This function translates known mismatches via
    ``_IMPORT_TO_PYPI``; names not in the table are returned unchanged.

    :param import_name: The Python import name as declared in ``requires_mod``.
    :returns: The corresponding PyPI distribution name.
    """
    pypi_name = _IMPORT_TO_PYPI.get(import_name, import_name)
    if pypi_name != import_name:
        LOG.warning(
            "requires_mod value %r is a Python import name, not a PyPI package "
            "name.  Please update the addon to use %r instead.  "
            "The correct name has been applied automatically this time.",
            import_name,
            pypi_name,
        )
    return pypi_name


# -------------------------------------------------------------------------
#
# Environment probes
#
# -------------------------------------------------------------------------
@functools.cache
def _pip_available() -> bool:
    """Return True if sys.executable can invoke pip as a module.

    Runs ``sys.executable -m pip --version`` once and caches the result.
    Returns False on Flatpak, stripped Docker images, and any environment
    where pip has been removed from the Python installation.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


# -------------------------------------------------------------------------
#
# Public API
#
# -------------------------------------------------------------------------
def install_package(
    package: str, target: str, extras: frozenset[str] = frozenset()
) -> list[str]:
    """
    Download and install *package* from PyPI into *target*.

    Performs a three-pass install:

    1. **Gather**: traverse the full dependency graph using PyPI JSON metadata
       to collect all version constraints without downloading any wheels.
    2. **Resolve**: for each constrained package, find the newest version that
       satisfies all accumulated constraints simultaneously.  Raises
       ``PyPIInstallError`` if no such version exists.
    3. **Install**: download and extract wheels in dependency order, using the
       resolved versions from pass 2.

    Extras embedded in *package* (e.g. ``"requests[security]"``) are parsed
    and merged with *extras*.  Returns a list of package names that were
    installed.

    :param package: PyPI package name, optionally with extras, e.g.
        ``"requests[security]"``.
    :param target: Filesystem path to install into (e.g. ``LIB_PATH``).
    :param extras: Set of extras to activate on *package*.
    :returns: List of package names that were installed.
    :raises PyPIInstallError: if the package or a dependency cannot be
        installed, or if no version satisfies the combined constraints.
    """
    # Parse extras embedded in the package name, e.g. "requests[security,crypto]".
    em = re.match(r"^([^\[]+)\[([^\]]+)\]$", package.strip())
    if em:
        package = em.group(1).strip()
        parsed = frozenset(e.strip() for e in em.group(2).split(",") if e.strip())
        extras = extras | parsed

    # Pass 1: gather all transitive version constraints from PyPI JSON metadata.
    specs: dict[str, list[str]] = {}
    _gather_requirements(package, extras, specs, set())

    # Pass 2: resolve a satisfying version for each constrained package.
    resolved: dict[str, str] = {}
    for pkg_canonical, spec_list in specs.items():
        combined = ",".join(spec_list)
        version = _find_satisfying_version(pkg_canonical, combined)
        if version is None:
            raise PyPIInstallError(
                _("No version of '%s' satisfies all constraints: %s")
                % (pkg_canonical, combined)
            )
        resolved[pkg_canonical] = version

    # Pass 3: install with pinned versions from the resolver.
    installed: list[str] = []
    _install_one(package, target, installed, set(), extras=extras, resolved=resolved)
    return installed


def _install_one(
    package: str,
    target: str,
    installed: list[str],
    seen: set[str],
    version_spec: str = "",
    extras: frozenset[str] = frozenset(),
    resolved: dict[str, str] | None = None,
) -> None:
    """
    Recursively install *package* and its applicable dependencies.

    *seen* prevents infinite loops in the case of circular deps.
    *version_spec* is a PEP 440 constraint string (e.g. ``">=2.0,<3"``)
    used to decide whether an already-importable package satisfies the
    requirement; an empty string means any version is accepted.
    *extras* is the set of extras requested on *package*; deps with
    matching ``extra ==`` markers are included.
    *resolved* maps canonical package names to the pre-resolved version
    string from the gather/resolve passes; when ``None`` the latest
    compatible wheel is selected.
    """
    canonical = package.lower().replace("-", "_")
    if canonical in seen:
        return
    seen.add(canonical)

    resolved_ver: str | None = resolved.get(canonical) if resolved is not None else None

    # Skip if already importable and the installed version satisfies the spec.
    try:
        importlib.import_module(canonical)
        if _version_satisfies(canonical, version_spec):
            LOG.debug(
                "'%s' is already importable and satisfies %r, skipping.",
                canonical,
                version_spec or "any",
            )
            return
        LOG.info(
            "'%s' importable but does not satisfy %r; reinstalling.",
            canonical,
            version_spec,
        )
    except ImportError:
        pass

    LOG.info("Installing '%s' from PyPI into %s", package, target)
    meta = _pypi_metadata(package)
    file_info = _pick_wheel(meta, package, version=resolved_ver)

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

    # Install applicable direct dependencies (platform-conditional and extras-aware)
    for dep_name, dep_spec, dep_extras in _direct_dependencies(wheel_meta, extras):
        _install_one(dep_name, target, installed, seen, dep_spec, dep_extras, resolved)
