#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009-2010  Stephen George
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2011       Paul Franklin
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import sys
import os
import signal

import logging

LOG = logging.getLogger(".")

from subprocess import Popen, PIPE

# -------------------------------------------------------------------------
# process 'safe mode'; set up for a temp directory for user data
# actual directory paths set up in const module
if "-S" in sys.argv or "--safe" in sys.argv:
    from tempfile import TemporaryDirectory

    tempdir = TemporaryDirectory(prefix="gramps_")
    os.environ["SAFEMODE"] = tempdir.name

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .gen.const import APP_GRAMPS, USER_DIRLIST, USER_DATA, ORIG_HOME_DIR
from .gen.constfunc import mac
from .version import VERSION_TUPLE
from .gen.constfunc import win, get_env_var
from .gen.config import config
from .gen.errors import HandleError

# -------------------------------------------------------------------------
#
# Instantiate Localization
#
# -------------------------------------------------------------------------

from .gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Ensure that output is encoded correctly to stdout and
# stderr. This is much less cumbersome and error-prone than
# encoding individual outputs:
#
# -------------------------------------------------------------------------

try:
    # On Darwin sys.getdefaultencoding() is correct, on Win32 it's
    # sys.stdout.encoding, and on Linux they're both right.
    if mac():
        _encoding = sys.getdefaultencoding()
    else:
        _encoding = sys.stdout.encoding
except:
    _encoding = "UTF-8"
try:
    sys.stdout = open(
        sys.stdout.fileno(),
        mode="w",
        encoding=_encoding,
        buffering=1,
        errors="backslashreplace",
    )
    sys.stderr = open(
        sys.stderr.fileno(),
        mode="w",
        encoding=_encoding,
        buffering=1,
        errors="backslashreplace",
    )
except:
    pass

# -------------------------------------------------------------------------
#
# Setup logging
#
# Ideally, this needs to be done before any Gramps modules are
# imported, so that any code that is executed as the modules are
# imported can log errors or warnings.  const and constfunc have to be
# imported before this code is executed because they are used in this
# code. That unfortunately initializes GrampsLocale, so it has its own
# logging setup during initialization.
# -------------------------------------------------------------------------
"""Set up basic logging support."""

# Setup a formatter
form = logging.Formatter(
    fmt="%(asctime)s.%(msecs).03d: %(levelname)s: "
    "%(filename)s: line %(lineno)d: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create the log handlers
if win():
    # If running in GUI mode redirect stdout and stderr to log file
    if not sys.stdout:
        logfile = os.path.join(USER_DATA, "Gramps%s%s.log") % (
            VERSION_TUPLE[0],
            VERSION_TUPLE[1],
        )
        # We now carry out the first step in build_user_paths(), to make sure
        # that the user home directory is available to store the log file. When
        # build_user_paths() is called, the call is protected by a try...except
        # block, and any failure will be logged. However, if the creation of the
        # user directory fails here, there is no way to report the failure,
        # because stdout/stderr are not available, and neither is the logfile.
        if os.path.islink(USER_DATA):
            pass  # ok
        elif not os.path.isdir(USER_DATA):
            os.makedirs(USER_DATA)
        sys.stdout = sys.stderr = open(logfile, "w", encoding="utf-8")
# macOS sets stderr to /dev/null when running without a terminal,
# e.g. if Gramps.app is lauched by double-clicking on it in
# finder. Write to a file instead.
if mac() and not sys.stdin.isatty():
    from tempfile import gettempdir

    log_file_name = "gramps-" + str(os.getpid()) + ".log"
    log_file_path = os.path.join(gettempdir(), log_file_name)
    log_file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    log_file_handler.setFormatter(form)
    log_file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.addHandler(log_file_handler)
else:
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # Setup the base level logger, this one gets
    # everything.
    l = logging.getLogger()
    l.setLevel(logging.WARNING)
    l.addHandler(stderrh)


def exc_hook(err_type, value, t_b):
    """put a hook on to catch any completely unhandled exceptions."""
    if err_type == KeyboardInterrupt:
        # Ctrl-C is not a bug.
        return
    if err_type == IOError:
        # strange Windows logging error on close
        return
    if err_type == HandleError and "not found" in value.value:
        # tell Gramps to run check & repair on next start
        config.set("behavior.runcheck", True)
        config.save()
    # Use this to show variables in each frame:
    # from gramps.gen.utils.debug import format_exception
    import traceback

    LOG.error(
        "Unhandled exception\n"
        + "".join(traceback.format_exception(err_type, value, t_b))
    )


sys.excepthook = exc_hook

from .gen.mime import mime_type_is_defined


# -------------------------------------------------------------------------
#
# Minimum version check
#
# -------------------------------------------------------------------------

MIN_PYTHON_VERSION = (3, 8, 0, "", 0)
if not sys.version_info >= MIN_PYTHON_VERSION:
    logging.warning(
        _(
            "Your Python version does not meet the "
            "requirements. At least Python %(v1)d.%(v2)d.%(v3)d is needed to"
            " start Gramps.\n\n"
            "Gramps will terminate now."
        )
        % {
            "v1": MIN_PYTHON_VERSION[0],
            "v2": MIN_PYTHON_VERSION[1],
            "v3": MIN_PYTHON_VERSION[2],
        }
    )
    sys.exit(1)

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
try:
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
except:
    pass

args = sys.argv


def build_user_paths():
    """check/make user-dirs on each Gramps session"""
    for path in USER_DIRLIST:
        if os.path.islink(path):
            pass  # ok
        elif not os.path.isdir(path):
            os.makedirs(path)


def show_settings():
    """
    Shows settings of all of the major components.
    """
    py_str = "%d.%d.%d" % sys.version_info[:3]
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        try:
            gtkver_str = "%d.%d.%d" % (
                Gtk.get_major_version(),
                Gtk.get_minor_version(),
                Gtk.get_micro_version(),
            )
        except:  # any failure to 'get' the version
            gtkver_str = "unknown version"
    except (ImportError, ValueError):
        gtkver_str = "not found"
    # no DISPLAY is a RuntimeError in an older pygtk (e.g. 2.17 in Fedora 14)
    except RuntimeError:
        gtkver_str = "DISPLAY not set"
    # exept TypeError: To handle back formatting on version split

    try:
        from gi.repository import GObject

        try:
            pygobjectver_str = "%d.%d.%d" % GObject.pygobject_version
        except:  # any failure to 'get' the version
            pygobjectver_str = "unknown version"

    except ImportError:
        pygobjectver_str = "not found"

    try:
        from gi.repository import Pango

        try:
            pangover_str = Pango.version_string()
        except:  # any failure to 'get' the version
            pangover_str = "unknown version"

    except ImportError:
        pangover_str = "not found"

    try:
        import cairo

        try:
            pycairover_str = "%d.%d.%d" % cairo.version_info
            cairover_str = cairo.cairo_version_string()
        except:  # any failure to 'get' the version
            pycairover_str = "unknown version"
            cairover_str = "unknown version"

    except ImportError:
        pycairover_str = "not found"
        cairover_str = "not found"

    try:
        gi.require_version("PangoCairo", "1.0")
        from gi.repository import PangoCairo

        pangocairo_str = PangoCairo._version
    except ImportError:
        pangocairo_str = _("not found")

    try:
        from gi import Repository

        repository = Repository.get_default()
        if repository.enumerate_versions("OsmGpsMap"):
            import gi

            gi.require_version("OsmGpsMap", "1.0")
            from gi.repository import OsmGpsMap as osmgpsmap

            try:
                osmgpsmap_str = osmgpsmap._version
            except:  # any failure to 'get' the version
                osmgpsmap_str = "unknown version"
        else:
            osmgpsmap_str = "not found"

    except ImportError:
        osmgpsmap_str = "not found"

    try:
        import gi

        repository = gi.Repository.get_default()
        if repository.enumerate_versions("GExiv2"):
            gi.require_version("GExiv2", "0.10")
            from gi.repository import GExiv2

            try:
                gexiv2_str = GExiv2._version
            except:  # any failure to 'get' the version
                gexiv2_str = "unknown version"
        else:
            gexiv2_str = "not found"

    except ImportError:
        gexiv2_str = "not found"
    except ValueError:
        gexiv2_str = "not new enough"

    try:
        vers_str = Popen(["exiv2", "-V"], stdout=PIPE).communicate(input=None)[0]
        try:
            if isinstance(vers_str, bytes) and sys.stdin.encoding:
                vers_str = vers_str.decode(sys.stdin.encoding)
            indx = vers_str.find("exiv2 ") + 6
            vers_str = vers_str[indx : indx + 4]
        except Exception:
            vers_str = _("not found")

    except Exception:
        vers_str = _("not found because exiv2 is not installed")

    try:
        import PyICU

        try:
            pyicu_str = PyICU.VERSION
            icu_str = PyICU.ICU_VERSION
        except:  # any failure to 'get' the version
            pyicu_str = "unknown version"
            icu_str = "unknown version"

    except ImportError:
        pyicu_str = "not found"
        icu_str = "not found"

    try:
        import icu

        icu_str = icu.PY_VERSION
    except Exception:
        icu_str = _("not found")

    try:
        import PIL

        try:
            pil_ver = PIL.__version__
        except Exception:
            try:
                pil_ver = str(PIL.PILLOW_VERSION)
            except Exception:
                try:
                    # print(dir(PIL))
                    pil_ver = str(PIL.VERSION)
                except Exception:
                    pil_ver = _("Installed but does not supply version")
    except ImportError:
        pil_ver = _("not found")

    def verstr(nums):
        return ".".join(str(num) for num in nums)

    try:
        gi.require_version("Gspell", "1")
        from gi.repository import Gspell

        gspell_ver = str(Gspell._version)
    except Exception:
        gspell_ver = _("not found")

    # RCS_MIN_VER = (5, 9, 4)
    # rcs_ver_str = verstr(RCS_MIN_VER)
    # print("os.environ: %s " % os.environ)
    try:
        if win():
            _RCS_FOUND = os.system("rcs -V >nul 2>nul") == 0
            rcs_ver = _("installed")
            # print("rcs -V : " + os.system("rcs -V"))
            if _RCS_FOUND and "TZ" not in os.environ:
                # RCS requires the "TZ" variable be set.
                os.environ["TZ"] = str(time.timezone)
        else:
            import subprocess
            import re

            # print("xx rcs -V : " + os.system("rcs --version"))
            _RCS_FOUND = str(subprocess.check_output(["rcs", "--version"]))
            version = re.compile(r".*GNU RCS\) ([0-9]+\.[0-9]+\.[0-9]+).*")
            rcs_ver = version.findall(_RCS_FOUND)[0]
    except Exception:
        rcs_ver = _("not found")

    try:
        gi.require_version("GeocodeGlib", "1.0")
        from gi.repository import GeocodeGlib

        geocodeglib_ver = str(GeocodeGlib._version)
    except Exception:
        geocodeglib_ver = _("not found")

    try:
        import bsddb3 as bsddb

        bsddb_str = bsddb.__version__
        bsddb_db_str = (
            str(bsddb.db.version()).replace(", ", ".").replace("(", "").replace(")", "")
        )
        bsddb_location_str = bsddb.__file__
    except:
        try:
            import berkeleydb as bsddb

            bsddb_str = bsddb.__version__
            bsddb_db_str = (
                str(bsddb.db.version())
                .replace(", ", ".")
                .replace("(", "")
                .replace(")", "")
            )
            bsddb_location_str = bsddb.__file__
        except:
            bsddb_str = "not found"
            bsddb_db_str = "not found"
            bsddb_location_str = "not found"

    try:
        import sqlite3

        sqlite3_py_version_str = sqlite3.version
        sqlite3_version_str = sqlite3.sqlite_version
        sqlite3_location_str = sqlite3.__file__
    except:
        sqlite3_version_str = "not found"
        sqlite3_py_version_str = "not found"
        sqlite3_location_str = "not found"

    try:
        from .gen.const import VERSION

        gramps_str = VERSION
    except:
        gramps_str = "not found"

    if hasattr(os, "uname"):
        kernel = os.uname()[2]
    else:
        kernel = None

    lang_str = get_env_var("LANG", "not set")
    language_str = get_env_var("LANGUAGE", "not set")
    grampsi18n_str = get_env_var("GRAMPSI18N", "not set")
    grampshome_str = get_env_var("GRAMPSHOME", "not set")
    grampsdir_str = get_env_var("GRAMPSDIR", "not set")
    gramps_resources_str = get_env_var("GRAMPS_RESOURCES", "not set")

    try:
        dotversion_str = Popen(["dot", "-V"], stderr=PIPE).communicate(input=None)[1]
        if isinstance(dotversion_str, bytes) and sys.stdin.encoding:
            dotversion_str = dotversion_str.decode(sys.stdin.encoding)
        if dotversion_str:
            dotversion_str = dotversion_str.replace("\n", "")[23:27]
    except:
        dotversion_str = "Graphviz not in system PATH"

    try:
        if win():
            try:
                gsversion_str = Popen(
                    ["gswin32c", "--version"], stdout=PIPE
                ).communicate(input=None)[0]
            except:
                gsversion_str = Popen(
                    ["gswin64c", "--version"], stdout=PIPE
                ).communicate(input=None)[0]
        else:
            gsversion_str = Popen(["gs", "--version"], stdout=PIPE).communicate(
                input=None
            )[0]
        if isinstance(gsversion_str, bytes) and sys.stdin.encoding:
            gsversion_str = gsversion_str.decode(sys.stdin.encoding)
        if gsversion_str:
            gsversion_str = gsversion_str.replace("\n", "")
    except:
        gsversion_str = "Ghostscript not in system PATH"

    os_path = get_env_var("PATH", "not set")
    os_path = os_path.split(os.pathsep)

    print("Gramps Settings:")
    print("----------------")
    print(" gramps    : %s" % gramps_str)
    print(" o.s.      : %s" % sys.platform)
    if kernel:
        print(" kernel    : %s" % kernel)
    print("")
    print("Required:")
    print("---------")
    print(" Python    : %s" % py_str)
    print(" Gtk++     : %s" % gtkver_str)
    print(" pygobject : %s" % pygobjectver_str)
    print(" Cairo     : %s" % cairover_str)
    print(" pycairo   : %s" % pycairover_str)
    print(" Pango     : %s" % pangover_str)
    print(" PangoCairo: %s" % pangocairo_str)
    print("")
    print("Recommended:")
    print("------------")
    print(" osmgpsmap : %s" % osmgpsmap_str)
    print(" Graphviz  : %s" % dotversion_str)
    print(" Ghostscr. : %s" % gsversion_str)
    print(" ICU       : %s" % icu_str)
    print(" PyICU     : %s" % pyicu_str)
    print("")
    print("Optional:")
    print("---------")
    print(" Gspell     :", gspell_ver)
    print(" RCS        :", rcs_ver)
    print(" PILLOW     :", pil_ver)
    print(" GExiv2     : %s" % gexiv2_str)
    print(" Exiv2 lib. : %s" % vers_str)
    print(" geocodeglib: %s" % geocodeglib_ver)
    print("")
    print("Environment settings:")
    print("---------------------")
    print(" LANG      : %s" % lang_str)
    print(" LANGUAGE  : %s" % language_str)
    print(" GRAMPSI18N: %s" % grampsi18n_str)
    print(" GRAMPSHOME: %s" % grampshome_str)
    print(" GRAMPSDIR : %s" % grampsdir_str)
    if __debug__:
        print(" GRAMPS_RESOURCES : %s" % gramps_resources_str)
    print(" PYTHONPATH:")
    for folder in sys.path:
        print("   ", folder)
    print("")
    print("System PATH env variable:")
    print("-------------------------")
    for folder in os_path:
        print("    ", folder)
    print("")
    print("Databases:")
    print("-------------------------")
    print(" bsddb     :")
    print("     version     : %s" % bsddb_str)
    print("     db version  : %s" % bsddb_db_str)
    print("     location    : %s" % bsddb_location_str)
    print(" sqlite3   :")
    print("     version     : %s" % sqlite3_version_str)
    print("     py version  : %s" % sqlite3_py_version_str)
    print("     location    : %s" % sqlite3_location_str)
    print("")


def run():
    error = []

    try:
        build_user_paths()
    except OSError as msg:
        error += [(_("Configuration error:"), str(msg))]
        return error
    except msg:
        LOG.error("Could not read configuration.", exc_info=True)
        return [(_("Could not read configuration"), str(msg))]

    if not mime_type_is_defined(APP_GRAMPS):
        error += [
            (
                _("Configuration error:"),
                _(
                    "A definition for the media type %s could not "
                    "be found \n\n Possibly the installation of Gramps "
                    "was incomplete. Make sure something to handle the "
                    "media types of Gramps is installed."
                )
                % APP_GRAMPS,
            )
        ]

    # we start with parsing the arguments to determine if we have a cli or a
    # gui session

    if "-v" in sys.argv or "--version" in sys.argv:
        show_settings()
        return error

    from .cli.argparser import ArgParser

    argv_copy = sys.argv[:]
    argpars = ArgParser(argv_copy)

    # if in safe mode we should point the db dir back to the original dir.
    # It is ok to import config here, 'Defaults' command had its chance...
    if "SAFEMODE" in os.environ:
        config.set("database.path", os.path.join(ORIG_HOME_DIR, "grampsdb"))

    # On windows the fontconfig handler is a better choice
    if win() and ("PANGOCAIRO_BACKEND" not in os.environ):
        os.environ["PANGOCAIRO_BACKEND"] = "fontconfig"

    # Calls to LOG must be after setup_logging() and ArgParser()
    LOG = logging.getLogger(".locale")
    LOG.debug("Encoding: %s", glocale.encoding)
    LOG.debug("Translating Gramps to %s", glocale.language[0])
    LOG.debug("Collation Locale: %s", glocale.collation)
    LOG.debug("Date/Time Locale: %s", glocale.calendar)

    if "LANG" in os.environ:
        LOG.debug("Using LANG: %s" % get_env_var("LANG"))
    else:
        LOG.debug("environment: LANG is not defined")
    if "LANGUAGE" in os.environ:
        LOG.debug("Using LANGUAGE: %s" % get_env_var("LANGUAGE"))
    else:
        LOG.debug("environment: LANGUAGE is not defined")

    if argpars.need_gui():
        LOG.debug("A GUI is needed. Set one up.")
        try:
            from .gui.grampsgui import startgramps

            # no DISPLAY is a RuntimeError in an older pygtk (e.g. 2.17 in Fedora 14)
        except RuntimeError as msg:
            error += [(_("Configuration error:"), str(msg))]
            return error
        startgramps(error, argpars)
    else:
        # CLI use of Gramps
        argpars.print_help()
        argpars.print_usage()
        from .cli.grampscli import startcli

        startcli(error, argpars)


def main():
    if "GRAMPS_RESOURCES" not in os.environ:
        resource_path, filename = os.path.split(os.path.abspath(__file__))
        resource_path, dirname = os.path.split(resource_path)
        os.environ["GRAMPS_RESOURCES"] = resource_path
    errors = run()
    if errors and isinstance(errors, list):
        for error in errors:
            logging.warning(error[0] + error[1])

    sys.stdout.close()
    sys.stderr.close()


if __name__ == "__main__":
    main()
