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


# es
plg = newplugin()
plg.id = "nameguesser_es"
plg.name = _("Spanish Name Guesser")
plg.description = _("Guesses names when adding a person")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "nameguesser_es.py"
plg.ptype = NAMEGUESSER
plg.nameguesserclass = "NameGuesser"
plg.lang_list = [
    "es",
    "ES",
    "es_ES",
    "espanol",
    "Espanol",
    "es_ES.UTF8",
    "es_ES@euro",
    "es_ES.UTF8@euro",
    "spanish",
    "Spanish",
    "es_ES.UTF-8",
    "es_ES.utf-8",
    "es_ES.utf8",
]

# is
plg = newplugin()
plg.id = "nameguesser_is"
plg.name = _("Icelandic Name Guesser")
plg.description = _("Guesses names when adding a person")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "nameguesser_is.py"
plg.ptype = NAMEGUESSER
plg.nameguesserclass = "NameGuesser"
plg.lang_list = ["is", "IS", "is_IS", "is_IS@euro", "is_IS.utf8"]


# pt
plg = newplugin()
plg.id = "nameguesser_pt"
plg.name = _("Portuguese Name Guesser")
plg.description = _("Guesses names when adding a person")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "nameguesser_pt.py"
plg.ptype = NAMEGUESSER
plg.nameguesserclass = "NameGuesser"
plg.lang_list = [
    "pt",
    "PT",
    "pt_PT",
    "pt_BR",
    "portugues",
    "Portugues",
    "pt_PT.UTF8",
    "pt_BR.UTF8",
    "pt_PT@euro",
    "pt_PT.UTF8@euro",
    "pt_PT.UTF-8",
    "pt_BR.UTF-8",
    "pt_PT.utf-8",
    "pt_BR.utf-8",
    "pt_PT.utf8",
    "pt_BR.utf8",
]
