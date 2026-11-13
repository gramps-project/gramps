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
End-to-end tests for gramps.gen.utils.pypi that hit the real PyPI network.

These tests are skipped automatically when pypi.org is not reachable, so
they are safe to run in CI but will be no-ops in offline environments.

Run explicitly with:
    python3 -m unittest gramps.gen.utils.test.pypi_e2e_test -v
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import hashlib
import importlib
import importlib.metadata
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import unittest
import zipfile

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..pypi import (
    PyPIInstallError,
    _fetch_url,
    _find_satisfying_version,
    _is_pure_wheel,
    _pick_wheel,
    _pypi_metadata,
    _version_sort_key,
    install_package,
)


def _network_available() -> bool:
    """Return True if pypi.org is reachable on port 443."""
    try:
        socket.create_connection(("pypi.org", 443), timeout=5)
        return True
    except OSError:
        return False


NETWORK_AVAILABLE = _network_available()
_skip_offline = unittest.skipUnless(
    NETWORK_AVAILABLE, "requires network access to pypi.org"
)

# A small, stable, pure-Python package with no runtime dependencies.
# iniconfig is used by pytest and changes very rarely.
_NODEP_PACKAGE = "iniconfig"

# A small pure-Python package that is unlikely to be pre-installed in
# the test environment, used to exercise the actual download path.
_DOWNLOAD_PACKAGE = "tomli"


def _force_extract(package: str, version: str, target: str) -> None:
    """Download and extract a specific *version* of *package* into *target*.

    Bypasses install_package()'s importability guard entirely by calling the
    download/extract steps directly, so upgrade-test fixtures can be seeded
    regardless of whether *package* happens to already be installed
    elsewhere in the environment (e.g. as a build-tool dependency in CI).
    """
    meta = _pypi_metadata(package)
    file_info = _pick_wheel(meta, package, version=version)
    data = _fetch_url(file_info["url"])
    with zipfile.ZipFile(io.BytesIO(data)) as whl:
        whl.extractall(target)


# -------------------------------------------------------------------------
#
# TestSSLAndMetadata
#
# -------------------------------------------------------------------------
class TestSSLAndMetadata(unittest.TestCase):
    """Verify that SSL and PyPI metadata fetching work without certifi."""

    @_skip_offline
    def test_ssl_reaches_pypi(self):
        """ssl.create_default_context() fetches data from pypi.org successfully."""
        data = _fetch_url(f"https://pypi.org/pypi/{_NODEP_PACKAGE}/json")
        self.assertGreater(len(data), 100)

    @_skip_offline
    def test_ssl_response_is_valid_json(self):
        """The PyPI metadata endpoint returns parseable JSON."""
        data = _fetch_url(f"https://pypi.org/pypi/{_NODEP_PACKAGE}/json")
        meta = json.loads(data)
        self.assertIn("info", meta)
        self.assertIn("urls", meta)

    @_skip_offline
    def test_pypi_metadata_returns_package_info(self):
        """_pypi_metadata() returns the expected package name."""
        meta = _pypi_metadata(_NODEP_PACKAGE)
        self.assertEqual(meta["info"]["name"].lower(), _NODEP_PACKAGE)

    @_skip_offline
    def test_pypi_metadata_unknown_package_raises(self):
        """_pypi_metadata() raises PyPIInstallError for a non-existent package."""
        with self.assertRaises(PyPIInstallError):
            _pypi_metadata("this-package-does-not-exist-xyzzy-42")


# -------------------------------------------------------------------------
#
# TestPickWheelE2E
#
# -------------------------------------------------------------------------
class TestPickWheelE2E(unittest.TestCase):
    """Verify wheel selection against real PyPI metadata."""

    @_skip_offline
    def test_iniconfig_has_pure_wheel(self):
        """iniconfig has a py3-none-any wheel on PyPI."""
        meta = _pypi_metadata(_NODEP_PACKAGE)
        wheel = _pick_wheel(meta, _NODEP_PACKAGE)
        self.assertIn("py3-none-any", wheel["filename"])

    @_skip_offline
    def test_picked_wheel_has_sha256(self):
        """The selected wheel entry carries a SHA-256 digest."""
        meta = _pypi_metadata(_NODEP_PACKAGE)
        wheel = _pick_wheel(meta, _NODEP_PACKAGE)
        sha256 = wheel.get("digests", {}).get("sha256", "")
        self.assertEqual(len(sha256), 64)

    @_skip_offline
    def test_numpy_has_no_pure_wheel(self):
        """numpy only ships compiled wheels; no pure-Python wheel exists on PyPI.

        We verify the absence of pure wheels directly from the metadata rather
        than calling _pick_wheel, because on a compatible platform (e.g. Linux
        x86_64 with glibc) _pick_wheel would successfully return a compiled
        wheel instead of raising.
        """
        meta = _pypi_metadata("numpy")
        all_files: list[dict] = list(meta.get("urls", []))
        for files in meta.get("releases", {}).values():
            all_files.extend(files)
        pure_wheels = [f for f in all_files if _is_pure_wheel(f)]
        self.assertEqual(pure_wheels, [], "Expected no pure-Python wheels for numpy")


# -------------------------------------------------------------------------
#
# TestDownloadExtractE2E
#
# -------------------------------------------------------------------------
class TestDownloadExtractE2E(unittest.TestCase):
    """
    End-to-end tests of the download → verify → extract pipeline.

    These tests call the internal helpers directly, bypassing
    install_package()'s importability guard.  That guard is correct
    behaviour (skip packages already on sys.path) but irrelevant here:
    we want to verify the network and extraction code work regardless
    of what is already installed in the environment.

    The wheel is fetched once in setUpClass and reused across tests to
    avoid redundant network round-trips.
    """

    _wheel_data: bytes = b""
    _wheel_info: dict = {}

    @classmethod
    def setUpClass(cls):
        """Download the test wheel once for all tests in this class."""
        if not NETWORK_AVAILABLE:
            return
        meta = _pypi_metadata(_DOWNLOAD_PACKAGE)
        cls._wheel_info = _pick_wheel(meta, _DOWNLOAD_PACKAGE)
        cls._wheel_data = _fetch_url(cls._wheel_info["url"])

    def setUp(self):
        self.target = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.target, ignore_errors=True)
        for mod in list(sys.modules):
            if mod == _DOWNLOAD_PACKAGE or mod.startswith(_DOWNLOAD_PACKAGE + "."):
                del sys.modules[mod]
        if self.target in sys.path:
            sys.path.remove(self.target)

    def _extract(self):
        """Extract the pre-downloaded wheel into self.target."""
        with zipfile.ZipFile(io.BytesIO(self._wheel_data)) as whl:
            whl.extractall(self.target)

    @_skip_offline
    def test_sha256_matches_pypi_digest(self):
        """The downloaded wheel's SHA-256 matches the digest published on PyPI."""
        expected = self._wheel_info["digests"]["sha256"]
        actual = hashlib.sha256(self._wheel_data).hexdigest()
        self.assertEqual(actual, expected)

    @_skip_offline
    def test_wheel_extracts_package_files(self):
        """Extracted wheel contains the package directory in target."""
        self._extract()
        entries = os.listdir(self.target)
        self.assertTrue(
            any(_DOWNLOAD_PACKAGE in e for e in entries),
            f"Expected '{_DOWNLOAD_PACKAGE}' among {entries}",
        )

    @_skip_offline
    def test_wheel_extracts_dist_info(self):
        """Extracted wheel contains a .dist-info directory in target."""
        self._extract()
        dist_infos = [e for e in os.listdir(self.target) if ".dist-info" in e]
        self.assertTrue(
            dist_infos,
            f"No .dist-info directory found among: {os.listdir(self.target)}",
        )

    @_skip_offline
    def test_extracted_package_is_importable(self):
        """Package extracted to target is importable once target is on sys.path."""
        self._extract()
        sys.path.insert(0, self.target)
        # Force import from target even if the package is already on sys.path
        sys.modules.pop(_DOWNLOAD_PACKAGE, None)
        mod = importlib.import_module(_DOWNLOAD_PACKAGE)
        self.assertIsNotNone(mod)


# -------------------------------------------------------------------------
#
# TestInstallPackageBehaviourE2E
#
# -------------------------------------------------------------------------
class TestInstallPackageBehaviourE2E(unittest.TestCase):
    """Tests of install_package() orchestration behaviour against real PyPI."""

    def setUp(self):
        self.target = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.target, ignore_errors=True)
        if self.target in sys.path:
            sys.path.remove(self.target)

    @_skip_offline
    def test_already_importable_skipped(self):
        """install_package() skips a package that is already importable."""
        # "os" is always importable; nothing should be downloaded or extracted.
        installed = install_package("os", self.target)
        self.assertEqual(installed, [])
        self.assertEqual(os.listdir(self.target), [])


# -------------------------------------------------------------------------
#
# TestUpgradeE2E
#
# -------------------------------------------------------------------------
class TestUpgradeE2E(unittest.TestCase):
    """Tests of install_package(upgrade=True) against real PyPI."""

    def setUp(self):
        self.target = tempfile.mkdtemp()
        self.canonical = _DOWNLOAD_PACKAGE.lower().replace("-", "_")
        sys.path.insert(0, self.target)

    def tearDown(self):
        if self.target in sys.path:
            sys.path.remove(self.target)
        shutil.rmtree(self.target, ignore_errors=True)
        # Drop the module we forced into sys.modules so later tests (in this
        # file or others sharing the process) resolve it fresh.
        sys.modules.pop(self.canonical, None)
        importlib.invalidate_caches()

    @_skip_offline
    def test_upgrade_replaces_outdated_version(self):
        """upgrade=True replaces an outdated mini-installed version."""
        if self.canonical in sys.modules:
            self.skipTest(f"{self.canonical!r} already imported in this process")

        meta = _pypi_metadata(_DOWNLOAD_PACKAGE)
        stable_versions = sorted(
            (
                ver
                for ver, files in meta.get("releases", {}).items()
                if files
                and not all(f.get("yanked") for f in files)
                and any(f.get("filename", "").endswith(".whl") for f in files)
            ),
            key=_version_sort_key,
        )
        self.assertGreaterEqual(
            len(stable_versions), 2, "test package needs 2+ releases"
        )
        old_version = stable_versions[0]

        # Seed target with the oldest release, bypassing install_package()'s
        # importability guard so this works regardless of whether the real
        # package is already installed elsewhere in the environment (e.g. as
        # a build-tool dependency in CI).  self.target sits at sys.path[0],
        # so this fixture shadows any such copy for the rest of the test.
        _force_extract(_DOWNLOAD_PACKAGE, old_version, self.target)
        importlib.invalidate_caches()
        self.assertEqual(importlib.metadata.version(self.canonical), old_version)

        # Upgrading should replace it with a newer release.
        installed = install_package(_DOWNLOAD_PACKAGE, self.target, upgrade=True)
        importlib.invalidate_caches()
        self.assertEqual(installed, [_DOWNLOAD_PACKAGE])
        new_version = importlib.metadata.version(self.canonical)
        self.assertGreater(
            _version_sort_key(new_version), _version_sort_key(old_version)
        )

        # The old dist-info must be gone, not merely shadowed.
        dist_info_dirs = [
            d for d in os.listdir(self.target) if d.endswith(".dist-info")
        ]
        self.assertTrue(all(old_version not in d for d in dist_info_dirs))

    @_skip_offline
    def test_upgrade_is_noop_when_already_latest(self):
        """upgrade=True does not reinstall a package already at the newest version."""
        if self.canonical in sys.modules:
            self.skipTest(f"{self.canonical!r} already imported in this process")

        latest = _find_satisfying_version(_DOWNLOAD_PACKAGE, "")
        self.assertIsNotNone(latest, "could not determine latest version from PyPI")

        # Seed target directly at the newest release (see comment above on
        # why this bypasses install_package() rather than calling it).
        _force_extract(_DOWNLOAD_PACKAGE, latest, self.target)
        importlib.invalidate_caches()
        self.assertEqual(importlib.metadata.version(self.canonical), latest)

        installed_again = install_package(_DOWNLOAD_PACKAGE, self.target, upgrade=True)
        self.assertEqual(installed_again, [])


if __name__ == "__main__":
    unittest.main()
