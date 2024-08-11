# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010-      Serge Noiraud
# Copyright (C) 2021-      T G L Lyons
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
Narrative Web Page generator.

Class:
    AlphabeticIndex - approximate emulation of ICU Alphabetic Index
"""

# ------------------------------------------------
# python modules
# ------------------------------------------------
from unicodedata import normalize
from collections import defaultdict
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

HAVE_ICU = False
try:
    from icu import Locale, Collator

    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Locale, Collator

        HAVE_ICU = True
    except ImportError:
        pass

LOG = logging.getLogger(".NarrativeWeb")
COLLATE_LANG = glocale.collation


class U_ENUM_OUT_OF_SYNC_ERROR(Exception):  # pylint: disable=invalid-name
    """
    Exception to match the error in the ICU AlphabetiIndex
    """

    pass


# See : http://www.gramps-project.org/bugs/view.php?id = 4423

# Contraction data taken from CLDR 22.1. Only the default variant is considered.
# The languages included below are, by no means, all the langauges that have
# contractions - just a sample of langauges that have been supported

# At the time of writing (Feb 2013), the following langauges have greater that
# 50% coverage of translation of Gramps: bg Bulgarian, ca Catalan, cs Czech, da
# Danish, de German, el Greek, en_GB, es Spanish, fi Finish, fr French, he
# Hebrew, hr Croation, hu Hungarian, it Italian, ja Japanese, lt Lithuanian, nb
# Noregian Bokmål, nn Norwegian Nynorsk, nl Dutch, pl Polish, pt_BR Portuguese
# (Brazil), pt_P Portugeuse (Portugal), ru Russian, sk Slovak, sl Slovenian, sv
# Swedish, vi Vietnamese, zh_CN Chinese.

# Key is the language (or language and country), Value is a list of
# contractions. Each contraction consists of a tuple. First element of the
# tuple is the list of characters, second element is the string to use as the
# index entry.

# The DUCET contractions (e.g. LATIN CAPIAL LETTER L, MIDDLE DOT) are ignored,
# as are the supresscontractions in some locales.

CONTRACTIONS_DICT = {
    # bg Bulgarian validSubLocales="bg_BG" no contractions
    # ca Catalan validSubLocales="ca_AD ca_ES"
    "ca": [(("l·", "L·"), "L")],
    # Czech, validSubLocales="cs_CZ" Czech_Czech Republic
    "cs": [(("ch", "cH", "Ch", "CH"), "CH")],
    # Danish validSubLocales="da_DK" Danish_Denmark
    "da": [(("aa", "Aa", "AA"), "Å")],
    # de German validSubLocales="de_AT de_BE de_CH de_DE de_LI de_LU" no
    # contractions in standard collation.
    # el Greek validSubLocales="el_CY el_GR" no contractions.
    # es Spanish validSubLocales="es_419 es_AR es_BO es_CL es_CO es_CR es_CU
    # es_DO es_EA es_EC es_ES es_GQ es_GT es_HN es_IC es_MX es_NI es_PA es_PE
    # es_PH es_PR es_PY es_SV es_US es_UY es_VE" no contractions in standard
    # collation.
    # fi Finish validSubLocales="fi_FI" no contractions in default (phonebook)
    # collation.
    # fr French no collation data.
    # he Hebrew validSubLocales="he_IL" no contractions
    # hr Croation validSubLocales="hr_BA hr_HR"
    "hr": [
        (("dž", "Dž", "DŽ"), "DŽ"),
        (("lj", "Lj", "LJ"), "Ǉ"),
        (("Nj", "NJ", "nj"), "Ǌ"),
    ],
    # Hungarian hu_HU for two and three character contractions.
    "hu": [
        (("cs", "Cs", "CS"), "CS"),
        (("dzs", "Dzs", "DZS"), "DZS"),  # order is important
        (("dz", "Dz", "DZ"), "DZ"),
        (("gy", "Gy", "GY"), "GY"),
        (("ly", "Ly", "LY"), "LY"),
        (("ny", "Ny", "NY"), "NY"),
        (("sz", "Sz", "SZ"), "SZ"),
        (("ty", "Ty", "TY"), "TY"),
        (("zs", "Zs", "ZS"), "ZS"),
    ],
    # it Italian no collation data.
    # ja Japanese unable to process the data as it is too complex.
    # lt Lithuanian no contractions.
    # Norwegian Bokmål
    "nb": [(("aa", "Aa", "AA"), "Å")],
    # nn Norwegian Nynorsk validSubLocales="nn_NO"
    "nn": [(("aa", "Aa", "AA"), "Å")],
    # nl Dutch no collation data.
    # pl Polish validSubLocales="pl_PL" no contractions
    # pt Portuguese no collation data.
    # ru Russian validSubLocales="ru_BY ru_KG ru_KZ ru_MD ru_RU ru_UA" no
    # contractions
    # Slovak,  validSubLocales="sk_SK" Slovak_Slovakia
    # having DZ in Slovak as a contraction was rejected in
    # http://unicode.org/cldr/trac/ticket/2968
    "sk": [(("ch", "cH", "Ch", "CH"), "Ch")],
    # sl Slovenian validSubLocales="sl_SI" no contractions
    # sv Swedish validSubLocales="sv_AX sv_FI sv_SE" default collation is
    # "reformed" no contractions.
    # vi Vietnamese validSubLocales="vi_VN" no contractions.
    # zh Chinese validSubLocales="zh_Hans zh_Hans_CN zh_Hans_SG" no contractions
    # in Latin characters the others are too complex.
}

# The comment below from the glibc locale sv_SE in
# localedata/locales/sv_SE :
#
# % The letter w is normally not present in the Swedish alphabet. It
# % exists in some names in Swedish and foreign words, but is accounted
# % for as a variant of 'v'.  Words and names with 'w' are in Swedish
# % ordered alphabetically among the words and names with 'v'. If two
# % words or names are only to be distinguished by 'v' or % 'w', 'v' is
# % placed before 'w'.
#
# See : http://www.gramps-project.org/bugs/view.php?id = 2933
#

# HOWEVER: the characters V and W in Swedish are not considered as a special
# case for several reasons. (1) The default collation for Swedish (called the
# 'reformed' collation type) regards the difference between 'v' and 'w' as a
# primary difference. (2) 'v' and 'w' in the 'standard' (non-default) collation
# type are not a contraction, just a case where the difference is secondary
# rather than primary. (3) There are plenty of other languages where a
# difference that is primary in other languages is secondary, and those are not
# specially handled.


def first_letter(string, rlocale=glocale):
    """
    Receives a string and returns the first letter
    """
    if string is None or len(string) < 1:
        return " "

    norm_unicode = normalize("NFKC", str(string))
    contractions = CONTRACTIONS_DICT.get(rlocale.collation)
    if contractions is None:
        contractions = CONTRACTIONS_DICT.get(rlocale.collation.split("_")[0])

    if contractions is not None:
        for contraction in contractions:
            count = len(contraction[0][0])
            if len(norm_unicode) >= count and norm_unicode[:count] in contraction[0]:
                return contraction[1]

    # no special case
    return norm_unicode[0].upper()


if HAVE_ICU:

    def primary_difference(prev_key, new_key, rlocale=glocale):
        """
        Try to use the PyICU collation.
        If we generate a report for another language, make sure we use the good
        collation sequence
        """
        collate_lang = Locale(rlocale.collation)
        collation = Collator.createInstance(collate_lang)
        collation.setStrength(Collator.PRIMARY)
        return collation.compare(prev_key, new_key) != 0

else:

    def primary_difference(prev_key, new_key, rlocale=glocale):
        """
        The PyICU collation is not available.

        Returns true if there is a primary difference between the two parameters
        See http://www.gramps-project.org/bugs/view.php?id=2933#c9317 if
        letter[i]+'a' < letter[i+1]+'b' and letter[i+1]+'a' < letter[i]+'b' is
        true then the letters should be grouped together

        The test characters here must not be any that are used in contractions.
        """

        return rlocale.sort_key(prev_key + "e") >= rlocale.sort_key(
            new_key + "f"
        ) or rlocale.sort_key(new_key + "e") >= rlocale.sort_key(prev_key + "f")


def get_index_letter(letter, index_list, rlocale=glocale):
    """
    This finds the letter in the index_list that has no primary difference from
    the letter provided. See the discussion in get_first_letters above.
    Continuing the example, if letter is Å and index_list is A, then this would
    return A.

    @param: letter     -- The letter to find in the index_list
    @param: index_list -- The list of all first letters in use
    @param: rlocale    -- The locale to use
    """
    for index in index_list:
        if not primary_difference(letter, index, rlocale):
            return index

    LOG.warning("Initial letter '%s' not found in alphabetic navigation list", letter)
    LOG.debug("filtered sorted index list %s", index_list)
    return letter


# ------------------------------------------------------------
#
# AlphabeticIndex (local non-ICU version)
#
# ------------------------------------------------------------
class AlphabeticIndex:
    """
    Approximately emulate the ICU AlphabeticIndex
    """

    def __init__(self, rlocale):
        self.rlocale = rlocale
        self._record_list = []
        # self.index_list = []

        self._bucket_list = []
        self._dirty = False
        self._bucket = -1
        self._record = -1
        # Externally available properties
        self.bucketLabel = ""  # pylint: disable=invalid-name
        self.recordName = ""  # pylint: disable=invalid-name
        self.recordData = ""  # pylint: disable=invalid-name
        self.bucketRecordCount = 0  # pylint: disable=invalid-name

    def __create_index(self):
        """
        Internal routine to create the Alphabetic Index
        """
        # The first letter (or letters if there is a contraction) are extracted
        # from all the records in the _record_list. There may be duplicates, and
        # there may be letters where there is only a secondary or tertiary
        # difference, not a primary difference.
        index_list = []
        for name, dummy_data in self._record_list:
            ltr = first_letter(name, self.rlocale)
            index_list.append(ltr)
        # The list is sorted in collation order.
        index_list.sort(key=self.rlocale.sort_key)
        # For each group with secondary or tertiary differences, the first in
        # collation sequence is retained. For example, assume the default
        # collation sequence (DUCET) and names Ånström and Apple. These will
        # sort in the order shown. Å and A have a secondary difference. If the
        # first letter from these names was chosen then the index entry would be
        # Å. This is not desirable. Instead, the initial letters are extracted
        # (Å and A). These are sorted, which gives A and Å. Then the first of
        # these is used for the index entry.

        # now remove letters where there is not a primary difference
        first = True
        prev_index = None
        for nkey in index_list[:]:
            # iterate over a slice copy
            if first or primary_difference(prev_index, nkey, self.rlocale):
                first = False
                prev_index = nkey
            else:
                index_list.remove(nkey)

        # finally construct the buckets and contents
        bucket_dict = defaultdict(list)
        for name, data in sorted(
            self._record_list, key=lambda x: self.rlocale.sort_key(x[0])
        ):
            letter = first_letter(name, self.rlocale)
            letter = get_index_letter(letter, index_list, self.rlocale)
            bucket_dict[letter].append((name, data))

        self._bucket_list = sorted(
            bucket_dict.items(), key=lambda x: self.rlocale.sort_key(x[0])
        )

        self._dirty = False

    def addRecord(self, name, data):  # pylint: disable=invalid-name
        """
        Add a record to the index.

        Each record will be associated with an index Bucket based on the
        record's name. The list of records for each bucket will be sorted
        based on the collation ordering of the names in the index's locale.
        Records with duplicate names are permitted; they will be kept in the
        order that they were added.

        @param: name        --  The display name
                                for the Record. The Record will be placed in
                                a bucket based on this name.
        @param: data        --  An optional pointer to user data associated
                                with this item. When iterating the contents
                                of a bucket, both the data pointer the name
                                will be available for each Record.
        """
        self._record_list.append((name, data))
        self._dirty = True

    def resetBucketIterator(self):  # pylint: disable=invalid-name
        """
        Reset the Bucket iteration for this index.

        The next call to nextBucket() will restart the iteration at the
        first label.
        """
        if self._dirty:
            self.__create_index()
        self._bucket = -1
        self.bucketLabel = ""
        self._record = -1
        self.recordName = ""
        self.recordData = ""

    def nextBucket(self):  # pylint: disable=invalid-name
        """
        Advance the iteration over the Buckets of this index.

        Return false if there are no more Buckets.
        """
        if self._dirty:
            raise U_ENUM_OUT_OF_SYNC_ERROR
        self._bucket += 1
        self._record = -1
        if self._bucket < len(self._bucket_list):
            self.bucketLabel = self._bucket_list[self._bucket][0]
            self.bucketRecordCount = len(self._bucket_list[self._bucket][1])
            self.recordName = ""
            self.recordData = None
            return True
        else:
            return False

    def nextRecord(self):  # pylint: disable=invalid-name
        """
        Advance to the next record in the current Bucket.

        When nextBucket() is called, Record iteration is reset to just
        before the first Record in the new Bucket.
        """
        if self._dirty:
            raise U_ENUM_OUT_OF_SYNC_ERROR
        self._record += 1
        if self._record < len(self._bucket_list[self._bucket][1]):
            curr_bucket = self._bucket_list[self._bucket]
            bucket_value = curr_bucket[1]
            curr_record = bucket_value[self._record]
            self.recordName = curr_record[0]
            self.recordData = curr_record[1]
            return True
        else:
            self.recordName = ""
            self.recordData = None
            return False
