#!/usr/bin/env python
import sys, os, subprocess

_home = os.environ["HOME"]
_res_path = os.path.normpath(os.path.join(sys.path[0], "..", "Resources"))
_lib_path = os.path.join(_res_path, "lib")
_share_path = os.path.join(_res_path, "share")
_pylib_path = os.path.join(_lib_path, "python2.6")
_site_lib_path = os.path.join(_pylib_path, "site-packages")
_gramps_path = os.path.join(_share_path, "gramps")
_gramps_locale = os.path.join(_share_path, "locale")
_conf_path = os.path.join(_res_path, "etc");
_gtk2_conf = os.path.join(_conf_path, "gtk-2.0")
sys.path = [_gramps_path,
            os.path.join(_pylib_path, "lib-dynload"),
            os.path.join(_site_lib_path, "pyenchant-1.6.1-py2.6.egg"),
            os.path.join(_site_lib_path, "gtk-2.0"),
            _site_lib_path,
            _pylib_path]

sys.prefix = _res_path
os.environ["XDG_DATA_DIRS"]=_share_path
os.environ["DYLD_LIBRARY_PATH"]=_lib_path
os.environ["LD_LIBRARY_PATH"]=_lib_path
os.environ["GTK_PATH"] = _res_path
os.environ["GTK2_RC_FILES"] = os.path.join(_gtk2_conf, "gtkrc")
os.environ["GTK_IM_MODULE_FILE"]= os.path.join(_gtk2_conf, "immodules")
os.environ["GDK_PIXBUF_LOADERS"] = os.path.join(_gtk2_conf, "gdk-pixbuf.loaders")
os.environ["PANGO_RC_FILES"] = os.path.join(_conf_path, "pango", "pangorc")

os.environ["GRAMPSDIR"] = _gramps_path
os.environ["GRAMPSI18N"] = _gramps_locale
os.environ["GRAMPSHOME"] = os.path.join(_home, "Library", "Application Support")

LANG = "C" #Default
defaults = "/usr/bin/defaults"
_languages = ""
_collation = ""
_locale = ""
_language = ""
LC_COLLATE = ""
try:
    _languages = subprocess.Popen(
        [defaults,  "read", "-app", "Gramps", "AppleLanguages"],
        stderr=open("/dev/null"),
        stdout=subprocess.PIPE).communicate()[0].strip("()\n").split(",\n")
except:
    pass
if not _languages:
    try:
        _languages = subprocess.Popen(
            [defaults, "read", "-g", "AppleLanguages"],
            stderr=open("/dev/null"),
            stdout=subprocess.PIPE).communicate()[0].strip("()\n").split(",\n")
    except:
        pass

for _lang in _languages:
    _lang=_lang.strip().strip('"').replace("-", "_", 1)
    if _lang == "cn_Hant": #Traditional; Gettext uses cn_TW
        _lang = "cn_TW"
    if _lang == "cn_Hans": #Simplified; Gettext uses cn_CN
        _lang = "cn_CN"
    _language = _lang
    if _lang.startswith("en"): #Gramps doesn't have explicit English translation, use C
        break
    if os.path.exists(os.path.join(_gramps_locale, _lang, "LC_MESSAGES",
                                   "gramps.mo")):
        LANG = _lang
        break
    elif os.path.exists(os.path.join(_gramps_locale, _lang[:2], "LC_MESSAGES",
                                     "gramps.mo")):
        LANG = _lang[:2]
        break
try:
    _collation=subprocess.Popen(
        [defaults, "read", "-app", "Gramps", "AppleCollationOrder"],
        stderr=open("/dev/null"),
        stdout=subprocess.PIPE).communicate()[0]
except:
    pass
if not _collation:
    try:
        _collation=subprocess.Popen(
            [defaults, "read", "-g", "AppleCollationOrder"],
            stderr=open("/dev/null"),
            stdout=subprocess.PIPE).communicate()[0]
    except:
        pass
if _collation:
    if LANG == "C" and not _language and os.path.exists(os.path.join(_gramps_locale, _collation,
                                                   "LC_MESSAGES", "gramps.mo")):
        LANG = _collation
    LC_COLLATE = _collation
if LANG == "C" and not _language:
    try:
        _locale=subprocess.Popen(
            [defaults, "read", "-app", "Gramps", "AppleLocale"],
            stderr=open("/dev/null"),
            stdout=subprocess.PIPE).communicate()[0]
    except:
        pass
    if not _locale:
        try:
            _locale=subprocess.Popen(
                [defaults, "read", "-g", "AppleLocale"],
                stderr=open("/dev/null"),
                stdout=subprocess.PIPE).communicate()[0]
        except:
            pass
    if _locale:
        if os.path.exists(os.path.join(_gramps_locale, _locale[:5],
                                       "LC_MESSAGES", "gramps.mo")):
            LANG = _locale[:5]
        elif os.path.exists(os.path.join(_gramps_locale, _locale[:2],
                                         "LC_MESSAGES", "gramps.mo")):
            LANG = _locale[:2]

os.environ["LANG"] = LANG
if not _language:
    _language = LANG
if LC_COLLATE:
    os.environ["LC_COLLATE"] = LC_COLLATE
if _language == "C" or _language == "en":
    LC_ALL = "en_US"
elif len(_language) == 2:
    LC_ALL = _language + "_" + _language.upper() #Because setlocale gets cranky
                                       #if it only has two letters
else:
    LC_ALL = _language

os.environ["LC_ALL"] = LC_ALL #Spell-checker dictionary support

#LaunchServices sticks this argument on the front of argument
#lists. It must make sense to somebody, but Gramps isn't that
#somebody.
for _arg in sys.argv:
    if _arg.startswith("-psn"):
        sys.argv.remove(_arg)
import gramps
