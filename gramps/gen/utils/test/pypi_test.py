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
    _IMPORT_TO_PYPI,
    _compatible_tags,
    _direct_dependencies,
    _eval_marker,
    _find_satisfying_version,
    _gather_requirements,
    _glibc_version,
    _is_compatible_wheel,
    _is_prerelease,
    _is_pure_wheel,
    _is_yanked,
    _manylinux_platform_tags,
    _musl_version,
    _pick_wheel,
    _requires_python_ok,
    _satisfies_spec,
    _tokenize_marker,
    _top_level_names,
    _verify_sha256,
    _version_satisfies,
    _version_sort_key,
    _wheel_metadata,
    install_package,
    resolve_pypi_name,
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
# TestResolvePypiName
#
# -------------------------------------------------------------------------
class TestResolvePypiName(unittest.TestCase):
    def test_pil_maps_to_pillow(self):
        """PIL (current addon-source import name) maps to Pillow and warns."""
        with self.assertLogs("gramps.gen.utils.pypi", level="WARNING") as cm:
            result = resolve_pypi_name("PIL")
        self.assertEqual(result, "Pillow")
        self.assertTrue(any("PIL" in msg and "Pillow" in msg for msg in cm.output))

    def test_yaml_maps_to_pyyaml(self):
        """yaml import name maps to PyYAML."""
        self.assertEqual(resolve_pypi_name("yaml"), "PyYAML")

    def test_cv2_maps_to_opencv(self):
        """cv2 import name maps to opencv-python."""
        self.assertEqual(resolve_pypi_name("cv2"), "opencv-python")

    def test_bs4_maps_to_beautifulsoup4(self):
        """bs4 import name maps to beautifulsoup4."""
        self.assertEqual(resolve_pypi_name("bs4"), "beautifulsoup4")

    def test_serial_maps_to_pyserial(self):
        """serial import name maps to pyserial (not the unrelated 'serial' package)."""
        self.assertEqual(resolve_pypi_name("serial"), "pyserial")

    def test_sklearn_maps_to_scikit_learn(self):
        """sklearn stub has no wheels; maps to scikit-learn."""
        self.assertEqual(resolve_pypi_name("sklearn"), "scikit-learn")

    def test_unknown_name_returned_unchanged_no_warning(self):
        """A name not in the table is returned as-is and emits no warning."""
        with self.assertNoLogs("gramps.gen.utils.pypi", level="WARNING"):
            self.assertEqual(resolve_pypi_name("requests"), "requests")
            self.assertEqual(resolve_pypi_name("pypdf"), "pypdf")
            self.assertEqual(resolve_pypi_name("reportlab"), "reportlab")

    def test_all_mapping_values_are_strings(self):
        """Every entry in _IMPORT_TO_PYPI maps to a non-empty string."""
        for import_name, pypi_name in _IMPORT_TO_PYPI.items():
            self.assertIsInstance(pypi_name, str, import_name)
            self.assertTrue(pypi_name, import_name)

    def test_no_self_mappings(self):
        """No entry maps a name to itself (that would be a pointless entry)."""
        for import_name, pypi_name in _IMPORT_TO_PYPI.items():
            self.assertNotEqual(
                import_name.lower(),
                pypi_name.lower(),
                f"{import_name!r} maps to itself",
            )


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
# TestEvalMarker
#
# -------------------------------------------------------------------------
class TestEvalMarker(unittest.TestCase):
    def test_empty_marker_returns_true(self):
        """An empty marker string is always True."""
        self.assertTrue(_eval_marker(""))

    def test_sys_platform_match(self):
        """sys_platform matching the current platform returns True."""
        self.assertTrue(_eval_marker(f'sys_platform == "{sys.platform}"'))

    def test_sys_platform_no_match(self):
        """sys_platform for a different platform returns False."""
        other = "win32" if sys.platform != "win32" else "linux"
        self.assertFalse(_eval_marker(f'sys_platform == "{other}"'))

    def test_sys_platform_not_equal(self):
        """sys_platform != other_platform returns True."""
        other = "win32" if sys.platform != "win32" else "linux"
        self.assertTrue(_eval_marker(f'sys_platform != "{other}"'))
        self.assertFalse(_eval_marker(f'sys_platform != "{sys.platform}"'))

    def test_python_version_gte_low(self):
        """python_version >= a very low version is True."""
        self.assertTrue(_eval_marker('python_version >= "2.7"'))

    def test_python_version_gte_future(self):
        """python_version >= a far-future version is False."""
        self.assertFalse(_eval_marker('python_version >= "99.0"'))

    def test_python_version_uses_numeric_order(self):
        """python_version comparison uses version order, not lexicographic order."""
        # "3.10" > "3.9" numerically but "3.10" < "3.9" lexicographically.
        if sys.version_info >= (3, 10):
            self.assertTrue(_eval_marker('python_version >= "3.10"'))
        else:
            self.assertFalse(_eval_marker('python_version >= "3.10"'))

    def test_extra_not_requested(self):
        """extra == 'foo' is False when no extras are requested."""
        self.assertFalse(_eval_marker('extra == "security"'))

    def test_extra_requested(self):
        """extra == 'foo' is True when that extra is in the requested set."""
        self.assertTrue(_eval_marker('extra == "security"', frozenset({"security"})))

    def test_extra_wrong_name(self):
        """extra == 'foo' is False when a different extra is requested."""
        self.assertFalse(_eval_marker('extra == "security"', frozenset({"crypto"})))

    def test_and_both_true(self):
        """'A and B' is True when both A and B are True."""
        self.assertTrue(
            _eval_marker(
                f'sys_platform == "{sys.platform}" and python_version >= "2.7"'
            )
        )

    def test_and_one_false(self):
        """'A and B' is False when one side is False."""
        self.assertFalse(
            _eval_marker(
                f'sys_platform == "{sys.platform}" and python_version >= "99.0"'
            )
        )

    def test_or_one_true(self):
        """'A or B' is True when at least one side is True."""
        other = "win32" if sys.platform != "win32" else "linux"
        self.assertTrue(
            _eval_marker(f'sys_platform == "{other}" or python_version >= "2.7"')
        )

    def test_or_both_false(self):
        """'A or B' is False when both sides are False."""
        other = "win32" if sys.platform != "win32" else "linux"
        self.assertFalse(
            _eval_marker(f'sys_platform == "{other}" or python_version >= "99.0"')
        )

    def test_parenthesised_expression(self):
        """Parenthesised sub-expressions are evaluated correctly."""
        self.assertTrue(
            _eval_marker(
                f'(sys_platform == "{sys.platform}") and (python_version >= "2.7")'
            )
        )

    def test_parse_error_returns_true(self):
        """An unparseable marker returns True so no dep is silently dropped."""
        self.assertTrue(_eval_marker("this is completely invalid !!!"))

    def test_platform_system_match(self):
        """platform_system matching the current system returns True."""
        import platform

        self.assertTrue(_eval_marker(f'platform_system == "{platform.system()}"'))

    def test_implementation_name_cpython(self):
        """implementation_name == 'cpython' is True on CPython."""
        import platform

        impl = platform.python_implementation().lower()
        self.assertTrue(_eval_marker(f'implementation_name == "{impl}"'))


# -------------------------------------------------------------------------
#
# TestTokenizeMarker
#
# -------------------------------------------------------------------------
class TestTokenizeMarker(unittest.TestCase):
    def test_simple_comparison(self):
        """A simple equality expression tokenises correctly."""
        tokens = _tokenize_marker('sys_platform == "win32"')
        self.assertEqual(tokens, ["sys_platform", "==", '"win32"'])

    def test_not_in_merged(self):
        """'not' followed by 'in' is merged into the single token 'not in'."""
        tokens = _tokenize_marker('sys_platform not in "win32 linux"')
        self.assertEqual(tokens, ["sys_platform", "not in", '"win32 linux"'])

    def test_boolean_not_not_merged(self):
        """'not' before a parenthesised expression is kept as a separate token."""
        tokens = _tokenize_marker('not (sys_platform == "win32")')
        self.assertIn("not", tokens)
        self.assertIn("(", tokens)

    def test_and_or_keywords(self):
        """'and' and 'or' appear as distinct tokens."""
        tokens = _tokenize_marker('sys_platform == "win32" and python_version >= "3.8"')
        self.assertIn("and", tokens)

    def test_two_char_operators(self):
        """Two-character operators are tokenised as a single token."""
        for op in (">=", "<=", "==", "!=", "~="):
            tokens = _tokenize_marker(f'python_version {op} "3.8"')
            self.assertIn(op, tokens, f"operator {op!r} not found")

    def test_single_quoted_string(self):
        """Single-quoted string literals are included with their quotes."""
        tokens = _tokenize_marker("sys_platform == 'win32'")
        self.assertIn("'win32'", tokens)

    def test_whitespace_ignored(self):
        """Extra whitespace does not produce extra tokens."""
        tokens = _tokenize_marker('  sys_platform   ==   "win32"  ')
        self.assertEqual(tokens, ["sys_platform", "==", '"win32"'])


# -------------------------------------------------------------------------
#
# TestDirectDependencies
#
# -------------------------------------------------------------------------
class TestDirectDependencies(unittest.TestCase):
    def test_simple_dependency(self):
        """A bare package name is returned with an empty spec and no extras."""
        meta = {"requires-dist": "requests"}
        self.assertEqual(_direct_dependencies(meta), [("requests", "", frozenset())])

    def test_version_constraint_preserved(self):
        """Version specifiers are preserved alongside the dependency name."""
        meta = {"requires-dist": "requests>=2.0"}
        self.assertEqual(
            _direct_dependencies(meta), [("requests", ">=2.0", frozenset())]
        )

    def test_compound_constraint_preserved(self):
        """Multiple comma-joined constraints are kept intact."""
        meta = {"requires-dist": "requests>=2.0,<3"}
        self.assertEqual(
            _direct_dependencies(meta), [("requests", ">=2.0,<3", frozenset())]
        )

    def test_non_matching_platform_marker_skipped(self):
        """A dep whose platform marker does not match the current platform is skipped."""
        other = "win32" if sys.platform != "win32" else "linux"
        meta = {"requires-dist": f'pywin32>=1.0; sys_platform == "{other}"'}
        self.assertEqual(_direct_dependencies(meta), [])

    def test_matching_platform_marker_included(self):
        """A dep whose platform marker matches the current platform is included."""
        meta = {"requires-dist": f'foo; sys_platform == "{sys.platform}"'}
        result = _direct_dependencies(meta)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "foo")

    def test_extra_dependency_skipped_without_extras(self):
        """Extra-conditional dependencies are skipped when no extras are requested."""
        meta = {"requires-dist": 'cryptography; extra == "security"'}
        self.assertEqual(_direct_dependencies(meta), [])

    def test_extra_dependency_included_when_extra_requested(self):
        """Extra-conditional deps are included when the matching extra is requested."""
        meta = {"requires-dist": 'cryptography; extra == "security"'}
        result = _direct_dependencies(meta, frozenset({"security"}))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "cryptography")

    def test_dep_extras_parsed(self):
        """Extras in square brackets are parsed into dep_extras."""
        meta = {"requires-dist": "requests[security]>=2.0"}
        result = _direct_dependencies(meta)
        self.assertEqual(len(result), 1)
        name, spec, dep_extras = result[0]
        self.assertEqual(name, "requests")
        self.assertEqual(spec, ">=2.0")
        self.assertEqual(dep_extras, frozenset({"security"}))

    def test_dep_multiple_extras_parsed(self):
        """Multiple comma-separated extras in square brackets are all captured."""
        meta = {"requires-dist": "requests[security,crypto]"}
        result = _direct_dependencies(meta)
        _, _, dep_extras = result[0]
        self.assertEqual(dep_extras, frozenset({"security", "crypto"}))

    def test_multiple_dependencies(self):
        """Multiple deps on separate lines are all returned."""
        meta = {"requires-dist": "requests\nclick\nrich"}
        self.assertEqual(
            _direct_dependencies(meta),
            [
                ("requests", "", frozenset()),
                ("click", "", frozenset()),
                ("rich", "", frozenset()),
            ],
        )

    def test_mixed_conditional_and_plain(self):
        """Only unconditional and matching entries are returned from a mixed list."""
        other = "win32" if sys.platform != "win32" else "linux"
        meta = {
            "requires-dist": (
                "requests\n" f'pywin32; sys_platform == "{other}"\n' "click\n"
            )
        }
        self.assertEqual(
            _direct_dependencies(meta),
            [("requests", "", frozenset()), ("click", "", frozenset())],
        )

    def test_empty_metadata(self):
        """Missing requires-dist key returns an empty list."""
        self.assertEqual(_direct_dependencies({}), [])

    def test_blank_lines_ignored(self):
        """Blank lines in the requires-dist value are ignored."""
        meta = {"requires-dist": "\nrequests\n\nclick\n"}
        self.assertEqual(
            _direct_dependencies(meta),
            [("requests", "", frozenset()), ("click", "", frozenset())],
        )

    def test_compatible_release_specifier_preserved(self):
        """The ~= specifier is preserved in the version spec field."""
        meta = {"requires-dist": "mdurl~=0.3.2"}
        self.assertEqual(
            _direct_dependencies(meta), [("mdurl", "~=0.3.2", frozenset())]
        )


# -------------------------------------------------------------------------
#
# TestSatisfiesSpec
#
# -------------------------------------------------------------------------
class TestSatisfiesSpec(unittest.TestCase):
    def test_empty_spec_always_true(self):
        """An empty spec string is always satisfied."""
        self.assertTrue(_satisfies_spec("1.0", ""))

    def test_gte_satisfied(self):
        """Installed version >= required version passes >=."""
        self.assertTrue(_satisfies_spec("2.0", ">=1.0"))
        self.assertTrue(_satisfies_spec("1.0", ">=1.0"))

    def test_gte_not_satisfied(self):
        """Installed version below required fails >=."""
        self.assertFalse(_satisfies_spec("0.9", ">=1.0"))

    def test_lte_satisfied(self):
        """Installed version <= required passes <=."""
        self.assertTrue(_satisfies_spec("1.0", "<=2.0"))
        self.assertTrue(_satisfies_spec("2.0", "<=2.0"))

    def test_lte_not_satisfied(self):
        """Installed version above required fails <=."""
        self.assertFalse(_satisfies_spec("3.0", "<=2.0"))

    def test_gt_satisfied(self):
        """Strictly greater than passes >."""
        self.assertTrue(_satisfies_spec("1.1", ">1.0"))

    def test_gt_not_satisfied_equal(self):
        """Equal to the bound does not satisfy >."""
        self.assertFalse(_satisfies_spec("1.0", ">1.0"))

    def test_lt_satisfied(self):
        """Strictly less than passes <."""
        self.assertTrue(_satisfies_spec("0.9", "<1.0"))

    def test_lt_not_satisfied_equal(self):
        """Equal to the bound does not satisfy <."""
        self.assertFalse(_satisfies_spec("1.0", "<1.0"))

    def test_eq_exact_match(self):
        """Exact version equality passes ==."""
        self.assertTrue(_satisfies_spec("1.2.3", "==1.2.3"))

    def test_eq_no_match(self):
        """Different version fails ==."""
        self.assertFalse(_satisfies_spec("1.2.4", "==1.2.3"))

    def test_eq_wildcard_match(self):
        """Major.minor wildcard passes == when prefix matches."""
        self.assertTrue(_satisfies_spec("1.2.5", "==1.2.*"))

    def test_eq_wildcard_no_match(self):
        """Major.minor wildcard fails when prefix differs."""
        self.assertFalse(_satisfies_spec("1.3.0", "==1.2.*"))

    def test_neq_no_match(self):
        """Equal version fails !=."""
        self.assertFalse(_satisfies_spec("1.2.3", "!=1.2.3"))

    def test_neq_match(self):
        """Different version passes !=."""
        self.assertTrue(_satisfies_spec("1.2.4", "!=1.2.3"))

    def test_neq_wildcard_match(self):
        """Wildcard != excludes the whole minor series."""
        self.assertFalse(_satisfies_spec("1.2.9", "!=1.2.*"))

    def test_compatible_release_two_part(self):
        """~=X.Y means >=X.Y and <(X+1)."""
        self.assertTrue(_satisfies_spec("1.5", "~=1.4"))
        self.assertFalse(_satisfies_spec("2.0", "~=1.4"))
        self.assertFalse(_satisfies_spec("1.3", "~=1.4"))

    def test_compatible_release_three_part(self):
        """~=X.Y.Z means >=X.Y.Z and <X.(Y+1)."""
        self.assertTrue(_satisfies_spec("1.4.1", "~=1.4.0"))
        self.assertTrue(_satisfies_spec("1.4.9", "~=1.4.0"))
        self.assertFalse(_satisfies_spec("1.5.0", "~=1.4.0"))
        self.assertFalse(_satisfies_spec("1.3.9", "~=1.4.0"))

    def test_compound_spec(self):
        """Multiple comma-joined constraints are all checked."""
        self.assertTrue(_satisfies_spec("2.5", ">=2.0,<3.0"))
        self.assertFalse(_satisfies_spec("3.1", ">=2.0,<3.0"))
        self.assertFalse(_satisfies_spec("1.9", ">=2.0,<3.0"))


# -------------------------------------------------------------------------
#
# TestVersionSatisfies
#
# -------------------------------------------------------------------------
class TestVersionSatisfies(unittest.TestCase):
    def test_empty_spec_always_true(self):
        """An empty spec is always satisfied without querying metadata."""
        self.assertTrue(_version_satisfies("requests", ""))

    def test_installed_version_satisfies(self):
        """Returns True when dist-info reports a version satisfying the spec."""
        with patch(
            "gramps.gen.utils.pypi.importlib.metadata.version", return_value="2.31.0"
        ):
            self.assertTrue(_version_satisfies("requests", ">=2.0"))

    def test_installed_version_does_not_satisfy(self):
        """Returns False when dist-info reports a version failing the spec."""
        with patch(
            "gramps.gen.utils.pypi.importlib.metadata.version", return_value="1.5.0"
        ):
            self.assertFalse(_version_satisfies("requests", ">=2.0"))

    def test_hyphenated_name_fallback(self):
        """Tries the hyphenated form when the underscore form has no dist-info."""
        import importlib.metadata as _md

        def fake_version(name):
            if name == "python-dateutil":
                return "2.8.2"
            raise _md.PackageNotFoundError(name)

        with patch("gramps.gen.utils.pypi.importlib.metadata.version", fake_version):
            self.assertTrue(_version_satisfies("python_dateutil", ">=2.0"))

    def test_no_dist_info_returns_true(self):
        """Returns True (assume OK) when no dist-info exists for the package."""
        import importlib.metadata as _md

        with patch(
            "gramps.gen.utils.pypi.importlib.metadata.version",
            side_effect=_md.PackageNotFoundError("x"),
        ):
            self.assertTrue(_version_satisfies("somepkg", ">=1.0"))


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
        """A dep whose platform marker does not match the current platform is not installed."""
        other = "win32" if sys.platform != "win32" else "linux"
        wheel_data = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\n"
            f'Requires-Dist: pywin32; sys_platform == "{other}"\n',
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
    def test_extras_dep_installed_when_extra_requested(self, mock_meta, mock_fetch):
        """An extra-conditional dep is installed when that extra is requested."""
        dep_wheel = _make_wheel_zip(
            "Name: fakepkg_dep\nVersion: 1.0\n",
            {"fakepkg_dep/__init__.py": b""},
        )
        dep_digest = _sha256(dep_wheel)

        main_wheel = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\n"
            'Requires-Dist: fakepkg_dep; extra == "security"\n',
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
            raise PyPIInstallError(f"unexpected package: {package}")

        def fake_fetch(url):
            return dep_wheel if "fakepkg_dep" in url else main_wheel

        mock_meta.side_effect = fake_meta
        mock_fetch.side_effect = fake_fetch

        installed = install_package("fakepkg", self.target, frozenset({"security"}))
        self.assertIn("fakepkg", installed)
        self.assertIn("fakepkg_dep", installed)

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_extras_dep_not_installed_without_extra(self, mock_meta, mock_fetch):
        """An extra-conditional dep is NOT installed when the extra is not requested."""
        main_wheel = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\n"
            'Requires-Dist: fakepkg_dep; extra == "security"\n',
            {"fakepkg/__init__.py": b""},
        )
        main_digest = _sha256(main_wheel)
        mock_meta.return_value = _fake_pypi_meta(
            "fakepkg-1.0-py3-none-any.whl",
            "https://example.com/fakepkg.whl",
            main_digest,
        )
        mock_fetch.return_value = main_wheel

        installed = install_package("fakepkg", self.target)
        self.assertIn("fakepkg", installed)
        self.assertNotIn("fakepkg_dep", installed)
        for call in mock_meta.call_args_list:
            self.assertNotEqual(call.args[0], "fakepkg_dep")

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_extras_parsed_from_package_name(self, mock_meta, mock_fetch):
        """Extras embedded in the package name activate the matching extra deps."""
        dep_wheel = _make_wheel_zip(
            "Name: fakepkg_dep\nVersion: 1.0\n",
            {"fakepkg_dep/__init__.py": b""},
        )
        dep_digest = _sha256(dep_wheel)

        main_wheel = _make_wheel_zip(
            "Name: fakepkg\nVersion: 1.0\n"
            'Requires-Dist: fakepkg_dep; extra == "security"\n',
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
            raise PyPIInstallError(f"unexpected package: {package}")

        def fake_fetch(url):
            return dep_wheel if "fakepkg_dep" in url else main_wheel

        mock_meta.side_effect = fake_meta
        mock_fetch.side_effect = fake_fetch

        # "fakepkg[security]" parses the "security" extra from the name.
        installed = install_package("fakepkg[security]", self.target)
        self.assertIn("fakepkg", installed)
        self.assertIn("fakepkg_dep", installed)

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

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_version_conflict_resolved(self, mock_meta, mock_fetch):
        """Conflicting version constraints on a shared dep are resolved correctly.

        pkg_a requires deplib>=1.0,<2.0 and pkg_b requires deplib>=1.5.
        The resolver should pick deplib 1.9 (newest satisfying >=1.5,<2.0).
        pkg_b is a direct dep of pkg_a (declared in pkg_a's wheel METADATA).
        """
        # Build wheels for each package
        deplib_wheel = _make_wheel_zip(
            "Name: deplib\nVersion: 1.9\n",
            {"deplib/__init__.py": b""},
        )
        deplib_digest = _sha256(deplib_wheel)

        pkg_b_wheel = _make_wheel_zip(
            "Name: fakepkg_b\nVersion: 1.0\n",
            {"fakepkg_b/__init__.py": b""},
        )
        pkg_b_digest = _sha256(pkg_b_wheel)

        pkg_a_wheel = _make_wheel_zip(
            "Name: fakepkg_a\nVersion: 1.0\n"
            "Requires-Dist: fakepkg_b\n"
            "Requires-Dist: deplib>=1.0,<2.0\n",
            {"fakepkg_a/__init__.py": b""},
        )
        pkg_a_digest = _sha256(pkg_a_wheel)

        # PyPI JSON for each package (info.requires_dist drives the gather pass)
        deplib_releases = {
            "2.0": [
                {
                    "filename": "deplib-2.0-py3-none-any.whl",
                    "url": "u/2.0",
                    "digests": {},
                }
            ],
            "1.9": [
                {
                    "filename": "deplib-1.9-py3-none-any.whl",
                    "url": "https://example.com/deplib-1.9.whl",
                    "digests": {"sha256": deplib_digest},
                }
            ],
            "1.5": [
                {
                    "filename": "deplib-1.5-py3-none-any.whl",
                    "url": "u/1.5",
                    "digests": {},
                }
            ],
        }

        def fake_meta(package):
            if package == "fakepkg_a":
                return {
                    "info": {
                        "requires_dist": [
                            "fakepkg_b",
                            "deplib>=1.0,<2.0",
                        ]
                    },
                    "urls": [
                        {
                            "filename": "fakepkg_a-1.0-py3-none-any.whl",
                            "url": "https://example.com/fakepkg_a.whl",
                            "digests": {"sha256": pkg_a_digest},
                        }
                    ],
                    "releases": {},
                }
            if package == "fakepkg_b":
                return {
                    "info": {"requires_dist": ["deplib>=1.5"]},
                    "urls": [
                        {
                            "filename": "fakepkg_b-1.0-py3-none-any.whl",
                            "url": "https://example.com/fakepkg_b.whl",
                            "digests": {"sha256": pkg_b_digest},
                        }
                    ],
                    "releases": {},
                }
            if package == "deplib":
                return {
                    "info": {"requires_dist": []},
                    "urls": [],
                    "releases": deplib_releases,
                }
            raise PyPIInstallError(f"unexpected: {package}")

        def fake_fetch(url):
            if "fakepkg_b" in url:
                return pkg_b_wheel
            if "fakepkg_a" in url:
                return pkg_a_wheel
            if "deplib-1.9" in url:
                return deplib_wheel
            raise Exception(f"unexpected fetch: {url}")

        mock_meta.side_effect = fake_meta
        mock_fetch.side_effect = fake_fetch

        installed = install_package("fakepkg_a", self.target)

        self.assertIn("fakepkg_a", installed)
        self.assertIn("deplib", installed)
        # Verify the resolved 1.9 wheel was extracted (not the 2.0 that violates
        # the <2.0 constraint, nor the 1.5 when a newer 1.9 satisfies both).
        fetched_urls = [call.args[0] for call in mock_fetch.call_args_list]
        self.assertTrue(
            any("deplib-1.9" in u for u in fetched_urls),
            f"Expected deplib-1.9 to be fetched; got {fetched_urls}",
        )

    @patch("gramps.gen.utils.pypi._fetch_url")
    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_unsatisfiable_conflict_raises(self, mock_meta, mock_fetch):
        """When no version satisfies the combined constraints, PyPIInstallError is raised."""

        def fake_meta(package):
            if package == "fakepkg":
                return {
                    "info": {"requires_dist": ["deplib>=2.0"]},
                    "urls": [
                        {
                            "filename": "fakepkg-1.0-py3-none-any.whl",
                            "url": "u",
                            "digests": {},
                        }
                    ],
                    "releases": {},
                }
            if package == "deplib":
                return {
                    "info": {"requires_dist": []},
                    "releases": {
                        "1.9": [
                            {
                                "filename": "deplib-1.9-py3-none-any.whl",
                                "url": "u/1.9",
                                "digests": {},
                            }
                        ]
                    },
                    "urls": [],
                }
            raise PyPIInstallError(f"unexpected: {package}")

        mock_meta.side_effect = fake_meta

        # fakepkg requires deplib>=2.0 but only 1.9 is available → conflict
        with self.assertRaises(PyPIInstallError) as ctx:
            install_package("fakepkg", self.target)

        self.assertIn("deplib", str(ctx.exception))


# -------------------------------------------------------------------------
#
# TestIsPrerelease
#
# -------------------------------------------------------------------------
class TestIsPrerelease(unittest.TestCase):
    def test_stable_version_is_not_prerelease(self):
        """Plain version numbers are not pre-releases."""
        for ver in ("1.0", "2.3.4", "1.10.0", "1.0.post1", "1.0.post2"):
            self.assertFalse(_is_prerelease(ver), ver)

    def test_alpha_is_prerelease(self):
        """aN suffix marks a pre-release."""
        for ver in ("1.0a1", "2.0a12", "1.0.0a3"):
            self.assertTrue(_is_prerelease(ver), ver)

    def test_beta_is_prerelease(self):
        """bN suffix marks a pre-release."""
        for ver in ("1.0b1", "2.0b2"):
            self.assertTrue(_is_prerelease(ver), ver)

    def test_rc_is_prerelease(self):
        """rcN suffix marks a release candidate."""
        for ver in ("1.0rc1", "2.1.0rc3"):
            self.assertTrue(_is_prerelease(ver), ver)

    def test_dev_is_prerelease(self):
        """.devN suffix marks a development release."""
        for ver in ("1.0.dev0", "2.0.dev1"):
            self.assertTrue(_is_prerelease(ver), ver)

    def test_post_release_is_not_prerelease(self):
        """.postN is a post-release, not a pre-release."""
        self.assertFalse(_is_prerelease("1.0.post1"))
        self.assertFalse(_is_prerelease("2.3.post0"))


# -------------------------------------------------------------------------
#
# TestIsYanked
#
# -------------------------------------------------------------------------
class TestIsYanked(unittest.TestCase):
    def test_yanked_true(self):
        """File entry with yanked=True is yanked."""
        self.assertTrue(_is_yanked({"yanked": True}))

    def test_yanked_false(self):
        """File entry with yanked=False is not yanked."""
        self.assertFalse(_is_yanked({"yanked": False}))

    def test_yanked_absent(self):
        """File entry without a yanked field is not yanked."""
        self.assertFalse(_is_yanked({}))

    def test_yanked_reason_string_is_truthy(self):
        """Some PyPI responses set yanked to a non-empty reason string."""
        self.assertTrue(_is_yanked({"yanked": "security issue"}))


# -------------------------------------------------------------------------
#
# TestRequiresPythonOk
#
# -------------------------------------------------------------------------
class TestRequiresPythonOk(unittest.TestCase):
    def test_no_field_always_ok(self):
        """A missing requires_python field is always satisfied."""
        self.assertTrue(_requires_python_ok({}))

    def test_empty_string_always_ok(self):
        """An empty requires_python string is always satisfied."""
        self.assertTrue(_requires_python_ok({"requires_python": ""}))

    def test_satisfied_lower_bound(self):
        """requires_python >= a very low version is satisfied."""
        self.assertTrue(_requires_python_ok({"requires_python": ">=2.7"}))

    def test_unsatisfied_future_version(self):
        """requires_python >= 99.0 is not satisfied."""
        self.assertFalse(_requires_python_ok({"requires_python": ">=99.0"}))

    def test_exact_current_version(self):
        """requires_python == current major.minor is satisfied."""
        current = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.assertTrue(_requires_python_ok({"requires_python": f"=={current}.*"}))

    def test_none_field_always_ok(self):
        """requires_python=None (as returned by some PyPI entries) is always ok."""
        self.assertTrue(_requires_python_ok({"requires_python": None}))


# -------------------------------------------------------------------------
#
# TestGatherRequirements
#
# -------------------------------------------------------------------------
class TestGatherRequirements(unittest.TestCase):
    def _meta(self, requires_dist: list[str]) -> dict:
        """Build a minimal PyPI JSON dict with the given requires_dist list."""
        return {
            "info": {"requires_dist": requires_dist},
            "urls": [],
            "releases": {},
        }

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_versioned_dep_added_to_specs(self, mock_meta):
        """A dep with a version constraint is added to specs."""

        def fake_meta(package):
            if package == "mypkg":
                return self._meta(["requests>=2.0"])
            return self._meta([])

        mock_meta.side_effect = fake_meta
        specs: dict[str, list[str]] = {}
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertIn("requests", specs)
        self.assertEqual(specs["requests"], [">=2.0"])

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_unversioned_dep_not_added(self, mock_meta):
        """A dep with no version constraint is NOT added to specs."""

        def fake_meta(package):
            if package == "mypkg":
                return self._meta(["requests"])
            return self._meta([])

        mock_meta.side_effect = fake_meta
        specs: dict[str, list[str]] = {}
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertNotIn("requests", specs)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_multiple_constraints_accumulated(self, mock_meta):
        """Constraints from multiple packages on the same dep accumulate."""

        def fake_meta(package):
            if package == "pkg_a":
                return self._meta(["requests>=1.0,<3.0"])
            if package == "pkg_b":
                return self._meta(["requests>=2.0"])
            return self._meta([])

        mock_meta.side_effect = fake_meta
        specs: dict[str, list[str]] = {}
        # Gather from pkg_a (which dep-pulls pkg_b that also constrains requests)
        # We drive this manually by calling gather on both roots.
        _gather_requirements("pkg_a", frozenset(), specs, set())
        _gather_requirements("pkg_b", frozenset(), specs, set())
        self.assertIn("requests", specs)
        # Both constraints should be present (order may vary)
        combined = ",".join(specs["requests"])
        self.assertIn(">=1.0,<3.0", combined)
        self.assertIn(">=2.0", combined)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_circular_dependency_does_not_loop(self, mock_meta):
        """Circular deps do not cause infinite recursion."""

        def fake_meta(package):
            if package == "pkg_a":
                return self._meta(["pkg_b>=1.0"])
            if package == "pkg_b":
                return self._meta(["pkg_a>=1.0"])  # circular
            return self._meta([])

        mock_meta.side_effect = fake_meta
        specs: dict[str, list[str]] = {}
        _gather_requirements("pkg_a", frozenset(), specs, set())
        # Should complete without RecursionError; both constraints gathered
        self.assertIn("pkg_b", specs)
        self.assertIn("pkg_a", specs)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_marker_filtered_dep_not_gathered(self, mock_meta):
        """A dep whose platform marker does not match is not gathered."""
        other = "win32" if sys.platform != "win32" else "linux"

        def fake_meta(package):
            if package == "mypkg":
                return self._meta([f'pywin32>=1.0; sys_platform == "{other}"'])
            return self._meta([])

        mock_meta.side_effect = fake_meta
        specs: dict[str, list[str]] = {}
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertNotIn("pywin32", specs)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_pypi_error_handled_gracefully(self, mock_meta):
        """PyPIInstallError during gather does not propagate."""
        mock_meta.side_effect = PyPIInstallError("network down")
        specs: dict[str, list[str]] = {}
        # Should not raise; install pass will surface the real error
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertEqual(specs, {})

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_null_requires_dist_handled(self, mock_meta):
        """info.requires_dist == None does not raise."""
        mock_meta.return_value = {"info": {"requires_dist": None}, "releases": {}}
        specs: dict[str, list[str]] = {}
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertEqual(specs, {})

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_missing_info_key_handled(self, mock_meta):
        """Missing info key does not raise."""
        mock_meta.return_value = {"releases": {}}
        specs: dict[str, list[str]] = {}
        _gather_requirements("mypkg", frozenset(), specs, set())
        self.assertEqual(specs, {})


# -------------------------------------------------------------------------
#
# TestFindSatisfyingVersion
#
# -------------------------------------------------------------------------
class TestFindSatisfyingVersion(unittest.TestCase):
    def _meta_with_releases(self, versions: list[str]) -> dict:
        """Build a minimal PyPI JSON dict with the given release versions."""
        releases = {
            v: [{"filename": f"pkg-{v}-py3-none-any.whl", "url": f"u/{v}"}]
            for v in versions
        }
        return {"info": {}, "urls": [], "releases": releases}

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_newest_for_empty_spec(self, mock_meta):
        """An empty spec returns the newest available version."""
        mock_meta.return_value = self._meta_with_releases(["1.0", "1.10", "1.2"])
        result = _find_satisfying_version("pkg", "")
        self.assertEqual(result, "1.10")

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_newest_satisfying_gte(self, mock_meta):
        """>=1.5 returns the newest version that is at least 1.5."""
        mock_meta.return_value = self._meta_with_releases(["1.0", "1.5", "2.0", "3.0"])
        result = _find_satisfying_version("pkg", ">=1.5")
        self.assertEqual(result, "3.0")

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_newest_satisfying_range(self, mock_meta):
        """>=1.0,<2.0 returns the newest 1.x version."""
        mock_meta.return_value = self._meta_with_releases(
            ["0.9", "1.5", "1.9", "2.0", "3.0"]
        )
        result = _find_satisfying_version("pkg", ">=1.0,<2.0")
        self.assertEqual(result, "1.9")

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_none_when_no_version_satisfies(self, mock_meta):
        """Returns None when no release satisfies the combined spec."""
        mock_meta.return_value = self._meta_with_releases(["1.0", "1.5"])
        result = _find_satisfying_version("pkg", ">=2.0")
        self.assertIsNone(result)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_none_on_pypi_error(self, mock_meta):
        """Returns None when _pypi_metadata raises PyPIInstallError."""
        mock_meta.side_effect = PyPIInstallError("unreachable")
        result = _find_satisfying_version("pkg", ">=1.0")
        self.assertIsNone(result)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_returns_none_on_empty_releases(self, mock_meta):
        """Returns None when the releases dict is empty."""
        mock_meta.return_value = {"info": {}, "releases": {}}
        result = _find_satisfying_version("pkg", "")
        self.assertIsNone(result)

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_skips_prerelease_versions(self, mock_meta):
        """Pre-release versions are skipped; the newest stable is returned."""
        mock_meta.return_value = {
            "info": {},
            "releases": {
                "2.0a1": [{"filename": "pkg-2.0a1-py3-none-any.whl", "yanked": False}],
                "1.9": [{"filename": "pkg-1.9-py3-none-any.whl", "yanked": False}],
                "1.8": [{"filename": "pkg-1.8-py3-none-any.whl", "yanked": False}],
            },
        }
        result = _find_satisfying_version("pkg", "")
        self.assertEqual(result, "1.9")

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_skips_yanked_versions(self, mock_meta):
        """Fully-yanked releases are skipped."""
        mock_meta.return_value = {
            "info": {},
            "releases": {
                "2.0": [{"filename": "pkg-2.0-py3-none-any.whl", "yanked": True}],
                "1.9": [{"filename": "pkg-1.9-py3-none-any.whl", "yanked": False}],
            },
        }
        result = _find_satisfying_version("pkg", "")
        self.assertEqual(result, "1.9")

    @patch("gramps.gen.utils.pypi._pypi_metadata")
    def test_post_release_not_skipped(self, mock_meta):
        """Post-releases (.postN) are not treated as pre-releases."""
        mock_meta.return_value = {
            "info": {},
            "releases": {
                "1.0.post1": [
                    {"filename": "pkg-1.0.post1-py3-none-any.whl", "yanked": False}
                ],
                "1.0": [{"filename": "pkg-1.0-py3-none-any.whl", "yanked": False}],
            },
        }
        result = _find_satisfying_version("pkg", "")
        self.assertEqual(result, "1.0.post1")


# -------------------------------------------------------------------------
#
# TestPickWheelVersion
#
# -------------------------------------------------------------------------
class TestPickWheelVersion(unittest.TestCase):
    def _meta_with_version(self, version: str, filename: str) -> dict:
        """Build a minimal PyPI JSON dict with a single release."""
        return {
            "urls": [],
            "releases": {
                version: [
                    {
                        "filename": filename,
                        "url": f"https://example.com/{filename}",
                        "digests": {},
                    }
                ]
            },
        }

    def test_pinned_version_selects_release_files(self):
        """When version is given, files from that release are used."""
        meta = self._meta_with_version("1.5", "pkg-1.5-py3-none-any.whl")
        result = _pick_wheel(meta, "pkg", version="1.5")
        self.assertEqual(result["filename"], "pkg-1.5-py3-none-any.whl")

    def test_pinned_version_not_found_raises(self):
        """A pinned version with no compatible wheel raises PyPIInstallError."""
        meta = self._meta_with_version("1.5", "pkg-1.5-py3-none-any.whl")
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "pkg", version="9.9")

    def test_pinned_version_no_compatible_wheel_raises(self):
        """A pinned version present in releases but incompatible raises."""
        with patch(
            "gramps.gen.utils.pypi._compatible_tags",
            return_value=(set(), set(), set()),
        ):
            meta = self._meta_with_version(
                "1.5", "pkg-1.5-cp311-cp311-linux_x86_64.whl"
            )
            with self.assertRaises(PyPIInstallError):
                _pick_wheel(meta, "pkg", version="1.5")

    def test_yanked_wheel_in_urls_skipped(self):
        """A yanked file in meta['urls'] is not returned."""
        meta = {
            "urls": [
                {
                    "filename": "pkg-1.0-py3-none-any.whl",
                    "url": "u",
                    "digests": {},
                    "yanked": True,
                }
            ],
            "releases": {},
        }
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "pkg")

    def test_requires_python_mismatch_skipped(self):
        """A wheel whose requires_python the interpreter doesn't satisfy is skipped."""
        meta = {
            "urls": [
                {
                    "filename": "pkg-1.0-py3-none-any.whl",
                    "url": "u",
                    "digests": {},
                    "requires_python": ">=99.0",
                    "yanked": False,
                }
            ],
            "releases": {},
        }
        with self.assertRaises(PyPIInstallError):
            _pick_wheel(meta, "pkg")

    def test_requires_python_satisfied_returned(self):
        """A wheel whose requires_python is satisfied is returned normally."""
        meta = {
            "urls": [
                {
                    "filename": "pkg-1.0-py3-none-any.whl",
                    "url": "u",
                    "digests": {},
                    "requires_python": ">=2.7",
                    "yanked": False,
                }
            ],
            "releases": {},
        }
        result = _pick_wheel(meta, "pkg")
        self.assertEqual(result["filename"], "pkg-1.0-py3-none-any.whl")


# -------------------------------------------------------------------------
#
# TestGlibcVersion
#
# -------------------------------------------------------------------------
class TestGlibcVersion(unittest.TestCase):
    def setUp(self):
        _glibc_version.cache_clear()

    def tearDown(self):
        _glibc_version.cache_clear()

    def test_ctypes_path_returns_tuple(self):
        """_glibc_version returns (major, minor) when gnu_get_libc_version is found."""
        import gramps.gen.utils.pypi as pypi_mod
        from unittest.mock import MagicMock

        mock_ns = MagicMock()
        mock_fn = MagicMock(return_value=b"2.31")
        mock_ns.gnu_get_libc_version = mock_fn
        with patch("gramps.gen.utils.pypi.ctypes") as mock_ctypes:
            mock_ctypes.CDLL.return_value = mock_ns
            mock_ctypes.c_char_p = str  # restype assignment must not raise
            _glibc_version.cache_clear()
            result = _glibc_version()
        self.assertEqual(result, (2, 31))

    def test_fallback_to_platform_libc_ver(self):
        """Falls back to platform.libc_ver when ctypes path raises."""
        import gramps.gen.utils.pypi as pypi_mod

        with patch("gramps.gen.utils.pypi.ctypes") as mock_ctypes:
            mock_ctypes.CDLL.side_effect = OSError("no ctypes")
            with patch("platform.libc_ver", return_value=("glibc", "2.17")):
                _glibc_version.cache_clear()
                result = _glibc_version()
        self.assertEqual(result, (2, 17))

    def test_returns_none_on_non_glibc(self):
        """Returns None when both ctypes and platform.libc_ver report non-glibc."""
        with patch("gramps.gen.utils.pypi.ctypes") as mock_ctypes:
            mock_ctypes.CDLL.side_effect = OSError("no ctypes")
            with patch("platform.libc_ver", return_value=("musl", "1.2")):
                _glibc_version.cache_clear()
                result = _glibc_version()
        self.assertIsNone(result)

    def test_result_is_cached(self):
        """Calling _glibc_version twice returns the same object."""
        first = _glibc_version()
        second = _glibc_version()
        self.assertEqual(first, second)


# -------------------------------------------------------------------------
#
# TestMuslVersion
#
# -------------------------------------------------------------------------
class TestMuslVersion(unittest.TestCase):
    def setUp(self):
        _musl_version.cache_clear()

    def tearDown(self):
        _musl_version.cache_clear()

    def test_returns_version_when_linker_present(self):
        """Returns (major, minor) when the musl linker exists and prints its version."""
        with patch("platform.machine", return_value="x86_64"):
            with patch("os.path.exists", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(
                        stdout="musl libc (x86_64)\nVersion 1.2.3\n",
                        stderr="",
                    )
                    _musl_version.cache_clear()
                    result = _musl_version()
        self.assertEqual(result, (1, 2))

    def test_returns_none_when_linker_absent(self):
        """Returns None when the musl dynamic linker file does not exist."""
        with patch("platform.machine", return_value="x86_64"):
            with patch("os.path.exists", return_value=False):
                _musl_version.cache_clear()
                result = _musl_version()
        self.assertIsNone(result)

    def test_returns_none_when_subprocess_raises(self):
        """Returns None when running the musl linker raises an exception."""
        with patch("platform.machine", return_value="x86_64"):
            with patch("os.path.exists", return_value=True):
                with patch("subprocess.run", side_effect=OSError("exec failed")):
                    _musl_version.cache_clear()
                    result = _musl_version()
        self.assertIsNone(result)

    def test_arm_variant_normalised(self):
        """armv7l and other armv* are mapped to 'arm' for the linker path."""
        seen_paths = []

        def fake_exists(path):
            seen_paths.append(path)
            return False

        with patch("platform.machine", return_value="armv7l"):
            with patch("os.path.exists", side_effect=fake_exists):
                _musl_version.cache_clear()
                _musl_version()
        self.assertTrue(any("ld-musl-arm.so.1" in p for p in seen_paths))


# -------------------------------------------------------------------------
#
# TestManylinuxPlatformTags
#
# -------------------------------------------------------------------------
class TestManylinuxPlatformTags(unittest.TestCase):
    def test_pep600_tags_generated(self):
        """PEP 600 manylinux_2_Y tags are generated for Y from 5 to glibc_minor."""
        tags = _manylinux_platform_tags("x86_64", 2, 31)
        self.assertIn("manylinux_2_5_x86_64", tags)
        self.assertIn("manylinux_2_17_x86_64", tags)
        self.assertIn("manylinux_2_31_x86_64", tags)
        self.assertNotIn("manylinux_2_32_x86_64", tags)
        self.assertNotIn("manylinux_2_4_x86_64", tags)

    def test_legacy_aliases_x86_64(self):
        """manylinux1, manylinux2010, and manylinux2014 are added for x86_64."""
        tags = _manylinux_platform_tags("x86_64", 2, 31)
        self.assertIn("manylinux1_x86_64", tags)
        self.assertIn("manylinux2010_x86_64", tags)
        self.assertIn("manylinux2014_x86_64", tags)

    def test_legacy_aliases_aarch64(self):
        """Only manylinux2014 alias is generated for aarch64."""
        tags = _manylinux_platform_tags("aarch64", 2, 28)
        self.assertNotIn("manylinux1_aarch64", tags)
        self.assertNotIn("manylinux2010_aarch64", tags)
        self.assertIn("manylinux2014_aarch64", tags)

    def test_no_manylinux1_below_2_5(self):
        """manylinux1 is not generated when glibc_minor < 5."""
        tags = _manylinux_platform_tags("x86_64", 2, 4)
        self.assertNotIn("manylinux1_x86_64", tags)

    def test_no_manylinux2010_below_2_12(self):
        """manylinux2010 is not generated when glibc_minor < 12."""
        tags = _manylinux_platform_tags("x86_64", 2, 11)
        self.assertNotIn("manylinux2010_x86_64", tags)
        self.assertIn("manylinux1_x86_64", tags)

    def test_no_manylinux2014_below_2_17(self):
        """manylinux2014 is not generated when glibc_minor < 17."""
        tags = _manylinux_platform_tags("x86_64", 2, 16)
        self.assertNotIn("manylinux2014_x86_64", tags)
        self.assertIn("manylinux2010_x86_64", tags)

    def test_non_x86_arch_gets_no_manylinux1(self):
        """ppc64le does not get manylinux1 or manylinux2010 aliases."""
        tags = _manylinux_platform_tags("ppc64le", 2, 31)
        self.assertNotIn("manylinux1_ppc64le", tags)
        self.assertNotIn("manylinux2010_ppc64le", tags)
        self.assertIn("manylinux2014_ppc64le", tags)

    def test_unknown_arch_gets_no_legacy_aliases(self):
        """An unrecognised arch gets PEP 600 tags but no legacy aliases."""
        tags = _manylinux_platform_tags("riscv64", 2, 35)
        self.assertIn("manylinux_2_17_riscv64", tags)
        self.assertNotIn("manylinux1_riscv64", tags)
        self.assertNotIn("manylinux2010_riscv64", tags)
        self.assertNotIn("manylinux2014_riscv64", tags)

    def test_glibc_major_not_2_returns_empty(self):
        """Non-2.x glibc returns an empty tag set."""
        tags = _manylinux_platform_tags("x86_64", 3, 0)
        self.assertEqual(tags, set())


# -------------------------------------------------------------------------
#
# Extended TestCompatibleTags — Linux manylinux/musllinux
#
# -------------------------------------------------------------------------
class TestCompatibleTagsLinux(unittest.TestCase):
    def setUp(self):
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def tearDown(self):
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None

    def _linux_tags(
        self,
        machine: str = "x86_64",
        glibc: tuple[int, int] | None = (2, 31),
        musl: tuple[int, int] | None = None,
    ) -> set[str]:
        """Return plat_tags for a patched Linux environment."""
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None
        with patch("platform.system", return_value="Linux"):
            with patch("platform.machine", return_value=machine):
                with patch("gramps.gen.utils.pypi._glibc_version", return_value=glibc):
                    with patch(
                        "gramps.gen.utils.pypi._musl_version", return_value=musl
                    ):
                        _, _, plat_tags = _compatible_tags()
        return plat_tags

    def test_manylinux_tags_present_on_glibc_system(self):
        """manylinux tags are generated when glibc is detectable."""
        tags = self._linux_tags(machine="x86_64", glibc=(2, 31))
        self.assertIn("manylinux_2_17_x86_64", tags)
        self.assertIn("manylinux_2_31_x86_64", tags)
        self.assertIn("manylinux1_x86_64", tags)
        self.assertIn("manylinux2014_x86_64", tags)

    def test_bare_linux_tag_always_present(self):
        """linux_{arch} is always included regardless of libc."""
        tags = self._linux_tags(machine="x86_64", glibc=(2, 31))
        self.assertIn("linux_x86_64", tags)

    def test_no_manylinux_when_glibc_undetected(self):
        """No manylinux tags when glibc detection returns None."""
        tags = self._linux_tags(machine="x86_64", glibc=None)
        self.assertFalse(any(t.startswith("manylinux") for t in tags))
        self.assertIn("linux_x86_64", tags)

    def test_musllinux_tags_present_on_musl_system(self):
        """musllinux tags are generated when musl is detectable."""
        tags = self._linux_tags(machine="x86_64", glibc=None, musl=(1, 2))
        self.assertIn("musllinux_1_1_x86_64", tags)
        self.assertIn("musllinux_1_2_x86_64", tags)
        self.assertNotIn("musllinux_1_3_x86_64", tags)

    def test_musllinux_and_manylinux_mutually_exclusive_in_practice(self):
        """On a pure musl system glibc returns None and no manylinux tags appear."""
        tags = self._linux_tags(machine="x86_64", glibc=None, musl=(1, 2))
        self.assertFalse(any(t.startswith("manylinux") for t in tags))

    def test_aarch64_manylinux2014_present(self):
        """aarch64 gets manylinux2014 and PEP 600 tags but not manylinux1."""
        tags = self._linux_tags(machine="aarch64", glibc=(2, 28))
        self.assertIn("manylinux2014_aarch64", tags)
        self.assertIn("manylinux_2_17_aarch64", tags)
        self.assertNotIn("manylinux1_aarch64", tags)

    def test_any_always_present_on_linux(self):
        """\"any\" is always in plat_tags on Linux."""
        tags = self._linux_tags()
        self.assertIn("any", tags)

    def test_manylinux_wheel_compatible_on_glibc_system(self):
        """_is_compatible_wheel matches a manylinux2014 wheel on a glibc system."""
        import gramps.gen.utils.pypi as pypi_mod

        pypi_mod._COMPAT_TAGS = None
        with patch("platform.system", return_value="Linux"):
            with patch("platform.machine", return_value="x86_64"):
                with patch(
                    "gramps.gen.utils.pypi._glibc_version", return_value=(2, 31)
                ):
                    with patch(
                        "gramps.gen.utils.pypi._musl_version", return_value=None
                    ):
                        # Use py3-none tags so the test is Python-version-agnostic;
                        # "py3" and "none" are always in the compat sets.
                        info = {
                            "filename": "pkg-1.0-py3-none-manylinux_2_17_x86_64.whl"
                        }
                        self.assertTrue(_is_compatible_wheel(info))


if __name__ == "__main__":
    unittest.main()
