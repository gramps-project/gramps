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
    _compatible_tags,
    _direct_dependencies,
    _is_compatible_wheel,
    _is_pure_wheel,
    _pick_wheel,
    _top_level_names,
    _verify_sha256,
    _version_sort_key,
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
# TestCompatibleTags
#
# -------------------------------------------------------------------------
class TestCompatibleTags(unittest.TestCase):
    def setUp(self):
        # Reset the module-level cache before each test.
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def tearDown(self):
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def test_returns_three_non_empty_sets(self):
        """_compatible_tags returns three non-empty sets."""
        py_tags, abi_tags, plat_tags = _compatible_tags()
        self.assertIsInstance(py_tags, set)
        self.assertIsInstance(abi_tags, set)
        self.assertIsInstance(plat_tags, set)
        self.assertTrue(py_tags)
        self.assertTrue(abi_tags)
        self.assertTrue(plat_tags)

    def test_current_cpython_tag_in_py_tags(self):
        """The exact CPython version tag is always present."""
        import sys

        expected = f"cp{sys.version_info.major}{sys.version_info.minor}"
        py_tags, _, _ = _compatible_tags()
        self.assertIn(expected, py_tags)

    def test_py3_in_py_tags(self):
        """Generic py3 tag is always present."""
        py_tags, _, _ = _compatible_tags()
        self.assertIn("py3", py_tags)

    def test_abi3_and_none_in_abi_tags(self):
        """abi3 and none are always in abi_tags."""
        _, abi_tags, _ = _compatible_tags()
        self.assertIn("abi3", abi_tags)
        self.assertIn("none", abi_tags)

    def test_windows_amd64(self):
        """win_amd64 platform tag is generated for Windows AMD64."""
        with patch("platform.system", return_value="Windows"):
            with patch("platform.machine", return_value="AMD64"):
                import gramps.gen.utils.pypi as pypi_mod

                pypi_mod._COMPAT_TAGS = None
                _, _, plat_tags = _compatible_tags()
        self.assertIn("win_amd64", plat_tags)
        self.assertNotIn("win32", plat_tags)

    def test_windows_arm64(self):
        """win_arm64 platform tag is generated for Windows ARM64."""
        with patch("platform.system", return_value="Windows"):
            with patch("platform.machine", return_value="ARM64"):
                import gramps.gen.utils.pypi as pypi_mod

                pypi_mod._COMPAT_TAGS = None
                _, _, plat_tags = _compatible_tags()
        self.assertIn("win_arm64", plat_tags)

    def test_macos_arm64_includes_universal2(self):
        """macOS arm64 platform tags include universal2 variants."""
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.machine", return_value="arm64"):
                with patch(
                    "platform.mac_ver", return_value=("14.4.0", ("", "", ""), "")
                ):
                    import gramps.gen.utils.pypi as pypi_mod

                    pypi_mod._COMPAT_TAGS = None
                    _, _, plat_tags = _compatible_tags()
        self.assertIn("macosx_14_4_arm64", plat_tags)
        self.assertIn("macosx_11_0_arm64", plat_tags)
        self.assertIn("macosx_14_4_universal2", plat_tags)
        self.assertNotIn("macosx_14_5_arm64", plat_tags)

    def test_macos_x86_64_includes_older_versions(self):
        """macOS x86_64 tags span from 10.4 up to the current version."""
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.machine", return_value="x86_64"):
                with patch(
                    "platform.mac_ver", return_value=("13.0.0", ("", "", ""), "")
                ):
                    import gramps.gen.utils.pypi as pypi_mod

                    pypi_mod._COMPAT_TAGS = None
                    _, _, plat_tags = _compatible_tags()
        self.assertIn("macosx_10_9_x86_64", plat_tags)
        self.assertIn("macosx_13_0_x86_64", plat_tags)
        self.assertNotIn("macosx_13_1_x86_64", plat_tags)

    def test_result_is_cached(self):
        """Calling _compatible_tags twice returns the same objects."""
        first = _compatible_tags()
        second = _compatible_tags()
        self.assertIs(first, second)

    def test_macos_empty_version_does_not_crash(self):
        """Empty mac_ver() string does not raise; falls back to pure wheels only."""
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.machine", return_value="arm64"):
                with patch("platform.mac_ver", return_value=("", ("", "", ""), "")):
                    import gramps.gen.utils.pypi as pypi_mod

                    pypi_mod._COMPAT_TAGS = None
                    py_tags, abi_tags, plat_tags = _compatible_tags()
        # Must not raise; "any" must still be present so pure wheels match.
        self.assertIn("any", plat_tags)
        # No macosx_* tags should be generated when version is unknown.
        self.assertFalse(any(t.startswith("macosx_") for t in plat_tags))

    def test_any_always_in_plat_tags(self):
        """\"any\" is always in platform tags regardless of OS."""
        for system, machine, extra in [
            ("Windows", "AMD64", {}),
            ("Linux", "x86_64", {}),
            ("Darwin", "arm64", {"mac_ver": ("14.0.0", ("", "", ""), "")}),
        ]:
            with patch("platform.system", return_value=system):
                with patch("platform.machine", return_value=machine):
                    import gramps.gen.utils.pypi as pypi_mod

                    pypi_mod._COMPAT_TAGS = None
                    if "mac_ver" in extra:
                        with patch("platform.mac_ver", return_value=extra["mac_ver"]):
                            _, _, plat_tags = _compatible_tags()
                    else:
                        _, _, plat_tags = _compatible_tags()
            self.assertIn("any", plat_tags, f"'any' missing for {system}/{machine}")


# -------------------------------------------------------------------------
#
# TestIsCompatibleWheel
#
# -------------------------------------------------------------------------
class TestIsCompatibleWheel(unittest.TestCase):
    def setUp(self):
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def tearDown(self):
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def _patch_tags(self, py, abi, plat):
        return patch(
            "gramps.gen.utils.pypi._compatible_tags", return_value=(py, abi, plat)
        )

    def test_matching_compiled_wheel(self):
        """A wheel whose tags all intersect the compat sets is compatible."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"win_amd64"}):
            info = {"filename": "pkg-1.0-cp312-cp312-win_amd64.whl"}
            self.assertTrue(_is_compatible_wheel(info))

    def test_non_matching_platform(self):
        """A wheel for a different platform is not compatible."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"win_amd64"}):
            info = {"filename": "pkg-1.0-cp312-cp312-linux_x86_64.whl"}
            self.assertFalse(_is_compatible_wheel(info))

    def test_non_matching_python_version(self):
        """A wheel for a different CPython minor version is not compatible."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"win_amd64"}):
            info = {"filename": "pkg-1.0-cp311-cp311-win_amd64.whl"}
            self.assertFalse(_is_compatible_wheel(info))

    def test_abi3_wheel(self):
        """A cp38-abi3 wheel is compatible when abi3 is in abi_tags."""
        with self._patch_tags({"cp312", "cp38"}, {"abi3", "cp312"}, {"win_amd64"}):
            info = {"filename": "pkg-1.0-cp38-abi3-win_amd64.whl"}
            self.assertTrue(_is_compatible_wheel(info))

    def test_multi_tag_platform_any_match(self):
        """A dot-joined multi-tag platform field matches if any token matches."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"macosx_11_0_arm64"}):
            # Filename has three dot-joined platform tags; arm64 one matches.
            info = {
                "filename": (
                    "pkg-1.0-cp312-cp312"
                    "-macosx_10_12_x86_64.macosx_11_0_arm64"
                    ".macosx_10_12_universal2.whl"
                )
            }
            self.assertTrue(_is_compatible_wheel(info))

    def test_tarball_not_compatible(self):
        """Source tarballs are never compatible wheels."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"win_amd64"}):
            self.assertFalse(_is_compatible_wheel({"filename": "pkg-1.0.tar.gz"}))

    def test_too_few_parts(self):
        """Filenames with fewer than five dash-parts are rejected."""
        with self._patch_tags({"cp312"}, {"cp312"}, {"win_amd64"}):
            self.assertFalse(_is_compatible_wheel({"filename": "pkg-1.0-cp312.whl"}))

    def test_empty_compat_sets_never_match(self):
        """Empty compat sets mean nothing is compatible."""
        with self._patch_tags(set(), set(), set()):
            info = {"filename": "pkg-1.0-cp312-cp312-win_amd64.whl"}
            self.assertFalse(_is_compatible_wheel(info))

    def test_pure_any_wheel_is_compatible(self):
        """py3-none-any wheels are compatible on every platform."""
        # Use real tags — "any" should always be in plat_tags.
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None
        info = {"filename": "pkg-1.0-py3-none-any.whl"}
        self.assertTrue(_is_compatible_wheel(info))

    def test_py2py3_any_wheel_is_compatible(self):
        """py2.py3-none-any wheels are compatible on every platform."""
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None
        info = {"filename": "pkg-1.0-py2.py3-none-any.whl"}
        self.assertTrue(_is_compatible_wheel(info))


# -------------------------------------------------------------------------
#
# TestVersionSortKey
#
# -------------------------------------------------------------------------
class TestVersionSortKey(unittest.TestCase):
    def test_simple_versions(self):
        """Basic dotted versions sort numerically, not lexicographically."""
        self.assertGreater(_version_sort_key("1.10"), _version_sort_key("1.9"))
        self.assertGreater(_version_sort_key("2.0"), _version_sort_key("1.99"))

    def test_three_part_version(self):
        """Three-part versions are ordered correctly."""
        self.assertGreater(_version_sort_key("1.0.1"), _version_sort_key("1.0.0"))

    def test_equal_versions(self):
        """Identical version strings produce identical keys."""
        self.assertEqual(_version_sort_key("1.2.3"), _version_sort_key("1.2.3"))

    def test_empty_string_does_not_crash(self):
        """An empty version string returns an empty tuple without raising."""
        self.assertEqual(_version_sort_key(""), ())

    def test_non_numeric_segment_is_zero(self):
        """Non-numeric segments are treated as zero."""
        key = _version_sort_key("1.0.dev1")
        self.assertEqual(key[0], 1)
        self.assertEqual(key[1], 0)

    def test_sorted_release_list(self):
        """A list of version strings sorts newest-first when reversed."""
        versions = ["0.9", "1.0", "1.10", "1.2", "2.0"]
        result = sorted(versions, key=_version_sort_key, reverse=True)
        self.assertEqual(result, ["2.0", "1.10", "1.2", "1.0", "0.9"])


# -------------------------------------------------------------------------
#
# TestTopLevelNames
#
# -------------------------------------------------------------------------
class TestTopLevelNames(unittest.TestCase):
    def _make_wheel_with_toplevel(self, names: str) -> zipfile.ZipFile:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("pkg-1.0.dist-info/top_level.txt", names)
        return zipfile.ZipFile(io.BytesIO(buf.getvalue()))

    def _make_wheel_without_toplevel(self) -> zipfile.ZipFile:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("pkg-1.0.dist-info/METADATA", "Name: pkg\n")
        return zipfile.ZipFile(io.BytesIO(buf.getvalue()))

    def test_single_name(self):
        """A single entry in top_level.txt is returned."""
        with self._make_wheel_with_toplevel("PIL\n") as whl:
            self.assertEqual(_top_level_names(whl), ["PIL"])

    def test_multiple_names(self):
        """Multiple entries are all returned."""
        with self._make_wheel_with_toplevel("foo\nbar\nbaz\n") as whl:
            self.assertEqual(_top_level_names(whl), ["foo", "bar", "baz"])

    def test_blank_lines_ignored(self):
        """Blank lines in top_level.txt are ignored."""
        with self._make_wheel_with_toplevel("\nfoo\n\nbar\n") as whl:
            self.assertEqual(_top_level_names(whl), ["foo", "bar"])

    def test_absent_returns_empty_list(self):
        """A wheel without top_level.txt returns an empty list."""
        with self._make_wheel_without_toplevel() as whl:
            self.assertEqual(_top_level_names(whl), [])


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
        """A compiled wheel for a non-matching platform raises PyPIInstallError."""
        # Use a tag that will never match the test runner's platform.
        with patch(
            "gramps.gen.utils.pypi._compatible_tags", return_value=(set(), set(), set())
        ):
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

    def test_releases_searched_newest_first(self):
        """When falling back to releases, the newest version is preferred."""
        meta = {
            "urls": [],
            "releases": {
                "0.9": [
                    {
                        "filename": "mypkg-0.9-py3-none-any.whl",
                        "url": "u09",
                        "digests": {},
                    }
                ],
                "1.10": [
                    {
                        "filename": "mypkg-1.10-py3-none-any.whl",
                        "url": "u110",
                        "digests": {},
                    }
                ],
                "1.2": [
                    {
                        "filename": "mypkg-1.2-py3-none-any.whl",
                        "url": "u12",
                        "digests": {},
                    }
                ],
            },
        }
        result = _pick_wheel(meta, "mypkg")
        # 1.10 > 1.2 numerically, so it should be preferred over 1.2
        self.assertEqual(result["filename"], "mypkg-1.10-py3-none-any.whl")


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
        for name in ("fakepkg", "fakepkg_dep", "fakepkg_toplevel", "fakepkg_alt"):
            sys.modules.pop(name, None)

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
    def test_no_compatible_wheel_raises(self, mock_meta, mock_fetch):
        """A package with no compatible wheels raises PyPIInstallError."""
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-cp311-cp311-linux_x86_64.whl"
        )
        with patch(
            "gramps.gen.utils.pypi._compatible_tags",
            return_value=(set(), set(), set()),
        ):
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

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_skips_when_top_level_name_importable(self, mock_meta, mock_fetch):
        """A package whose top_level.txt name is importable is skipped even when
        the canonical PyPI name is not directly importable (e.g. Pillow → PIL)."""
        wheel_data = _make_wheel_zip(
            "Name: fakepkg_toplevel\nVersion: 1.0\n",
            {
                "fakepkg_toplevel-1.0.dist-info/top_level.txt": b"fakepkg_alt\n",
                "fakepkg_alt/__init__.py": b"",
            },
        )
        digest = _sha256(wheel_data)
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg_toplevel-1.0-py3-none-any.whl",
            "https://example.com/fakepkg_toplevel.whl",
            digest,
        )
        mock_fetch.return_value = wheel_data

        # Simulate "fakepkg_alt" already installed under its real import name.
        sys.modules["fakepkg_alt"] = MagicMock()

        installed = install_package("fakepkg_toplevel", self.target)

        # Package was not re-extracted.
        self.assertEqual(installed, [])
        # The wheel was downloaded (needed to read top_level.txt).
        mock_fetch.assert_called_once()
        # Nothing was written to the target directory.
        self.assertEqual(os.listdir(self.target), [])

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_installs_when_top_level_name_not_importable(self, mock_meta, mock_fetch):
        """A package is installed when its top_level.txt name is not yet importable."""
        wheel_data = _make_wheel_zip(
            "Name: fakepkg_toplevel\nVersion: 1.0\n",
            {
                "fakepkg_toplevel-1.0.dist-info/top_level.txt": b"fakepkg_alt\n",
                "fakepkg_alt/__init__.py": b"",
            },
        )
        digest = _sha256(wheel_data)
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg_toplevel-1.0-py3-none-any.whl",
            "https://example.com/fakepkg_toplevel.whl",
            digest,
        )
        mock_fetch.return_value = wheel_data

        installed = install_package("fakepkg_toplevel", self.target)

        self.assertIn("fakepkg_toplevel", installed)
        self.assertTrue(
            os.path.exists(os.path.join(self.target, "fakepkg_alt", "__init__.py"))
        )


if __name__ == "__main__":
    unittest.main()
