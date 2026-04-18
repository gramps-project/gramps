#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 B. Malengier
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
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
General utility functions useful for the generic plugin system
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any
from urllib.error import HTTPError, URLError

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...version import VERSION_TUPLE
from ..config import config
from ..const import GRAMPS_LOCALE as glocale
from ..const import USER_PLUGINS
from ..constfunc import mac
from . import BasePluginManager
from ._pluginreg import make_environment

LOG = logging.getLogger(".gen.plug")

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# Local utility functions for gen.plug
#
# -------------------------------------------------------------------------
def version_str_to_tup(sversion, positions):
    """
    Given a string version and positions count, returns a tuple of
    integers.

    >>> version_str_to_tup("1.02.9", 2)
    (1, 2)
    """
    try:
        tup = tuple(map(int, sversion.split(".")))
        tup += (0,) * (positions - len(tup))
    except:
        tup = (0,) * positions
    return tup[:positions]


class FakeRegistrar:
    """
    Fakes ``register`` and ``newplugin``.
    """

    def __init__(self):
        self.results = []

    @property
    def newplugin(self):
        class _newplugin:
            """
            Fake newplugin.
            """

            def __init__(inner_self):
                self.results.append({})

            def __setattr__(inner_self, attr, value):
                self.results[-1][attr] = value

        return _newplugin

    def register(self, ptype, **kwargs):
        """
        Fake registration. Side-effect sets results to kwargs.
        """
        retval = {"ptype": ptype}
        retval.update(kwargs)
        # Get the results back to calling function
        self.results.append(retval)


class Zipfile:
    """
    Class to duplicate the methods of tarfile.TarFile, for Python 2.5.
    """

    def __init__(self, buffer):
        import zipfile

        self.buffer = buffer
        self.zip_obj = zipfile.ZipFile(buffer)

    def extractall(self, path, members=None):
        """
        Extract all of the files in the zip into path.
        """
        names = self.zip_obj.namelist()
        for name in self.get_paths(names):
            fullname = os.path.join(path, name)
            if not os.path.exists(fullname):
                os.mkdir(fullname)
        for name in self.get_files(names):
            fullname = os.path.join(path, name)
            with open(fullname, "wb") as outfile:
                outfile.write(self.zip_obj.read(name))

    def extractfile(self, name):
        """
        Extract a name from the zip file.

        >>> Zipfile(buffer).extractfile("Dir/dile.py").read()
        <Contents>
        """

        class ExtractFile:
            """
            Simple class to extract a file
            """

            def __init__(self, zip_obj, name):
                self.zip_obj = zip_obj
                self.name = name

            def read(self):
                data = self.zip_obj.read(self.name)
                del self.zip_obj
                return data

        return ExtractFile(self.zip_obj, name)

    def close(self):
        """
        Close the zip object.
        """
        self.zip_obj.close()

    def getnames(self):
        """
        Get the files and directories of the zipfile.
        """
        return self.zip_obj.namelist()

    def get_paths(self, items):
        """
        Get the directories from the items.
        """
        return (name for name in items if self.is_path(name) and not self.is_file(name))

    def get_files(self, items):
        """
        Get the files from the items.
        """
        return (name for name in items if self.is_file(name))

    def is_path(self, name):
        """
        Is the name a path?
        """
        return os.path.split(name)[0]

    def is_file(self, name):
        """
        Is the name a directory?
        """
        return os.path.split(name)[1]


def urlopen_maybe_no_check_cert(url):
    """
    Similar to urllib.request.urlopen, but disables certificate
    verification on Mac.
    """
    context = None
    from urllib.request import urlopen

    if mac():
        from ssl import CERT_NONE, create_default_context

        context = create_default_context()
        context.check_hostname = False
        context.verify_mode = CERT_NONE
    timeout = 10  # seconds
    fptr = None
    try:
        fptr = urlopen(url, timeout=timeout, context=context)
    except TypeError:
        fptr = urlopen(url, timeout=timeout)
    return fptr


_PROJECT_URL_SCHEMES = ("http://", "https://", "file://")


def normalize_project_url(url: object) -> str | None:
    """
    Normalize an Addon Manager "project" URL.

    Strips surrounding whitespace and trailing slashes so that callers
    can build ``{url}/listings/addons-<lang>.json`` deterministically.
    Returns ``None`` for values that are not a string, are empty, or do
    not begin with a supported scheme (``http://``, ``https://``,
    ``file://``); these are the same schemes accepted by
    :func:`get_addons` today.
    """
    if not isinstance(url, str):
        return None
    stripped = url.strip()
    if not stripped:
        return None
    if not stripped.startswith(_PROJECT_URL_SCHEMES):
        return None
    while stripped.endswith("/") and not stripped.endswith("://"):
        stripped = stripped[:-1]
    return stripped


# ------------------------------------------------------------
#
# ProjectFetchStatus
#
# ------------------------------------------------------------
class ProjectFetchStatus:
    """
    String constants describing the outcome of a single Addon Manager
    project fetch. These are used both as machine-readable statuses
    and as stable identifiers for UI indicators, so values are kept
    short and untranslated.
    """

    OK = "ok"
    INVALID_URL = "invalid_url"
    NETWORK_ERROR = "network_error"
    HTTP_ERROR = "http_error"
    JSON_ERROR = "json_error"
    EMPTY_LISTING = "empty_listing"
    NO_COMPATIBLE_ADDONS = "no_compatible_addons"
    LANG_FALLBACK_EN = "lang_fallback_en"


# ------------------------------------------------------------
#
# ProjectFetchResult
#
# ------------------------------------------------------------
@dataclass
class ProjectFetchResult:
    """
    Structured result of :func:`classify_project_fetch`.

    ``status`` is one of the :class:`ProjectFetchStatus` constants.
    ``normalized_url`` is the cleaned URL that was actually tried, or
    ``None`` when the input could not be normalized. ``fetched_url``
    is the full listing URL that succeeded, if any; ``fetched_language``
    is the language code whose ``addons-<lang>.json`` was returned.
    ``http_code`` is populated for :data:`ProjectFetchStatus.HTTP_ERROR`.
    ``detail`` is a short English string suitable for logging or a
    tooltip. ``addon_count`` is the number of records in the listing;
    ``compatible_count`` is how many of them target the running major.
    minor Gramps version.
    """

    status: str
    requested_url: str
    normalized_url: str | None = None
    fetched_url: str | None = None
    fetched_language: str | None = None
    http_code: int | None = None
    detail: str | None = None
    addon_count: int = 0
    compatible_count: int = 0
    tried_languages: list[str] = field(default_factory=list)


def _candidate_languages(languages: list[str] | None) -> list[str]:
    """Build the ordered list of language codes to try, matching
    :func:`get_addons` behaviour: the user's locale chain followed by
    ``en`` as a final fallback, with duplicates removed."""
    if languages is None:
        langs = list(glocale.get_language_list())
        langs.append("en")
    else:
        langs = list(languages)
    seen: set[str] = set()
    ordered: list[str] = []
    for lang in langs:
        if lang and lang not in seen:
            ordered.append(lang)
            seen.add(lang)
    return ordered


def _try_fetch_listing(url: str, lang: str) -> tuple[Any, str | None, int]:
    """Try ``addons-<lang>.json`` then ``addons-<lang[:2]>.json``.

    Returns ``(fptr, fetched_url, http_code)`` on a 200-or-file success,
    or ``(None, None, code)`` otherwise. ``code`` is ``0`` when no HTTP
    status was obtained (network error, file:// not found, ...).
    Raises :class:`URLError` for pure network failures so that the
    caller can distinguish them from HTTP errors.
    """
    candidates = [f"{url}/listings/addons-{lang}.json"]
    short = lang[:2]
    if short and short != lang:
        candidates.append(f"{url}/listings/addons-{short}.json")
    last_http_code = 0
    last_network_error: URLError | None = None
    for addon_url in candidates:
        try:
            fptr = urlopen_maybe_no_check_cert(addon_url)
        except HTTPError as err:
            last_http_code = err.code
            continue
        except URLError as err:
            last_network_error = err
            continue
        code = 0
        try:
            code = fptr.getcode() or 0
        except AttributeError:
            code = 0
        is_file = getattr(fptr, "file", None) is not None
        if code == 200 or is_file:
            return fptr, addon_url, code or 200
        last_http_code = code
        try:
            fptr.close()
        except Exception:
            pass
    if last_http_code:
        return None, None, last_http_code
    if last_network_error is not None:
        raise last_network_error
    return None, None, 0


def classify_project_fetch(
    url: object,
    current_version: tuple[int, int, int] | None = None,
    languages: list[str] | None = None,
) -> ProjectFetchResult:
    """
    Fetch the ``addons-<lang>.json`` listing for ``url`` and classify
    the outcome.

    The classifier never raises: any problem is reported via
    :class:`ProjectFetchResult`. The call does not mutate any global
    state and does not update the plugin manager; it exists so that
    the Addon Manager UI can render a per-project status indicator
    (bug #13069) without re-implementing the lookup logic.

    ``current_version`` defaults to the running Gramps
    :data:`VERSION_TUPLE`; pass an explicit tuple in tests to pin the
    compatibility check. ``languages`` overrides the locale list in
    the same way.
    """
    requested_url = url if isinstance(url, str) else ""
    normalized = normalize_project_url(url)
    if normalized is None:
        return ProjectFetchResult(
            status=ProjectFetchStatus.INVALID_URL,
            requested_url=requested_url,
            detail=_(
                "URL is empty or does not start with http://, https:// or file://"
            ),
        )
    candidate_langs = _candidate_languages(languages)
    tried: list[str] = []
    fptr: Any = None
    fetched_url: str | None = None
    fetched_language: str | None = None
    last_http_code = 0
    network_error: URLError | None = None
    for lang in candidate_langs:
        tried.append(lang)
        try:
            fptr, fetched_url, code = _try_fetch_listing(normalized, lang)
        except URLError as err:
            network_error = err
            continue
        if fptr is not None:
            fetched_language = lang
            break
        if code:
            last_http_code = code
    if fptr is None:
        if network_error is not None:
            return ProjectFetchResult(
                status=ProjectFetchStatus.NETWORK_ERROR,
                requested_url=requested_url,
                normalized_url=normalized,
                detail=_("Network error: %s") % network_error.reason,
                tried_languages=tried,
            )
        if last_http_code:
            return ProjectFetchResult(
                status=ProjectFetchStatus.HTTP_ERROR,
                requested_url=requested_url,
                normalized_url=normalized,
                http_code=last_http_code,
                detail=_("HTTP %s while fetching listing") % last_http_code,
                tried_languages=tried,
            )
        return ProjectFetchResult(
            status=ProjectFetchStatus.NETWORK_ERROR,
            requested_url=requested_url,
            normalized_url=normalized,
            detail=_("No listing could be fetched"),
            tried_languages=tried,
        )
    try:
        try:
            payload = json.load(fptr)
        except (ValueError, UnicodeDecodeError) as err:
            return ProjectFetchResult(
                status=ProjectFetchStatus.JSON_ERROR,
                requested_url=requested_url,
                normalized_url=normalized,
                fetched_url=fetched_url,
                fetched_language=fetched_language,
                detail=_("Listing is not valid JSON: %s") % err,
                tried_languages=tried,
            )
    finally:
        try:
            fptr.close()
        except Exception:
            pass
    if not isinstance(payload, list):
        return ProjectFetchResult(
            status=ProjectFetchStatus.JSON_ERROR,
            requested_url=requested_url,
            normalized_url=normalized,
            fetched_url=fetched_url,
            fetched_language=fetched_language,
            detail=_("Listing is not a JSON array"),
            tried_languages=tried,
        )
    addon_count = len(payload)
    target_major_minor = (
        current_version[:2] if current_version is not None else VERSION_TUPLE[:2]
    )
    compatible = 0
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        entry_version = entry.get("t")
        if not isinstance(entry_version, str):
            continue
        if version_str_to_tup(entry_version, 2) == target_major_minor:
            compatible += 1
    if addon_count == 0:
        status = ProjectFetchStatus.EMPTY_LISTING
        detail = _("Listing fetched but contained no entries")
    elif compatible == 0:
        status = ProjectFetchStatus.NO_COMPATIBLE_ADDONS
        detail = _("Listing fetched but no entries target the running Gramps %s.%s") % (
            target_major_minor[0],
            target_major_minor[1],
        )
    elif fetched_language == "en" and candidate_langs and candidate_langs[0] != "en":
        status = ProjectFetchStatus.LANG_FALLBACK_EN
        detail = (
            _("No listing for the requested language; fell back to %s")
            % fetched_language
        )
    else:
        status = ProjectFetchStatus.OK
        detail = None
    return ProjectFetchResult(
        status=status,
        requested_url=requested_url,
        normalized_url=normalized,
        fetched_url=fetched_url,
        fetched_language=fetched_language,
        detail=detail,
        addon_count=addon_count,
        compatible_count=compatible,
        tried_languages=tried,
    )


def get_addons(project, url):
    """
    Get addons
    """
    LOG.debug("Checking for updated addons...")
    if not url.startswith(("http://", "https://", "file://")):
        return []
    langs = glocale.get_language_list()
    langs.append("en")
    # now we have a list of languages to try:
    fptr = None
    for lang in langs:
        addon_url = f"{url}/listings/addons-{lang}.json"
        LOG.debug("   trying: %s", addon_url)
        try:
            fptr = urlopen_maybe_no_check_cert(addon_url)
        except:
            try:
                addon_url = f"{url}/listings/addons-{lang[:2]}.json"
                fptr = urlopen_maybe_no_check_cert(addon_url)
            except Exception as err:  # some error
                LOG.warning(
                    "Failed to open addon metadata for %s %s: %s", lang, addon_url, err
                )
                fptr = None
        if fptr and (fptr.getcode() == 200 or fptr.file):
            break

    addon_list = []
    if fptr and (fptr.getcode() == 200 or fptr.file):
        addon_list = json.load(fptr)
        for plugin_dict in addon_list:
            if "a" not in plugin_dict:
                plugin_dict["a"] = 0
            if "s" not in plugin_dict:
                plugin_dict["s"] = 0
            if "h" not in plugin_dict:
                plugin_dict["h"] = ""
            plugin_dict["_p"] = project
            plugin_dict["_u"] = url
            pmgr = BasePluginManager.get_instance()
            plugin = pmgr.get_plugin(plugin_dict["i"])
            if plugin:
                plugin_dict["_v"] = plugin.version
    else:
        LOG.debug("Checking Addons Failed")
    LOG.debug("Done checking!")

    return addon_list


def get_all_addons():
    """
    Get addons for all projects
    """
    projects = config.get("behavior.addons-projects")
    all_addons = []
    for project, url, enabled in projects:
        if enabled:
            addons_list = get_addons(project, url)
            all_addons.extend(addons_list)
    return all_addons


def available_updates():
    """
    Check for available updates
    """
    whattypes = config.get("behavior.check-for-addon-update-types")
    addon_update_list = []
    for plugin_dict in get_all_addons():
        if "_v" in plugin_dict:
            LOG.debug(
                "Comparing %s > %s",
                version_str_to_tup(plugin_dict["v"], 3),
                version_str_to_tup(plugin_dict["_v"], 3),
            )
            if version_str_to_tup(plugin_dict["v"], 3) > version_str_to_tup(
                plugin_dict["_v"], 3
            ):
                LOG.debug("   Downloading '%s'...", plugin_dict["z"])
                if "update" in whattypes:
                    if not config.get(
                        "behavior.do-not-show-previously-seen-addon-updates"
                    ) or plugin_dict["i"] not in config.get(
                        "behavior.previously-seen-addon-updates"
                    ):
                        addon_update_list.append(
                            (
                                _("Updated"),
                                "%s/download/%s"
                                % (plugin_dict["_u"], plugin_dict["z"]),
                                plugin_dict,
                            )
                        )
            else:
                LOG.debug("   '%s' is ok", plugin_dict["n"])
        else:
            LOG.debug("   '%s' is not installed", plugin_dict["n"])
            if "new" in whattypes:
                if not config.get(
                    "behavior.do-not-show-previously-seen-addon-updates"
                ) or plugin_dict["i"] not in config.get(
                    "behavior.previously-seen-addon-updates"
                ):
                    addon_update_list.append(
                        (
                            _("New", "updates"),
                            "%s/download/%s" % (plugin_dict["_u"], plugin_dict["z"]),
                            plugin_dict,
                        )
                    )
    config.set(
        "behavior.last-check-for-addon-updates",
        datetime.date.today().strftime("%Y/%m/%d"),
    )

    return addon_update_list


def load_addon_file(path, callback=None):
    """
    Load an addon from a particular path (from URL or file system).
    """
    import tarfile

    if path.startswith(("http://", "https://", "ftp://", "file://")):
        try:
            fptr = urlopen_maybe_no_check_cert(path)
        except:
            if callback:
                callback(_("Unable to open '%s'") % path)
            return False
    else:
        try:
            fptr = open(path, "rb")
        except:
            if callback:
                callback(_("Unable to open '%s'") % path)
            return False
    try:
        content = fptr.read()
        buffer = BytesIO(content)
    except:
        if callback:
            callback(_("Error in reading '%s'") % path)
        return False
    fptr.close()
    # file_obj is either Zipfile or TarFile
    if path.endswith((".zip", ".ZIP")):
        file_obj = Zipfile(buffer)
    elif path.endswith((".tar.gz", ".tgz")):
        try:
            file_obj = tarfile.open(None, fileobj=buffer)
        except:
            if callback:
                callback(_("Error: cannot open '%s'") % path)
            return False
    else:
        if callback:
            callback(_("Error: unknown file type: '%s'") % path)
        return False
    # First, see what versions we have/are getting:
    good_gpr = set()
    for gpr_file in [name for name in file_obj.getnames() if name.endswith(".gpr.py")]:
        if callback:
            callback((_("Examining '%s'...") % gpr_file) + "\n")
        contents = file_obj.extractfile(gpr_file).read()
        registrar = FakeRegistrar()
        # Put a fake register and _ function in environment:
        env = make_environment(
            register=registrar.register,
            newplugin=registrar.newplugin,
            _=lambda text: text,
        )
        # evaluate the contents:
        try:
            exec(contents, env)
        except Exception as exp:
            if callback:
                msg = _("Error in '%s' file: cannot load.") % gpr_file
                callback("   " + msg + "\n" + str(exp))
            continue
        # There can be multiple addons per gpr file:
        for results in registrar.results:
            gramps_target_version = results.get("gramps_target_version", None)
            if gramps_target_version:
                vtup = version_str_to_tup(gramps_target_version, 2)
                # Is it for the right version of gramps?
                if vtup == VERSION_TUPLE[0:2]:
                    # If this version is not installed, or > installed, install it
                    good_gpr.add(gpr_file)
                    if callback:
                        callback(
                            "   "
                            + (_("'%s' is for this version of Gramps.") % id)
                            + "\n"
                        )
                else:
                    # If the plugin is for another version; inform and do nothing
                    if callback:
                        callback(
                            "   "
                            + (_("'%s' is NOT for this version of Gramps.") % id)
                            + "\n"
                        )
                        callback(
                            "   "
                            + (
                                _("It is for version %(v1)d.%(v2)d")
                                % {"v1": vtup[0], "v2": vtup[1]}
                                + "\n"
                            )
                        )
                    continue
            else:
                # another register function doesn't have gramps_target_version
                if gpr_file in good_gpr:
                    os.remove(gpr_file)
                if callback:
                    callback(
                        "   "
                        + (
                            _("Error: missing gramps_target_version in '%s'...")
                            % gpr_file
                        )
                        + "\n"
                    )
    registered_count = 0
    if len(good_gpr) > 0:
        # Now, install the ok ones
        try:
            file_obj.extractall(USER_PLUGINS)
        except OSError:
            if callback:
                callback(f"OSError installing '{path}', skipped!")
            file_obj.close()
            return False
        if callback:
            callback((_("Installing '%s'...") % path) + "\n")
        gpr_files = {
            os.path.split(os.path.join(USER_PLUGINS, name))[0] for name in good_gpr
        }
        for gpr_file in gpr_files:
            if callback:
                callback("   " + (_("Registered '%s'") % gpr_file) + "\n")
            registered_count += 1
    file_obj.close()
    if registered_count:
        return True
    return False


# -------------------------------------------------------------------------
#
# OpenFileOrStdout class
#
# -------------------------------------------------------------------------
class OpenFileOrStdout:
    """Context manager to open a file or stdout for writing."""

    def __init__(self, filename, encoding=None, errors=None, newline=None):
        self.filename = filename
        self.filehandle = None
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

    def __enter__(self):
        if self.filename == "-":
            self.filehandle = sys.stdout
        else:
            self.filehandle = open(
                self.filename,
                "w",
                encoding=self.encoding,
                errors=self.errors,
                newline=self.newline,
            )
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filehandle and self.filename != "-":
            self.filehandle.close()
        return False


# -------------------------------------------------------------------------
#
# OpenFileOrStdin class
#
# -------------------------------------------------------------------------
class OpenFileOrStdin:
    """Context manager to open a file or stdin for reading."""

    def __init__(self, filename, add_mode="", encoding=None):
        self.filename = filename
        self.mode = f"r{add_mode}"
        self.filehandle = None
        self.encoding = encoding

    def __enter__(self):
        if self.filename == "-":
            self.filehandle = sys.stdin
        elif self.encoding:
            self.filehandle = open(self.filename, self.mode, encoding=self.encoding)
        else:
            self.filehandle = open(self.filename, self.mode)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename != "-":
            self.filehandle.close()
        return False


# -------------------------------------------------------------------------
#
# get_cite function
#
# -------------------------------------------------------------------------
def get_cite():
    """
    Function that returns the active cite plugin.
    """
    plugman = BasePluginManager.get_instance()
    for pdata in plugman.get_reg_cite():
        if pdata.id != config.get("preferences.cite-plugin"):
            continue
        module = plugman.load_plugin(pdata)
        if not module:
            print(f"Error loading formatter '{pdata.name}': skipping content")
            continue
        cite = getattr(module, "Formatter")()
        return cite
