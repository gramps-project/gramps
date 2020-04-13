# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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
from gramps.gen.plug._pluginreg import newplugin, STABLE, RELCALC
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

MODULE_VERSION="5.2"

#
# Relationship calculators
#

# ca
plg = newplugin()
plg.id = 'relcalc_ca'
plg.name = _("Catalan Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_ca.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
## TODO PYTHON 3: does this third entry work?
plg.lang_list = ['ca_ES', 'ca', 'català', 'Catalan', 'ca_FR', 'ca_AD', 'ca_IT']

# cs
plg = newplugin()
plg.id = 'relcalc_cs'
plg.name = _("Czech Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_cs.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["cs", "CZ", "cs_CZ", "česky", "czech", "Czech", "cs_CZ.UTF8", "cs_CZ.UTF-8",                   "cs_CZ.utf-8", "cs_CZ.utf8"]

# da
plg = newplugin()
plg.id = 'relcalc_da'
plg.name = _("Danish Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_da.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = [ "da", "DA", "da_DK", "danish", "Danish", "da_DK.UTF8",
      "da_DK@euro", "da_DK.UTF8@euro", "dansk", "Dansk",
      "da_DK.UTF-8", "da_DK.utf-8", "da_DK.utf8",
      "da_DK.ISO-8859-1","da_DK.iso-8859-1","da_DK.iso88591" ]

# de
plg = newplugin()
plg.id = 'relcalc_de'
plg.name = _("German Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_de.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["de", "DE", "de_DE", "deutsch", "Deutsch", "de_DE.UTF8",
                 "de_DE@euro", "de_DE.UTF8@euro", "de_AT.UTF-8", "de_AT.utf-8",
                 "de_AT.utf8", "german","German", "de_DE.UTF-8", "de_DE.utf-8",
                 "de_DE.utf8", "de_CH.UTF-8", "de_CH.utf-8", "de_CH.utf8"]

# es
plg = newplugin()
plg.id = 'relcalc_es'
plg.name = _("Spanish Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_es.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["es", "ES", "es_ES", "espanol", "Espanol", "es_ES.UTF8",
                  "es_ES@euro", "es_ES.UTF8@euro", "spanish", "Spanish",
                  "es_ES.UTF-8", "es_ES.utf-8", "es_ES.utf8"]

# fi
plg = newplugin()
plg.id = 'relcalc_fi'
plg.name = _("Finnish Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_fi.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["fi", "FI", "fi_FI", "finnish", "Finnish", "fi_FI.UTF8",
                 "fi_FI@euro", "fi_FI.UTF8@euro", "suomi", "Suomi",
                 "fi_FI.UTF-8", "fi_FI.utf-8", "fi_FI.utf8"]

# fr
plg = newplugin()
plg.id = 'relcalc_fr'
plg.name = _("French Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_fr.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["fr", "FR", "fr_FR", "fr_CA", "français",
                 "Français", "fr_FR.UTF8", "fr_FR@euro",
                 "fr_FR.UTF8@euro", "french", "French",
                 "fr_FR.UTF-8", "fr_FR.utf-8", "fr_FR.utf8",
                 "fr_CA.UTF-8", "Français_France"]

# hr
plg = newplugin()
plg.id = 'relcalc_hr'
plg.name = _("Croatian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_hr.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["hrvatski", "Hrvatski", "croatian", "Croatian", "hr", "HR",
                 "hr_HR", "hr_HR.UTF-8", "hr_HR.utf-8", "Croatian_Croatia"]

# hu
plg = newplugin()
plg.id = 'relcalc_hu'
plg.name = _("Hungarian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_hu.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["hu", "HU", "hu_HU", "hu_HU.utf8", "hu_HU.UTF8"]

# is
plg = newplugin()
plg.id = 'relcalc_is'
plg.name = _("Icelandic Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_is.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["is", "IS", "is_IS", "is_IS@euro", "is_IS.utf8"]

# it
plg = newplugin()
plg.id = 'relcalc_it'
plg.name = _("Italian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_it.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["it", "IT", "it_IT", "it_IT@euro", "it_IT.utf8"]

# nl
plg = newplugin()
plg.id = 'relcalc_nl'
plg.name = _("Dutch Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_nl.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["nl", "NL", "nl_NL", "nl_BE", "nederlands", "Nederlands",
                 "nl_NL.UTF8", "nl_BE.UTF8","nl_NL@euro", "nl_NL.UTF8@euro",
                 "nl_BE@euro", "dutch", "Dutch", "nl_NL.UTF-8",
                 "nl_BE.UTF-8", "nl_NL.utf-8", "nl_BE.utf-8","nl_NL.utf8",
                 "nl_BE.UTF-8", "nl_BE.UTF8@euro"]

# no
plg = newplugin()
plg.id = 'relcalc_no'
plg.name = _("Norwegian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_no.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["nb", "nn", "no", "nb_NO", "nn_NO", "no_NO", "nb_NO.UTF8",
                 "nn_NO.UTF8", "no_NO.UTF8", "nb_NO.UTF-8", "nn_NO.UTF-8",
                 "no_NO.UTF-8", "nb_NO.utf-8", "nn_NO.utf-8", "no_NO.utf-8",
                 "nb_NO.iso88591", "nn_NO.iso88591", "no_NO.iso88591",
                 "nynorsk", "Nynorsk"]

# pl
plg = newplugin()
plg.id = 'relcalc_pl'
plg.name = _("Polish Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_pl.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["pl", "PL", "pl_PL", "polski", "Polski",
                 "pl_PL.UTF-8", "pl_PL.UTF8", "pl_PL.utf-8", "pl_PL.utf8",
                 "pl_PL.iso-8859-2", "pl_PL.iso8859-2",
                 "pl_PL.cp1250", "pl_PL.cp-1250"]

# pt
plg = newplugin()
plg.id = 'relcalc_pt'
plg.name = _("Portuguese Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_pt.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["pt", "PT", "pt_PT", "pt_BR", "portugues", "Portugues",
                 "pt_PT.UTF8", "pt_BR.UTF8", "pt_PT@euro", "pt_PT.UTF8@euro",
                 "pt_PT.UTF-8", "pt_BR.UTF-8", "pt_PT.utf-8", "pt_BR.utf-8",
                 "pt_PT.utf8","pt_BR.utf8"]

# ru
plg = newplugin()
plg.id = 'relcalc_ru'
plg.name = _("Russian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_ru.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["ru", "RU", "ru_RU", "koi8r", "ru_koi8r", "russian",
                 "Russian", "ru_RU.koi8r", "ru_RU.KOI8-R", "ru_RU.utf8",
                 "ru_RU.UTF8", "ru_RU.utf-8", "ru_RU.UTF-8", "ru_RU.iso88595",
                 "ru_RU.iso8859-5", "ru_RU.iso-8859-5"]

# sk
plg = newplugin()
plg.id = 'relcalc_sk'
plg.name = _("Slovak Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_sk.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["sk", "SK", "sk_SK", "slovensky", "slovak", "Slovak",
                 "sk_SK.UTF8", "sk_SK.UTF-8", "sk_SK.utf-8", "sk_SK.utf8"]

# sl
plg = newplugin()
plg.id = 'relcalc_sl'
plg.name = _("Slovenian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_sl.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["sl", "SL", "sl_SI", "slovenščina", "slovenian", "Slovenian",
                 "sl_SI.UTF8", "sl_SI.UTF-8", "sl_SI.utf-8", "sl_SI.utf8"]
# sv
plg = newplugin()
plg.id = 'relcalc_sv'
plg.name = _("Swedish Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_sv.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["sv", "SV", "sv_SE", "swedish", "Swedish", "sv_SE.UTF8",
                 "sv_SE@euro", "sv_SE.UTF8@euro", "svenska", "Svenska",
                 "sv_SE.UTF-8", "sv_SE.utf-8", "sv_SE.utf8", "Swedish_Sweden"]
# uk
plg = newplugin()
plg.id = 'relcalc_uk'
plg.name = _("Ukrainian Relationship Calculator")
plg.description = _("Calculates relationships between people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rel_uk.py'
plg.ptype = RELCALC
plg.relcalcclass = 'RelationshipCalculator'
plg.lang_list = ["uk", "UA", "uk_UA", "ukrainian",
                 "Ukrainian", "uk_UA.utf8",
                 "uk_UA.UTF8", "uk_UA.utf-8", "uk_UA.UTF-8", "uk_UA.iso88595",
                 "uk_UA.iso8859-5", "uk_UA.iso-8859-5", "koi8u", "uk_koi8u",
                 "uk_UA.koi8u","uk_UA.KOI8-U",]
