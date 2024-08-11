# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023       John Ralls
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
GrampsTranslations encapsulates Gettext behavior, allowing for a primary
language binding for the user interface and user-invoked language bindings
for reports so that they can be created in a different language from the UI's.
"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import gettext
import collections
import inspect


# -------------------------------------------------------------------------
#
# Translations Classes
#
# -------------------------------------------------------------------------
class Lexeme(str):
    r"""
    Created with :meth:`~GrampsTranslations.lexgettext`

    .. rubric:: Example

    Python code::

        _ = lexgettext
        dec = _("|December", "localized lexeme inflections")
        xmas = _("|Christmas", "lexeme")
        text = _("{holiday} is celebrated in {month}".format(
                    holiday=xmas, month=dec))
        greeting = _("Merry {holiday}!").format(holiday=xmas)
        XMAS = xmas.upper()
        print ("\n".join([XMAS, text, greeting]))

    Translation database (Russian example)::

        msgctxt "localized lexeme inflections"
        msgid "|December"
        msgstr "NOMINATIVE=декабрь|GENITIVE=декабря|ABLATIVE=декабрём|"
        "LOCATIVE=декабре"

        msgctxt "lexeme"
        msgid "|Christmas"
        msgstr "NOMINATIVE=рождество|GENITIVE=рождества|ABLATIVE=рождеством"

        msgid "{holiday} is celebrated in {month}"
        msgstr "{holiday} празднуют в {month.forms[LOCATIVE]}"

        msgid "Merry {holiday}!"
        msgstr "Счастливого {holiday.forms[GENITIVE]}!"

    Prints out::

        In English locale:
            CHRISTMAS
            Christmas is celebrated in December
            Merry Christmas!

        In Russian locale:
            РОЖДЕСТВО
            рождество празднуют в декабре
            Счастливого рождества!

    .. rubric:: Description

    Stores an arbitrary number of forms, e.g., inflections.
    These forms are accessible under dictionary keys for each form.
    The names of the forms are language-specific. They are assigned
    by the human translator of the corresponding language (in XX.po)
    as in the example above,
    see :meth:`~GrampsTranslations.lexgettext` docs
    for more info.

    The translated format string can then refer to a specific form
    of the lexeme using ``.``:attr:`~Lexeme.forms` and square brackets:
    ``{holiday.forms[GENITIVE]}``
    expects holiday to be a Lexeme which has a form ``'GENITIVE'`` in it.

    An instance of Lexeme can also be used as a regular unicode string.
    In this case, the work will be delegated to the string for the very
    first form provided in the translated string. In the example above,
    ``{holiday}`` in the translated string will expand to the Russian
    nominative form for Christmas, and ``xmas.upper()`` will produce
    the same nominative form in capital letters.

    .. rubric:: Motivation

    Lexeme is the term used in linguistics for the set of forms taken
    by a particular word, e.g. cases for a noun or tenses for a verb.

    Gramps often needs to compose sentences from several blocks of
    text and single words, often by using python string formatting.

    For instance, formatting a date range is done similarly to this::

        _("Between {startdate_month} {startdate_year}"
              "and {enddate_month} {enddate_year}").format(
                 startdate_month = m1,
                 startdate_year = y1,
                 enddate_month = m2,
                 enddate_year = y2)

    To make such text translatable, the arguments injected into
    format string need to bear all the linguistical information
    on how to plug them into a sentence, i.e., the forms, depending
    on the linguistic context of where the argument appears.
    The format string needs to select the relevant linguistic form.
    This is why ``m1`` and ``m2`` are instances of :class:`~Lexeme`.

    On the other hand, for languages where there is no linguistic
    variation in such sentences, the code needs not to be aware of
    the underlying :class:`~Lexeme` complexity;
    and so they can be processed just like simple strings
    both when passed around in the code and when formatted.
    """

    def __new__(cls, iterable, *args, **kwargs):
        if isinstance(iterable, str):
            newobj = str.__new__(cls, iterable, *args, **kwargs)
        else:
            forms = collections.OrderedDict(iterable)
            values = list(forms.values()) or [""]
            newobj = str.__new__(cls, values[0], *args, **kwargs)
            newobj._forms = forms
        return newobj

    def variants(self):
        """All lexeme forms, in the same order as given upon construction.
        The first one returned is the default form, which is used when the
        Lexeme instance is used in lieu of a string object.

        Same as ``f.values()``"""
        return self._forms.values()

    @property
    def forms(self):
        """Dictionary of the lexeme forms"""
        return self._forms


class GrampsTranslations(gettext.GNUTranslations):
    """
    Overrides and extends gettext.GNUTranslations. See the Python gettext
    "Class API" documentation for how to use this.
    """

    CONTEXT = "%s\x04%s"

    def __init__(self, fp=None):
        super().__init__(fp)
        self.lang = None

    def language(self):
        """
        Return the target languge of this translations object.
        """
        return self.lang

    def gettext(self, msgid, context=""):
        """
        Obtain translation of gettext, return a unicode object

        :param msgid: The string to translated.
        :type msgid: unicode
        :param context: The message context.
        :type context: unicode
        :returns: Translation or the original.
        :rtype: unicode
        """
        # If context=="" and msgid =="" then gettext will return po file header
        # and that's not what we want.
        if len((context + msgid).strip()) == 0:
            return msgid
        if context:
            return self.pgettext(context, msgid)
        return gettext.GNUTranslations.gettext(self, msgid)

    def ngettext(self, singular, plural, num):
        """
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the singular.

        :param singular: The singular form of the string to be translated.
                         may contain a context seperator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param num: the amount for which to decide the translation
        :type num: int
        :returns: Translation or the original.
        :rtype: unicode
        """
        return gettext.GNUTranslations.ngettext(self, singular, plural, num)

    def sgettext(self, msgid, context=""):
        """
        Strip the context used for resolving translation ambiguities.

        The translation of msgid is returned unless the translation is
        not available and the msgid contains the separator. In that case,
        the returned value is the portion of msgid following the last
        separator. Default separator is '|'.

        :param msgid: The string to translated.
        :type msgid: unicode
        :param context: The message context.
        :type context: unicode
        :param sep: The separator marking the context.
        :type sep: unicode
        :returns: Translation or the original with context stripped.
        :rtype: unicode
        """
        if "\x04" in msgid:  # Deferred translation
            context, msgid = msgid.split("\x04")
        return self.gettext(msgid, context)

    def lexgettext(self, msgid, context=""):
        """
        Extract all inflections of the same lexeme,
        stripping the '|'-separated context using :meth:`~sgettext`

        The *resulting* message provided by the translator
        is supposed to be '|'-separated as well.
        The possible formats are either (1) a single string
        for a language with no inflections, or (2) a list of
        <inflection name>=<inflected form>, separated with '|'.
        For example:

           (1) "Uninflectable"
           (2) "n=Inflected-nominative|g=Inflected-genitive|d=Inflected-dative"

        See :class:`~Lexeme` documentation for detailed explanation and example.

        :param msgid: The string to translated.
        :type msgid: unicode
        :param context: The message context.
        :type context: unicode
        :returns: Translation or the original with context stripped.
        :rtype: unicode (for option (1)) / Lexeme (option (2))
        """
        variants = self.sgettext(msgid, context).split("|")
        return (
            Lexeme([v.split("=") for v in variants])
            if len(variants) > 1
            else variants[0]
        )

    def pgettext(self, context, message):
        """
        Copied from python 3.8
        """
        ctxt_msg_id = self.CONTEXT % (context, message)
        missing = object()
        tmsg = self._catalog.get(ctxt_msg_id, missing)
        if tmsg is missing:
            if self._fallback:
                return self._fallback.pgettext(context, message)
            return message
        return tmsg


class GrampsNullTranslations(gettext.NullTranslations):
    """
    Extends gettext.NullTranslations to provide the sgettext method.

    Note that it's necessary for msgid to be unicode. If it's not,
    neither will be the returned string.
    """

    def gettext(self, msgid, context=""):
        """
        Apply the context if there is one, otherwise just pass it on.
        """
        if context:
            return self.pgettext(context, msgid)
        return gettext.NullTranslations.gettext(self, msgid)

    def sgettext(self, msgid, context=""):
        """
        An old workaround to not having proper context msgids: The msgid
        is a single string with an ASCII Message Separator character
        between the context and the mssgid."
        """
        if "\x04" in msgid:  # Deferred translation
            context, msgid = msgid.split("\x04")
        return self.gettext(msgid, context)

    lexgettext = sgettext

    def language(self):
        """
        The null translation returns the raw msgids, which are in English
        """
        return "en"

    def pgettext(self, context, message):
        """
        Copied from python 3.8
        """
        if self._fallback:
            return self._fallback.pgettext(context, message)
        return message
