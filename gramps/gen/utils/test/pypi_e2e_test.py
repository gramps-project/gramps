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
    _pick_wheel,
    _pypi_metadata,
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
        """numpy only ships compiled wheels; _pick_wheel raises PyPIInstallError."""
        meta = _pypi_metadata("numpy")
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "numpy")


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


if __name__ == "__main__":
    unittest.main()
