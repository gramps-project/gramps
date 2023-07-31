#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010,2017  Nick Hall
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
Note class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .primaryobj import BasicPrimaryObject
from .tagbase import TagBase
from .notetype import NoteType
from .styledtext import StyledText
from .styledtexttagtype import StyledTextTagType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Class for notes used throughout the majority of Gramps objects
#
# -------------------------------------------------------------------------
class Note(BasicPrimaryObject):
    """Define a text note.

    Starting from Gramps 3.1 Note object stores the text in
    :class:`~.styledtext.StyledText` instance, thus it can have text formatting
    information.

    To get and set only the clear text of the note use the :meth:`get` and
    :meth:`set` methods.

    To get and set the formatted version of the Note's text use the
    :meth:`get_styledtext` and :meth:`set_styledtext` methods.

    The note may be 'preformatted' or 'flowed', which indicates that the
    text string is considered to be in paragraphs, separated by newlines.

    :cvar FLOWED: indicates flowed format
    :cvar FORMATTED: indicates formatted format (respecting whitespace needed)
    :cvar POS_<x>: (int) Position of <x> attribute in the serialized format of
        an instance.

    .. warning:: The POS_<x> class variables reflect the serialized object,
                 they have to be updated in case the data structure or the
                 :meth:`serialize` method changes!
    """

    (FLOWED, FORMATTED) = list(range(2))

    (
        POS_HANDLE,
        POS_ID,
        POS_TEXT,
        POS_FORMAT,
        POS_TYPE,
        POS_CHANGE,
        POS_TAGS,
        POS_PRIVATE,
    ) = list(range(8))

    def __init__(self, text=""):
        """Create a new Note object, initializing from the passed string."""
        BasicPrimaryObject.__init__(self)
        self.text = StyledText(text)
        self.format = Note.FLOWED
        self.type = NoteType()

    def serialize(self):
        """Convert the object to a serialized tuple of data.

        :returns: The serialized format of the instance.
        :rtype: tuple

        """
        return (
            self.handle,
            self.gramps_id,
            self.text.serialize(),
            self.format,
            self.type.serialize(),
            self.change,
            TagBase.serialize(self),
            self.private,
        )

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Note"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string", "maxLength": 50, "title": _("Handle")},
                "gramps_id": {"type": "string", "title": _("Gramps ID")},
                "text": StyledText.get_schema(),
                "format": {"type": "integer", "title": _("Format")},
                "type": NoteType.get_schema(),
                "change": {"type": "integer", "title": _("Last changed")},
                "tag_list": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "title": _("Tags"),
                },
                "private": {"type": "boolean", "title": _("Private")},
            },
        }

    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.

        :param data: The serialized format of a Note.
        :type: data: tuple
        """
        (
            self.handle,
            self.gramps_id,
            the_text,
            self.format,
            the_type,
            self.change,
            tag_list,
            self.private,
        ) = data

        self.text = StyledText()
        self.text.unserialize(the_text)
        self.type = NoteType()
        self.type.unserialize(the_type)
        TagBase.unserialize(self, tag_list)
        return self

    def get_text_data_list(self):
        """Return the list of all textual attributes of the object.

        :returns: The list of all textual attributes of the object.
        :rtype: list
        """
        return [str(self.text), self.gramps_id]

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        reflist = []
        for dom, obj, prop, hndl in self.get_links():
            if dom != "gramps" or prop != "handle":
                continue
            else:
                reflist.append((obj, hndl))
        reflist.extend(self.get_referenced_tag_handles())
        return reflist

    def has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given
        primary object type.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str

        :returns:
          Returns whether the object has reference to this handle of
          this object type.

        :rtype: bool
        """
        for dom, obj, prop, hndl in self.get_links():
            if (
                dom == "gramps"
                and prop == "handle"
                and obj == classname
                and hndl == handle
            ):
                return True
        return False

    def remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str

        If the link is in the styled text, we just remove the style for that
        link.
        """
        tags = []
        for styledtext_tag in self.text.get_tags():
            if (
                styledtext_tag.name == StyledTextTagType.LINK
                and styledtext_tag.value.startswith("gramps://")
            ):
                obj, prop, value = styledtext_tag.value[9:].split("/", 2)
                if obj == classname and prop == "handle" and value in handle_list:
                    continue
            tags.append(styledtext_tag)
        self.text.set_tags(tags)

    def replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        for styledtext_tag in self.text.get_tags():
            if (
                styledtext_tag.name == StyledTextTagType.LINK
                and styledtext_tag.value.startswith("gramps://")
            ):
                obj, prop, value = styledtext_tag.value[9:].split("/", 2)
                if obj == classname and prop == "handle" and value == old_handle:
                    styledtext_tag.value = styledtext_tag.value.replace(
                        old_handle, new_handle
                    )

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this note.

        Lost: handle, id, type, format, text and styles of acquisition.

        :param acquisition: The note to merge with the present note.
        :type acquisition: Note
        """
        self._merge_privacy(acquisition)
        self._merge_tag_list(acquisition)

    def set(self, text):
        """Set the text associated with the note to the passed string.

        :param text: The *clear* text defining the note contents.
        :type text: str
        """
        self.text = StyledText(text)

    def get(self):
        """Return the text string associated with the note.

        :returns: The *clear* text of the note contents.
        :rtype: unicode
        """
        return str(self.text)

    def set_styledtext(self, text):
        """Set the text associated with the note to the passed string.

        :param text: The *formatted* text defining the note contents.
        :type text: :class:`~.styledtext.StyledText`
        """
        self.text = text

    def get_styledtext(self):
        """Return the text string associated with the note.

        :returns: The *formatted* text of the note contents.
        :rtype: :class:`~.styledtext.StyledText`
        """
        return self.text

    def append(self, text):
        """Append the specified text to the text associated with the note.

        :param text: Text string to be appended to the note.
        :type text: str or :class:`~.styledtext.StyledText`
        """
        self.text = self.text + text

    def set_format(self, format):
        """Set the format of the note to the passed value.

        :param format: The value can either indicate Flowed or Preformatted.
        :type format: int
        """
        self.format = format

    def get_format(self):
        """Return the format of the note.

        The value can either indicate Flowed or Preformatted.

        :returns: 0 indicates Flowed, 1 indicates Preformated
        :rtype: int
        """
        return self.format

    def set_type(self, the_type):
        """Set descriptive type of the Note.

        :param the_type: descriptive type of the Note
        :type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """Get descriptive type of the Note.

        :returns: the descriptive type of the Note
        :rtype: str
        """
        return self.type

    def get_links(self):
        """
        Get the jump links from this note. Links can be external, to
        urls, or can be internal to gramps objects.

        Return examples::

            [("gramps", "Person", "handle", "7657626365362536"),
             ("external", "www", "url", "http://example.com")]

        :returns: list of [(domain, type, propery, value), ...]
        :rtype: list
        """
        retval = []
        for styledtext_tag in self.text.get_tags():
            if int(styledtext_tag.name) == StyledTextTagType.LINK:
                if styledtext_tag.value.startswith("gramps://"):
                    object_class, prop, value = styledtext_tag.value[9:].split("/", 2)
                    retval.append(("gramps", object_class, prop, value))
                else:
                    retval.append(("external", "www", "url", styledtext_tag.value))
        return retval
