from gramps.gen.plug._pluginreg import newplugin, STABLE, NAMEGUESSER
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "6.0"

# de
plg = newplugin()
plg.id = "nameguesser_de"
plg.name = _("German Name Guesser")
plg.description = _("Guesses names when adding a person")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "nameguesser_de.py"
plg.ptype = NAMEGUESSER
plg.nameguesserclass = "NameGuesser"
plg.lang_list = [
    "de",
    "DE",
    "deutsch",
    "Deutsch",
    "de_DE.UTF8",
    "de_DE@euro",
    "de_DE.UTF8@euro",
    "german",
    "German",
    "de_DE",
    "de_DE.UTF-8",
    "de_DE.utf-8",
    "de_DE.utf8",
    "de_CH",
    "de_CH.UTF-8",
    "de_CH.utf-8",
    "de_CH.utf8",
    "de_AT",
    "de_AT.UTF-8",
    "de_AT.utf-8",
    "de_AT.utf8",
    "de_AT.UTF8",
]