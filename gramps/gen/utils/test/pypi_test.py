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

"""Tests for gramps.gen.utils.pypi."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import hashlib
import io
import os
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import MagicMock, patch

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..pypi import (
    PyPIInstallError,
    _direct_dependencies,
    _is_pure_wheel,
    _pick_wheel,
    _verify_sha256,
    _wheel_metadata,
    install_package,
)


# -------------------------------------------------------------------------
#
# Helpers
#
# -------------------------------------------------------------------------
def _make_wheel_zip(metadata_text: str = "", extra_files: dict | None = None) -> bytes:
    """
    Build a minimal in-memory wheel zip with the given METADATA content.

    :param metadata_text: Content for the ``pkg-1.0.dist-info/METADATA`` entry.
    :param extra_files: Additional ``{name: bytes}`` entries to add.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pkg-1.0.dist-info/METADATA", metadata_text)
        for name, data in (extra_files or {}).items():
            zf.writestr(name, data)
    return buf.getvalue()


def _sha256(data: bytes) -> str:
    """Return the hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def _fake_pypi_meta(
    filename: str, url: str = "https://example.com/pkg.whl", sha256: str = ""
) -> dict:
    """Build a minimal PyPI JSON metadata dict with a single file entry."""
    return {
        "urls": [
            {
                "filename": filename,
                "url": url,
                "packagetype": "bdist_wheel",
                "digests": {"sha256": sha256},
            }
        ],
        "releases": {},
    }


# -------------------------------------------------------------------------
#
# TestIsPureWheel
#
# -------------------------------------------------------------------------
class TestIsPureWheel(unittest.TestCase):
    def test_py3_none_any_is_pure(self):
        """py3-none-any wheels are pure Python."""
        info = {"filename": "mypkg-1.0-py3-none-any.whl"}
        self.assertTrue(_is_pure_wheel(info))

    def test_py2_py3_none_any_is_pure(self):
        """py2.py3-none-any wheels are pure Python."""
        info = {"filename": "mypkg-1.0-py2.py3-none-any.whl"}
        self.assertTrue(_is_pure_wheel(info))

    def test_platform_wheel_is_not_pure(self):
        """Platform-specific wheels are not pure Python."""
        info = {"filename": "mypkg-1.0-cp311-cp311-linux_x86_64.whl"}
        self.assertFalse(_is_pure_wheel(info))

    def test_abi3_wheel_is_not_pure(self):
        """abi3 wheels are compiled and not pure Python."""
        info = {"filename": "mypkg-1.0-cp38-abi3-manylinux1_x86_64.whl"}
        self.assertFalse(_is_pure_wheel(info))

    def test_tarball_is_not_pure(self):
        """Source tarballs are not wheels."""
        info = {"filename": "mypkg-1.0.tar.gz"}
        self.assertFalse(_is_pure_wheel(info))

    def test_too_few_parts_is_not_pure(self):
        """Wheel filenames with fewer than 5 dash-separated parts are rejected."""
        info = {"filename": "mypkg-1.0-py3.whl"}
        self.assertFalse(_is_pure_wheel(info))

    def test_empty_filename_is_not_pure(self):
        """An empty filename is not a pure wheel."""
        self.assertFalse(_is_pure_wheel({"filename": ""}))


# -------------------------------------------------------------------------
#
# TestVerifySha256
#
# -------------------------------------------------------------------------
class TestVerifySha256(unittest.TestCase):
    def test_correct_hash_passes(self):
        """A correct SHA-256 digest does not raise."""
        data = b"hello world"
        _verify_sha256(data, _sha256(data), "test.whl")

    def test_wrong_hash_raises(self):
        """A mismatched SHA-256 digest raises PyPIInstallError."""
        with self.assertRaises(PyPIInstallError):
            _verify_sha256(b"hello world", "deadbeef" * 8, "test.whl")

    def test_empty_data(self):
        """SHA-256 of empty bytes is verified correctly."""
        data = b""
        _verify_sha256(data, _sha256(data), "empty.whl")


# -------------------------------------------------------------------------
#
# TestWheelMetadata
#
# -------------------------------------------------------------------------
class TestWheelMetadata(unittest.TestCase):
    def _open(self, data: bytes) -> zipfile.ZipFile:
        return zipfile.ZipFile(io.BytesIO(data))

    def test_parses_name_and_version(self):
        """Standard Name and Version headers are parsed."""
        meta_text = "Name: mypkg\nVersion: 1.2.3\n"
        with self._open(_make_wheel_zip(meta_text)) as whl:
            meta = _wheel_metadata(whl)
        self.assertEqual(meta.get("name"), "mypkg")
        self.assertEqual(meta.get("version"), "1.2.3")

    def test_parses_requires_dist(self):
        """Multiple Requires-Dist headers are joined with newlines."""
        meta_text = "Name: mypkg\nRequires-Dist: requests\nRequires-Dist: click\n"
        with self._open(_make_wheel_zip(meta_text)) as whl:
            meta = _wheel_metadata(whl)
        deps = meta.get("requires-dist", "")
        self.assertIn("requests", deps)
        self.assertIn("click", deps)

    def test_missing_metadata_returns_empty(self):
        """A wheel with no METADATA file returns an empty dict."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("pkg-1.0.dist-info/WHEEL", "Wheel-Version: 1.0\n")
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as whl:
            meta = _wheel_metadata(whl)
        self.assertEqual(meta, {})


# -------------------------------------------------------------------------
#
# TestDirectDependencies
#
# -------------------------------------------------------------------------
class TestDirectDependencies(unittest.TestCase):
    def test_simple_dependency(self):
        """A bare package name is returned as-is."""
        meta = {"requires-dist": "requests"}
        self.assertEqual(_direct_dependencies(meta), ["requests"])

    def test_version_constraint_stripped(self):
        """Version specifiers are stripped from dependency names."""
        meta = {"requires-dist": "requests>=2.0"}
        self.assertEqual(_direct_dependencies(meta), ["requests"])

    def test_conditional_dependency_skipped(self):
        """Entries with environment markers (semicolons) are skipped."""
        meta = {"requires-dist": 'pywin32>=1.0; sys_platform == "win32"'}
        self.assertEqual(_direct_dependencies(meta), [])

    def test_extra_dependency_skipped(self):
        """Extra-conditional dependencies are skipped."""
        meta = {"requires-dist": 'cryptography; extra == "security"'}
        self.assertEqual(_direct_dependencies(meta), [])

    def test_multiple_dependencies(self):
        """Multiple deps on separate lines are all returned."""
        meta = {"requires-dist": "requests\nclick\nrich"}
        self.assertEqual(_direct_dependencies(meta), ["requests", "click", "rich"])

    def test_mixed_conditional_and_plain(self):
        """Only unconditional entries are returned from a mixed list."""
        meta = {
            "requires-dist": (
                "requests\n" 'pywin32; sys_platform == "win32"\n' "click\n"
            )
        }
        self.assertEqual(_direct_dependencies(meta), ["requests", "click"])

    def test_empty_metadata(self):
        """Missing requires-dist key returns an empty list."""
        self.assertEqual(_direct_dependencies({}), [])

    def test_blank_lines_ignored(self):
        """Blank lines in the requires-dist value are ignored."""
        meta = {"requires-dist": "\nrequests\n\nclick\n"}
        self.assertEqual(_direct_dependencies(meta), ["requests", "click"])


# -------------------------------------------------------------------------
#
# TestPickWheel
#
# -------------------------------------------------------------------------
class TestPickWheel(unittest.TestCase):
    def test_picks_pure_wheel_from_urls(self):
        """A pure-Python wheel in urls is returned."""
        meta = _fake_pypi_meta("mypkg-1.0-py3-none-any.whl")
        result = _pick_wheel(meta, "mypkg")
        self.assertEqual(result["filename"], "mypkg-1.0-py3-none-any.whl")

    def test_skips_compiled_wheel(self):
        """A compiled wheel in urls is not picked; raises if no pure wheel."""
        meta = _fake_pypi_meta("mypkg-1.0-cp311-cp311-linux_x86_64.whl")
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "mypkg")

    def test_falls_back_to_releases(self):
        """Falls back to releases dict when urls has no pure wheel."""
        meta = {
            "urls": [],
            "releases": {
                "0.9": [
                    {
                        "filename": "mypkg-0.9-py3-none-any.whl",
                        "url": "u",
                        "digests": {},
                    }
                ]
            },
        }
        result = _pick_wheel(meta, "mypkg")
        self.assertEqual(result["filename"], "mypkg-0.9-py3-none-any.whl")

    def test_no_wheel_at_all_raises(self):
        """No pure wheel anywhere raises PyPIInstallError."""
        meta = {"urls": [], "releases": {}}
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "mypkg")


# -------------------------------------------------------------------------
#
# TestInstallPackage
#
# -------------------------------------------------------------------------
class TestInstallPackage(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.target, ignore_errors=True)
        # Remove any test module from sys.modules to avoid cross-test pollution
        sys.modules.pop("fakepkg", None)
        sys.modules.pop("fakepkg_dep", None)

    def _make_wheel_bytes(self, metadata_text: str = "") -> bytes:
        return _make_wheel_zip(metadata_text, {"fakepkg/__init__.py": b""})

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_installs_pure_package(self, mock_meta, mock_fetch):
        """A pure-Python package with no deps is extracted to target."""
        wheel_data = self._make_wheel_bytes("Name: fakepkg\nVersion: 1.0\n")
        digest = _sha256(wheel_data)

        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-py3-none-any.whl",
            "https://example.com/fakepkg.whl",
            digest,
        )
        mock_fetch.return_value = wheel_data

        installed = install_package("fakepkg", self.target)

        self.assertIn("fakepkg", installed)
        self.assertTrue(
            os.path.exists(os.path.join(self.target, "fakepkg", "__init__.py"))
        )

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_skips_already_importable(self, mock_meta, mock_fetch):
        """Packages already importable are skipped without a network call."""
        installed = install_package("os", self.target)
        mock_meta.assert_not_called()
        mock_fetch.assert_not_called()
        self.assertEqual(installed, [])

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_sha256_mismatch_raises(self, mock_meta, mock_fetch):
        """A SHA-256 mismatch raises PyPIInstallError."""
        wheel_data = self._make_wheel_bytes()
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-py3-none-any.whl",
            "https://example.com/fakepkg.whl",
            "deadbeef" * 8,
        )
        mock_fetch.return_value = wheel_data

        with self.assertRaises(PyPIInstallError):
            install_package("fakepkg", self.target)

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_no_pure_wheel_raises(self, mock_meta, mock_fetch):
        """A package with only compiled wheels raises PyPIInstallError."""
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-cp311-cp311-linux_x86_64.whl"
        )
        with self.assertRaises(PyPIInstallError):
            install_package("fakepkg", self.target)
        mock_fetch.assert_not_called()

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_network_error_raises(self, mock_meta, mock_fetch):
        """A network error on metadata fetch raises PyPIInstallError."""
        mock_meta.side_effect = PyPIInstallError("network down")
        with self.assertRaises(PyPIInstallError):
            install_package("fakepkg", self.target)

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_installs_direct_dependency(self, mock_meta, mock_fetch):
        """A package's unconditional direct dependency is also installed."""
        dep_wheel = _make_wheel_zip(
            "Name: fakepkg_dep\nVersion: 1.0\n",
            {"fakepkg_dep/__init__.py": b""},
        )
        dep_digest = _sha256(dep_wheel)

        main_wheel = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\nRequires-Dist: fakepkg_dep\n",
            {"fakepkg/__init__.py": b""},
        )
        main_digest = _sha256(main_wheel)

        def fake_meta(package):
            if package == "fakepkg":
                return _fake_pypi_meta(
                    "fakepkg-1.0-py3-none-any.whl",
                    "https://example.com/fakepkg.whl",
                    main_digest,
                )
            if package == "fakepkg_dep":
                return _fake_pypi_meta(
                    "fakepkg_dep-1.0-py3-none-any.whl",
                    "https://example.com/fakepkg_dep.whl",
                    dep_digest,
                )
            raise PyPIInstallError(f"unexpected: {package}")

        def fake_fetch(url):
            if "fakepkg_dep" in url:
                return dep_wheel
            return main_wheel

        mock_meta.side_effect = fake_meta
        mock_fetch.side_effect = fake_fetch

        installed = install_package("fakepkg", self.target)

        self.assertIn("fakepkg", installed)
        self.assertIn("fakepkg_dep", installed)

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_circular_dependency_does_not_loop(self, mock_meta, mock_fetch):
        """Circular Requires-Dist entries do not cause infinite recursion."""
        wheel_data = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\nRequires-Dist: fakepkg\n",
            {"fakepkg/__init__.py": b""},
        )
        digest = _sha256(wheel_data)
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-py3-none-any.whl",
            "https://example.com/fakepkg.whl",
            digest,
        )
        mock_fetch.return_value = wheel_data

        installed = install_package("fakepkg", self.target)
        self.assertIn("fakepkg", installed)
        # Only installed once despite the self-referential dep
        self.assertEqual(installed.count("fakepkg"), 1)

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_conditional_dependency_not_installed(self, mock_meta, mock_fetch):
        """Platform-conditional dependencies are not installed."""
        wheel_data = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\n"
            'Requires-Dist: pywin32; sys_platform == "win32"\n',
            {"fakepkg/__init__.py": b""},
        )
        digest = _sha256(wheel_data)
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-py3-none-any.whl",
            "https://example.com/fakepkg.whl",
            digest,
        )
        mock_fetch.return_value = wheel_data

        installed = install_package("fakepkg", self.target)
        self.assertIn("fakepkg", installed)
        self.assertNotIn("pywin32", installed)
        # pywin32 metadata should never have been fetched
        for call in mock_meta.call_args_list:
            self.assertNotEqual(call.args[0], "pywin32")


if __name__ == "__main__":
    unittest.main()
