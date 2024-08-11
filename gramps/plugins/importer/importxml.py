#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 200?-2013  Benny Malengier
# Copyright (C) 2009       Douglas S. Blank
# Copyright (C) 2010-2011  Nick Hall
# Copyright (C) 2011       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
# Standard Python Modules
#
# -------------------------------------------------------------------------
import os
import sys
import time
from xml.parsers.expat import ExpatError, ParserCreate
from xml.sax.saxutils import escape
from gramps.gen.const import URL_WIKISTRING
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
import re
import logging
from collections import abc

LOG = logging.getLogger(".ImportXML")

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.mime import get_type
from gramps.gen.lib import (
    Address,
    Attribute,
    AttributeType,
    ChildRef,
    ChildRefType,
    Citation,
    Date,
    DateError,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    LdsOrd,
    Location,
    Media,
    MediaRef,
    Name,
    NameOriginType,
    NameType,
    Note,
    NoteType,
    Person,
    PersonRef,
    Place,
    PlaceName,
    PlaceRef,
    PlaceType,
    RepoRef,
    Repository,
    Researcher,
    Source,
    SrcAttribute,
    SrcAttributeType,
    StyledText,
    StyledTextTag,
    StyledTextTagType,
    Surname,
    Tag,
    Url,
)
from gramps.gen.db import DbTxn

# from gramps.gen.db.write import CLASS_TO_KEY_MAP
from gramps.gen.errors import GrampsImportError
from gramps.gen.utils.id import create_id
from gramps.gen.utils.db import family_name
from gramps.gen.utils.unknown import make_unknown, create_explanation_note
from gramps.gen.utils.file import create_checksum, media_path, expand_media_path
from gramps.gen.datehandler import parser, set_date
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.db.dbconst import (
    PERSON_KEY,
    FAMILY_KEY,
    SOURCE_KEY,
    EVENT_KEY,
    MEDIA_KEY,
    PLACE_KEY,
    REPOSITORY_KEY,
    NOTE_KEY,
    TAG_KEY,
    CITATION_KEY,
    CLASS_TO_KEY_MAP,
)
from gramps.gen.updatecallback import UpdateCallback
from gramps.version import VERSION
from gramps.gen.config import config

# import gramps.plugins.lib.libgrampsxml
from gramps.plugins.lib import libgrampsxml
from gramps.gen.plug.utils import version_str_to_tup
from gramps.plugins.lib.libplaceimport import PlaceImport

# -------------------------------------------------------------------------
#
# Try to detect the presence of gzip
#
# -------------------------------------------------------------------------
try:
    import gzip

    GZIP_OK = True
except:
    GZIP_OK = False

PERSON_RE = re.compile(r"\s*\<person\s(.*)$")

CHILD_REL_MAP = {
    "Birth": ChildRefType(ChildRefType.BIRTH),
    "Adopted": ChildRefType(ChildRefType.ADOPTED),
    "Stepchild": ChildRefType(ChildRefType.STEPCHILD),
    "Sponsored": ChildRefType(ChildRefType.SPONSORED),
    "Foster": ChildRefType(ChildRefType.FOSTER),
    "Unknown": ChildRefType(ChildRefType.UNKNOWN),
}

# feature requests 2356, 1658: avoid genitive form
EVENT_FAMILY_STR = _("%(event_name)s of %(family)s")
# feature requests 2356, 1658: avoid genitive form
EVENT_PERSON_STR = _("%(event_name)s of %(person)s")

HANDLE = 0
INSTANTIATED = 1


# -------------------------------------------------------------------------
#
# Importing data into the currently open database.
# Must takes care of renaming media files according to their new IDs.
#
# -------------------------------------------------------------------------
def importData(database, filename, user):
    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}
    line_cnt = 1
    person_cnt = 0

    with ImportOpenFileContextManager(filename, user) as xml_file:
        if xml_file is None:
            return

        if filename == "-":
            change = time.time()
        else:
            change = os.path.getmtime(filename)
        if database.get_feature("skip-import-additions"):  # don't add source or tags
            parser = GrampsParser(database, user, change, None)
        else:
            parser = GrampsParser(
                database,
                user,
                change,
                (
                    config.get("preferences.tag-on-import-format")
                    if config.get("preferences.tag-on-import")
                    else None
                ),
            )

        if filename != "-":
            linecounter = LineParser(filename)
            line_cnt = linecounter.get_count()
            person_cnt = linecounter.get_person_count()

        read_only = database.readonly
        database.readonly = False

        try:
            info = parser.parse(xml_file, line_cnt, person_cnt)
        except GrampsImportError as err:  # version error
            user.notify_error(*err.messages())
            return
        except IOError as msg:
            user.notify_error(_("Error reading %s") % filename, str(msg))
            import traceback

            traceback.print_exc()
            return
        except ExpatError as msg:
            user.notify_error(
                _("Error reading %s") % filename,
                str(msg)
                + "\n"
                + _(
                    "The file is probably either corrupt or not a "
                    "valid Gramps database."
                ),
            )
            return

    database.readonly = read_only
    return info


# -------------------------------------------------------------------------
#
# Remove extraneous spaces
#
# -------------------------------------------------------------------------


def rs(text):
    return " ".join(text.split())


def fix_spaces(text_list):
    return "\n".join(map(rs, text_list))


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------


class ImportInfo:
    """
    Class object that can hold information about the import
    """

    keyorder = [
        PERSON_KEY,
        FAMILY_KEY,
        SOURCE_KEY,
        EVENT_KEY,
        MEDIA_KEY,
        PLACE_KEY,
        REPOSITORY_KEY,
        NOTE_KEY,
        TAG_KEY,
        CITATION_KEY,
    ]
    key2data = {
        PERSON_KEY: 0,
        FAMILY_KEY: 1,
        SOURCE_KEY: 2,
        EVENT_KEY: 3,
        MEDIA_KEY: 4,
        PLACE_KEY: 5,
        REPOSITORY_KEY: 6,
        NOTE_KEY: 7,
        TAG_KEY: 8,
        CITATION_KEY: 9,
    }

    def __init__(self):
        """
        Init of the import class.

        This creates the datastructures to hold info
        """
        self.data_mergecandidate = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        self.data_newobject = [0] * 10
        self.data_unknownobject = [0] * 10
        self.data_families = ""
        self.expl_note = ""
        self.data_relpath = False

    def add(self, category, key, obj, sec_obj=None):
        """
        Add info of a certain category. Key is one of the predefined keys,
        while obj is an object of which information will be extracted
        """
        if category == "merge-candidate":
            self.data_mergecandidate[self.key2data[key]][obj.handle] = (
                self._extract_mergeinfo(key, obj, sec_obj)
            )
        elif category == "new-object":
            self.data_newobject[self.key2data[key]] += 1
        elif category == "unknown-object":
            self.data_unknownobject[self.key2data[key]] += 1
        elif category == "relative-path":
            self.data_relpath = True
        elif category == "unlinked-family":
            # This is a bit ugly because it isn't using key in the same way as
            # the rest of the categories, but it is only the calling routine
            # that really knows what the error message should be.
            self.data_families += key + "\n"

    def _extract_mergeinfo(self, key, obj, sec_obj):
        """
        Extract info from obj about 'merge-candidate', Key is one of the
        predefined keys.
        """
        key2string = {
            FAMILY_KEY: _("Family"),
            SOURCE_KEY: _("Source"),
            EVENT_KEY: _("Event"),
            MEDIA_KEY: _("Media Object"),
            PLACE_KEY: _("Place"),
            REPOSITORY_KEY: _("Repository"),
            NOTE_KEY: _("Note"),
            CITATION_KEY: _("Citation"),
        }
        if key == PERSON_KEY:
            return _("  {id1} - {text} with {id2}").format(
                id1=obj.gramps_id,
                text=name_displayer.display(obj),
                id2=sec_obj.gramps_id,
            )
        elif key == TAG_KEY:
            pass  # Tags can't be merged
        else:
            return _("  {obj} {id1} with {id2}").format(
                obj=key2string[key], id1=obj.gramps_id, id2=sec_obj.gramps_id
            )

    def info_text(self):
        """
        Construct an info message from the data in the class.
        """
        key2string = {
            PERSON_KEY: _("People"),
            FAMILY_KEY: _("Families"),
            SOURCE_KEY: _("Sources"),
            EVENT_KEY: _("Events"),
            MEDIA_KEY: _("Media Objects"),
            PLACE_KEY: _("Places"),
            REPOSITORY_KEY: _("Repositories"),
            NOTE_KEY: _("Notes"),
            TAG_KEY: _("Tags"),
            CITATION_KEY: _("Citations"),
        }
        txt = [_("Number of new objects imported:")]
        table = []
        for key in self.keyorder:
            label = _("%s:") % key2string[key]
            new = "%d" % self.data_newobject[self.key2data[key]]
            if any(self.data_unknownobject):
                unknown = "(%d)" % self.data_unknownobject[self.key2data[key]]
                table.append([label, new, unknown])
            else:
                table.append([label, new])
        txt.append(table)

        if any(self.data_unknownobject):
            txt.append(
                _(
                    "\nThe imported file was not self-contained.\n"
                    "To correct for that, %(new)d objects were created and\n"
                    "their typifying attribute was set to 'Unknown'.\n"
                    "The breakdown per category is depicted by the\n"
                    "number in parentheses. Where possible these\n"
                    "'Unknown' objects are referenced by note %(unknown)s."
                )
                % {"new": sum(self.data_unknownobject), "unknown": self.expl_note}
            )
        if self.data_relpath:
            txt.append(
                _(
                    "\nMedia objects with relative paths have been\n"
                    "imported. These paths are considered relative to\n"
                    "the media directory you can set in the preferences,\n"
                    "or, if not set, relative to the user's directory."
                )
            )
        merge = False
        for key in self.keyorder:
            if self.data_mergecandidate[self.key2data[key]]:
                merge = True
                break
        if merge:
            txt.append(_("\nObjects that are candidates to be merged:"))
            for key in self.keyorder:
                datakey = self.key2data[key]
                for handle in list(self.data_mergecandidate[datakey].keys()):
                    txt.append(self.data_mergecandidate[datakey][handle])

        if self.data_families:
            txt.append(self.data_families)

        return txt


class LineParser:
    def __init__(self, filename):
        self.count = 0
        self.person_count = 0

        if GZIP_OK:
            use_gzip = 1
            try:
                with gzip.open(filename, "r") as f:
                    f.read(1)
            except IOError as msg:
                use_gzip = 0
            except ValueError as msg:
                use_gzip = 1
        else:
            use_gzip = 0

        try:
            if use_gzip:
                import io

                # Bug 6255. TextIOWrapper is required for python3 to
                #           present file contents as text, otherwise they
                #           are read as binary. However due to a missing
                #           method (read1) in early python3 versions this
                #           try block will fail.
                #           Gramps will still import XML files using python
                #           versions < 3.3.0 but the file progress meter
                #           will not work properly, going immediately to
                #           100%.
                #           It should work correctly from version 3.3.
                ofile = io.TextIOWrapper(
                    gzip.open(filename, "rb"), encoding="utf8", errors="replace"
                )
            else:
                ofile = open(filename, "r", encoding="utf8", errors="replace")

            for line in ofile:
                self.count += 1
                if PERSON_RE.match(line):
                    self.person_count += 1
        except:
            self.count = 0
            self.person_count = 0
        finally:
            # Ensure the file handle is always closed
            ofile.close()

    def get_count(self):
        return self.count

    def get_person_count(self):
        return self.person_count


# -------------------------------------------------------------------------
#
# ImportOpenFileContextManager
#
# -------------------------------------------------------------------------
class ImportOpenFileContextManager:
    """
    Context manager to open a file or stdin for reading.
    """

    def __init__(self, filename, user):
        self.filename = filename
        self.filehandle = None
        self.user = user

    def __enter__(self):
        if self.filename == "-":
            try:
                self.filehandle = sys.stdin.buffer
            except:
                self.filehandle = sys.stdin
        else:
            self.filehandle = self.open_file(self.filename)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename != "-":
            if self.filehandle:
                self.filehandle.close()
        return False

    def open_file(self, filename):
        """
        Open the xml file.
        Return a valid file handle if the file opened sucessfully.
        Return None if the file was not able to be opened.
        """
        if GZIP_OK:
            use_gzip = True
            try:
                with gzip.open(filename, "r") as ofile:
                    ofile.read(1)
            except IOError as msg:
                use_gzip = False
            except ValueError as msg:
                use_gzip = True
        else:
            use_gzip = False

        try:
            if use_gzip:
                xml_file = gzip.open(filename, "rb")
            else:
                xml_file = open(filename, "rb")
        except IOError as msg:
            self.user.notify_error(_("%s could not be opened") % filename, str(msg))
            xml_file = None
        except:
            self.user.notify_error(_("%s could not be opened") % filename)
            xml_file = None

        return xml_file


# -------------------------------------------------------------------------
#
# Gramps database parsing class.  Derived from SAX XML parser
#
# -------------------------------------------------------------------------
class GrampsParser(UpdateCallback):
    def __init__(self, database, user, change, default_tag_format=None):
        UpdateCallback.__init__(self, user.callback)
        self.user = user
        self.__gramps_version = "unknown"
        self.__xml_version = (1, 0, 0)
        self.stext_list = []
        self.scomments_list = []
        self.note_list = []
        self.tlist = []
        self.conf = 2
        self.gid2id = {}
        self.gid2fid = {}
        self.gid2eid = {}
        self.gid2pid = {}
        self.gid2oid = {}
        self.gid2sid = {}
        self.gid2rid = {}
        self.gid2nid = {}
        self.childref_map = {}
        self.change = change
        self.dp = parser
        self.info = ImportInfo()
        self.all_abs = True
        self.db = database
        # Data with handles already present in the db will overwrite existing
        # data, so all imported data gets a new handle. This behavior is not
        # needed and even unwanted if data is imported in an empty family tree
        # because NarWeb urls are based on handles. Also for debugging purposes
        # it can be advantageous to preserve the orginal handle.
        self.replace_import_handle = (
            self.db.get_number_of_people() > 0 and not LOG.isEnabledFor(logging.DEBUG)
        )

        # Similarly, if the data is imported into an empty family tree, we also
        # import the Researcher; if the tree was not empty, the existing
        # Researcher is retained
        self.import_researcher = self.db.get_total() == 0
        self.ord = None
        self.objref = None
        self.object = None
        self.repo = None
        self.reporef = None
        self.pref = None
        self.use_p = 0
        self.in_note = 0
        self.in_stext = 0
        self.in_scomments = 0
        self.note = None
        self.note_text = None
        self.note_tags = []
        self.in_witness = False
        self.photo = None
        self.person = None
        self.family = None
        self.address = None
        self.citation = None
        self.in_old_sourceref = False
        self.source = None
        self.attribute = None
        self.srcattribute = None
        self.placeobj = None
        self.placeref = None
        self.place_name = None
        self.locations = 0
        self.place_names = 0
        self.place_map = {}
        self.place_import = PlaceImport(self.db)

        self.resname = ""
        self.resaddr = ""
        self.reslocality = ""
        self.rescity = ""
        self.resstate = ""
        self.rescon = ""
        self.respos = ""
        self.resphone = ""
        self.resemail = ""

        self.mediapath = ""

        self.pmap = {}
        self.fmap = {}
        self.smap = {}
        self.lmap = {}
        self.media_file_map = {}

        # List of new name formats and a dict for remapping them
        self.name_formats = []
        self.name_formats_map = {}
        self.taken_name_format_numbers = [num[0] for num in self.db.name_formats]

        self.event = None
        self.eventref = None
        self.childref = None
        self.personref = None
        self.name = None
        self.surname = None
        self.surnamepat = None
        self.home = None
        self.owner = Researcher()
        self.func_list = [None] * 50
        self.func_index = 0
        self.func = None
        self.witness_comment = ""
        self.idswap = {}
        self.fidswap = {}
        self.eidswap = {}
        self.cidswap = {}
        self.sidswap = {}
        self.pidswap = {}
        self.oidswap = {}
        self.ridswap = {}
        self.nidswap = {}
        self.eidswap = {}
        self.import_handles = {}

        if default_tag_format:
            name = time.strftime(default_tag_format)
            tag = self.db.get_tag_from_name(name)
            if tag:
                self.default_tag = tag
            else:
                self.default_tag = Tag()
                self.default_tag.set_name(name)
        else:
            self.default_tag = None

        self.func_map = {
            # name part
            "name": (self.start_name, self.stop_name),
            "first": (None, self.stop_first),
            "call": (None, self.stop_call),
            "aka": (self.start_name, self.stop_aka),  # deprecated < 1.3.0
            "last": (self.start_last, self.stop_last),  # deprecated in 1.4.0
            "nick": (None, self.stop_nick),
            "title": (None, self.stop_title),
            "suffix": (None, self.stop_suffix),
            "patronymic": (
                self.start_patronymic,
                self.stop_patronymic,
            ),  # deprecated in 1.4.0
            "familynick": (None, self.stop_familynick),  # new in 1.4.0
            "group": (None, self.stop_group),  # new in 1.4.0, replaces attribute
            # new in 1.4.0
            "surname": (self.start_surname, self.stop_surname),
            #
            "namemaps": (None, None),
            "name-formats": (None, None),
            # other
            "address": (self.start_address, self.stop_address),
            "addresses": (None, None),
            "alt_name": (None, self.stop_alt_name),
            "childlist": (None, None),
            "attribute": (self.start_attribute, self.stop_attribute),
            "attr_type": (None, self.stop_attr_type),
            "attr_value": (None, self.stop_attr_value),
            "srcattribute": (self.start_srcattribute, self.stop_srcattribute),
            "bookmark": (self.start_bmark, None),
            "bookmarks": (None, None),
            "format": (self.start_format, None),
            "child": (self.start_child, None),
            "childof": (self.start_childof, None),
            "childref": (self.start_childref, self.stop_childref),
            "personref": (self.start_personref, self.stop_personref),
            "citation": (self.start_citation, self.stop_citation),
            "citationref": (self.start_citationref, None),
            "citations": (None, None),
            "city": (None, self.stop_city),
            "county": (None, self.stop_county),
            "country": (None, self.stop_country),
            "comment": (None, self.stop_comment),
            "confidence": (None, self.stop_confidence),
            "created": (self.start_created, None),
            "ref": (None, self.stop_ref),
            "database": (self.start_database, self.stop_database),
            "phone": (None, self.stop_phone),
            "date": (None, self.stop_date),
            "cause": (None, self.stop_cause),
            "code": (None, self.stop_code),
            "description": (None, self.stop_description),
            "event": (self.start_event, self.stop_event),
            "type": (None, self.stop_type),
            "witness": (self.start_witness, self.stop_witness),
            "eventref": (self.start_eventref, self.stop_eventref),
            "data_item": (self.start_data_item, None),  # deprecated in 1.6.0
            "families": (None, self.stop_families),
            "family": (self.start_family, self.stop_family),
            "rel": (self.start_rel, None),
            "region": (self.start_region, None),
            "father": (self.start_father, None),
            "gender": (None, self.stop_gender),
            "header": (None, self.stop_header),
            "map": (self.start_namemap, None),
            "mediapath": (None, self.stop_mediapath),
            "mother": (self.start_mother, None),
            "note": (self.start_note, self.stop_note),
            "noteref": (self.start_noteref, None),
            "p": (None, self.stop_ptag),
            "parentin": (self.start_parentin, None),
            "people": (self.start_people, self.stop_people),
            "person": (self.start_person, self.stop_person),
            "img": (self.start_photo, self.stop_photo),
            "objref": (self.start_objref, self.stop_objref),
            "object": (self.start_media, self.stop_media),
            "file": (self.start_file, None),
            "page": (None, self.stop_page),
            "place": (self.start_place, self.stop_place),
            "dateval": (self.start_dateval, None),
            "daterange": (self.start_daterange, None),
            "datespan": (self.start_datespan, None),
            "datestr": (self.start_datestr, None),
            "places": (None, self.stop_places),
            "placeobj": (self.start_placeobj, self.stop_placeobj),
            "placeref": (self.start_placeref, self.stop_placeref),
            "ptitle": (None, self.stop_ptitle),
            "pname": (self.start_place_name, self.stop_place_name),
            "locality": (None, self.stop_locality),
            "location": (self.start_location, None),
            "lds_ord": (self.start_lds_ord, self.stop_lds_ord),
            "temple": (self.start_temple, None),
            "status": (self.start_status, None),
            "sealed_to": (self.start_sealed_to, None),
            "coord": (self.start_coord, None),
            "pos": (self.start_pos, None),
            "postal": (None, self.stop_postal),
            "range": (self.start_range, None),
            "researcher": (None, self.stop_research),
            "resname": (None, self.stop_resname),
            "resaddr": (None, self.stop_resaddr),
            "reslocality": (None, self.stop_reslocality),
            "rescity": (None, self.stop_rescity),
            "resstate": (None, self.stop_resstate),
            "rescountry": (None, self.stop_rescountry),
            "respostal": (None, self.stop_respostal),
            "resphone": (None, self.stop_resphone),
            "resemail": (None, self.stop_resemail),
            "sauthor": (None, self.stop_sauthor),
            "sabbrev": (None, self.stop_sabbrev),
            "scomments": (None, self.stop_scomments),
            "source": (self.start_source, self.stop_source),
            "sourceref": (self.start_sourceref, self.stop_sourceref),
            "sources": (None, None),
            "spage": (None, self.stop_spage),
            "spubinfo": (None, self.stop_spubinfo),
            "state": (None, self.stop_state),
            "stext": (None, self.stop_stext),
            "stitle": (None, self.stop_stitle),
            "street": (None, self.stop_street),
            "style": (self.start_style, None),
            "tag": (self.start_tag, self.stop_tag),
            "tagref": (self.start_tagref, None),
            "tags": (None, None),
            "text": (None, self.stop_text),
            "url": (self.start_url, None),
            "repository": (self.start_repo, self.stop_repo),
            "reporef": (self.start_reporef, self.stop_reporef),
            "rname": (None, self.stop_rname),
        }
        self.grampsuri = re.compile(
            r"^gramps://(?P<object_class>[A-Z][a-z]+)/" r"handle/(?P<handle>\w+)$"
        )

    def inaugurate(self, handle, target, prim_obj):
        """
        Assign a handle (identity) to a primary object (and create it if it
        doesn't exist yet) and add it to the database.

        This method can be called with an object instance or with a
        class object. Be aware that in the first case the side effect of this
        function is to fill the object instance with the data read from the db.
        In the second case, an empty object with the correct handle will be
        created.

        :param handle: The handle of the primary object, typically as read
                       directly from the XML attributes.
        :type handle: str
        :param target: Indicates the primary object type this handle relates to.
        :type target: str, identical to target attr of bookmarks.
        :param prim_obj: template of the primary object that is to be created.
        :type prim_obj: Either an empty instance of a primary object or the
                         class object of a primary object.
        :returns: The handle of the primary object.
        :rtype: str
        """
        handle = str(handle.replace("_", ""))
        orig_handle = handle
        if (
            orig_handle in self.import_handles
            and target in self.import_handles[orig_handle]
        ):
            handle = self.import_handles[handle][target][HANDLE]
            if not isinstance(prim_obj, abc.Callable):
                # This method is called by a start_<primary_object> method.
                get_raw_obj_data = {
                    "person": self.db.get_raw_person_data,
                    "family": self.db.get_raw_family_data,
                    "event": self.db.get_raw_event_data,
                    "place": self.db.get_raw_place_data,
                    "source": self.db.get_raw_source_data,
                    "citation": self.db.get_raw_citation_data,
                    "repository": self.db.get_raw_repository_data,
                    "media": self.db.get_raw_media_data,
                    "note": self.db.get_raw_note_data,
                    "tag": self.db.get_raw_tag_data,
                }[target]
                raw = get_raw_obj_data(handle)
                prim_obj.unserialize(raw)
                self.import_handles[orig_handle][target][INSTANTIATED] = True
            return handle
        elif handle in self.import_handles:
            LOG.warning(
                "The file you import contains duplicate handles "
                "which is illegal and being fixed now."
            )
            handle = create_id()
            while handle in self.import_handles:
                handle = create_id()
            self.import_handles[orig_handle][target] = [handle, False]
        else:
            orig_handle = handle
            if self.replace_import_handle:
                handle = create_id()
                while handle in self.import_handles:
                    handle = create_id()
            else:
                has_handle_func = {
                    "person": self.db.has_person_handle,
                    "family": self.db.has_family_handle,
                    "event": self.db.has_event_handle,
                    "place": self.db.has_place_handle,
                    "source": self.db.has_source_handle,
                    "citation": self.db.get_raw_citation_data,
                    "repository": self.db.has_repository_handle,
                    "media": self.db.has_media_handle,
                    "note": self.db.has_note_handle,
                    "tag": self.db.has_tag_handle,
                }[target]
                while has_handle_func(handle):
                    handle = create_id()
            self.import_handles[orig_handle] = {target: [handle, False]}
        # method is called by a reference
        if isinstance(prim_obj, abc.Callable):
            prim_obj = prim_obj()
        else:
            self.import_handles[orig_handle][target][INSTANTIATED] = True
        prim_obj.set_handle(handle)
        if target == "tag":
            self.db.add_tag(prim_obj, self.trans)
        else:
            add_func = {
                "person": self.db.add_person,
                "family": self.db.add_family,
                "event": self.db.add_event,
                "place": self.db.add_place,
                "source": self.db.add_source,
                "citation": self.db.add_citation,
                "repository": self.db.add_repository,
                "media": self.db.add_media,
                "note": self.db.add_note,
            }[target]
            add_func(prim_obj, self.trans, set_gid=False)
        return handle

    def inaugurate_id(self, id_, key, prim_obj):
        """
        Equivalent of inaugurate but for old style XML.
        """
        if id_ is None:
            raise GrampsImportError(
                _("The Gramps Xml you are trying to " "import is malformed."),
                _("Attributes that link the data " "together are missing."),
            )
        id2handle_map = [
            self.gid2id,
            self.gid2fid,
            self.gid2sid,
            self.gid2eid,
            self.gid2oid,
            self.gid2pid,
            self.gid2rid,
            "reference",
            self.gid2nid,
        ][key]
        has_handle_func = [
            self.db.has_person_handle,
            self.db.has_family_handle,
            self.db.has_source_handle,
            self.db.has_event_handle,
            self.db.has_media_handle,
            self.db.has_place_handle,
            self.db.has_repository_handle,
            "reference",
            self.db.has_note_handle,
        ][key]
        add_func = [
            self.db.add_person,
            self.db.add_family,
            self.db.add_source,
            self.db.add_event,
            self.db.add_media,
            self.db.add_place,
            self.db.add_repository,
            "reference",
            self.db.add_note,
        ][key]
        get_raw_obj_data = [
            self.db.get_raw_person_data,
            self.db.get_raw_family_data,
            self.db.get_raw_source_data,
            self.db.get_raw_event_data,
            self.db.get_raw_media_data,
            self.db.get_raw_place_data,
            self.db.get_raw_repository_data,
            "reference",
            self.db.get_raw_note_data,
        ][key]
        id2id_map = [
            self.idswap,
            self.fidswap,
            self.sidswap,
            self.eidswap,
            self.oidswap,
            self.pidswap,
            self.ridswap,
            "reference",
            self.nidswap,
        ][key]
        id2user_format = [
            self.db.id2user_format,
            self.db.fid2user_format,
            self.db.sid2user_format,
            self.db.eid2user_format,
            self.db.oid2user_format,
            self.db.pid2user_format,
            self.db.rid2user_format,
            "reference",
            self.db.nid2user_format,
        ][key]
        find_next_gramps_id = [
            self.db.find_next_person_gramps_id,
            self.db.find_next_family_gramps_id,
            self.db.find_next_source_gramps_id,
            self.db.find_next_event_gramps_id,
            self.db.find_next_media_gramps_id,
            self.db.find_next_place_gramps_id,
            self.db.find_next_repository_gramps_id,
            "reference",
            self.db.find_next_note_gramps_id,
        ][key]
        has_gramps_id = [
            self.db.has_person_gramps_id,
            self.db.has_family_gramps_id,
            self.db.has_source_gramps_id,
            self.db.has_event_gramps_id,
            self.db.has_media_gramps_id,
            self.db.has_place_gramps_id,
            self.db.has_repository_gramps_id,
            "reference",
            self.db.has_note_gramps_id,
        ][key]

        gramps_id = self.legalize_id(
            id_, key, id2id_map, id2user_format, find_next_gramps_id, has_gramps_id
        )
        handle = id2handle_map.get(gramps_id)
        if handle:
            raw = get_raw_obj_data(handle)
            prim_obj.unserialize(raw)
        else:
            handle = create_id()
            while has_handle_func(handle):
                handle = create_id()
            if isinstance(prim_obj, abc.Callable):
                prim_obj = prim_obj()
            prim_obj.set_handle(handle)
            prim_obj.set_gramps_id(gramps_id)
            add_func(prim_obj, self.trans)
            id2handle_map[gramps_id] = handle
        return handle

    def legalize_id(
        self, id_, key, gramps_ids, id2user_format, find_next_gramps_id, has_gramps_id
    ):
        """
        Given an import id, adjust it so that it fits with the existing data.

        :param id_: The id as it is in the Xml import file, might be None.
        :type id_: str
        :param key: Indicates kind of primary object this id is for.
        :type key: int
        :param gramps_ids: Dictionary with id's that have already been imported.
        :type import_ids: dict
        :param id2user_format: Function to convert a raw id into the format as
                               specified in the prefixes.
        :type id2user_format: func
        :param find_next_gramps_id: function to get the next available id.
        :type find_next_gramps_id: func
        :returns: The id.
        :rtype: str
        """
        gramps_id = id2user_format(id_)
        if gramps_id is None or not gramps_ids.get(id_):
            if gramps_id is None or has_gramps_id(gramps_id):
                gramps_ids[id_] = find_next_gramps_id()
            else:
                gramps_ids[id_] = gramps_id
        return gramps_ids[id_]

    def parse(self, ifile, linecount=1, personcount=0):
        """
        Parse the xml file
        :param ifile: must be a file handle that is already open, with position
                      at the start of the file
        """
        with DbTxn(_("Gramps XML import"), self.db, batch=True) as self.trans:
            self.set_total(linecount)

            self.db.disable_signals()

            if self.default_tag and self.default_tag.handle is None:
                self.db.add_tag(self.default_tag, self.trans)

            self.p = ParserCreate()
            self.p.StartElementHandler = self.startElement
            self.p.EndElementHandler = self.endElement
            self.p.CharacterDataHandler = self.characters
            self.p.ParseFile(ifile)

            if len(self.name_formats) > 0:
                # add new name formats to the existing table
                self.db.name_formats += self.name_formats
                # Register new formats
                name_displayer.set_name_format(self.db.name_formats)

            # If the database was originally empty we update the researcher from
            # the XML (or initialised to no researcher)
            if self.import_researcher:
                self.db.set_researcher(self.owner)
            if self.home is not None:
                person = self.db.get_person_from_handle(self.home)
                self.db.set_default_person_handle(person.handle)

            # Set media path
            # The paths are normalized before being compared.
            if self.mediapath:
                if not self.db.get_mediapath():
                    self.db.set_mediapath(self.mediapath)
                elif not media_path(self.db) == expand_media_path(
                    self.mediapath, self.db
                ):
                    self.user.notify_error(
                        _("Could not change media path"),
                        _(
                            "The opened file has media path %s, which conflicts with"
                            " the media path of the Family Tree you import into. "
                            "The original media path has been retained. Copy the "
                            "files to a correct directory or change the media "
                            "path in the Preferences."
                        )
                        % self.mediapath,
                    )

            self.fix_not_instantiated()
            self.fix_families()
            for key in list(self.func_map.keys()):
                del self.func_map[key]
            del self.func_map
            del self.func_list
            del self.p
            del self.update
        self.db.enable_signals()
        self.db.request_rebuild()
        return self.info

    def start_database(self, attrs):
        """
        Get the xml version of the file.
        """
        if "xmlns" in attrs:
            xmlns = attrs.get("xmlns").split("/")
            if len(xmlns) >= 2 and not xmlns[2] == "gramps-project.org":
                self.__xml_version = (0, 0, 0)
            else:
                try:
                    self.__xml_version = version_str_to_tup(xmlns[4], 3)
                except:
                    # leave version at 1.0.0 although it could be 0.0.0 ??
                    pass
        else:
            # 1.0 or before xml, no dtd schema yet on
            # http://www.gramps-project.org/xml/
            self.__xml_version = (0, 0, 0)

    def start_created(self, attrs):
        """
        Get the Gramps version that produced the file.
        """
        if "sources" in attrs:
            self.num_srcs = int(attrs["sources"])
        else:
            self.num_srcs = 0
        if "places" in attrs:
            self.num_places = int(attrs["places"])
        else:
            self.num_places = 0
        if "version" in attrs:
            self.__gramps_version = attrs.get("version")

    def stop_header(self, *dummy):
        """
        Check the version of Gramps and XML.
        """
        xmlversion_str = ".".join(str(i) for i in self.__xml_version)
        if self.__gramps_version == "unknown":
            msg = _(
                "The .gramps file you are importing does not contain information about "
                "the version of Gramps with, which it was produced.\n\n"
                "The file will not be imported."
            )
            raise GrampsImportError(_("Import file misses Gramps version"), msg)
        if self.__xml_version > libgrampsxml.GRAMPS_XML_VERSION_TUPLE:
            msg = _(
                "The .gramps file you are importing was made by "
                "version %(newer)s of "
                "Gramps, while you are running an older version %(older)s. "
                "The file will not be imported. Please upgrade to the "
                "latest version of Gramps and try again."
            ) % {"newer": self.__gramps_version, "older": VERSION}
            raise GrampsImportError("", msg)
        if self.__xml_version < (1, 0, 0):
            msg = _(
                "The .gramps file you are importing was made by version "
                "%(oldgramps)s of Gramps, while you are running a more "
                "recent version %(newgramps)s.\n\n"
                "The file will not be imported. Please use an older version"
                " of Gramps that supports version %(xmlversion)s of the "
                "xml.\nSee\n  %(gramps_wiki_xml_url)s\n for more info."
            ) % {
                "oldgramps": self.__gramps_version,
                "newgramps": VERSION,
                "xmlversion": xmlversion_str,
                "gramps_wiki_xml_url": URL_WIKISTRING + "Gramps_XML",
            }
            raise GrampsImportError(_("The file will not be imported"), msg)
        elif self.__xml_version < (1, 1, 0):
            msg = _(
                "The .gramps file you are importing was made by version "
                "%(oldgramps)s of Gramps, while you are running a much "
                "more recent version %(newgramps)s.\n\n"
                "Ensure after import everything is imported correctly. In "
                "the event of problems, please submit a bug and use an "
                "older version of Gramps in the meantime to import this "
                "file, which is version %(xmlversion)s of the xml.\nSee\n  "
                "%(gramps_wiki_xml_url)s\nfor more info."
            ) % {
                "oldgramps": self.__gramps_version,
                "newgramps": VERSION,
                "xmlversion": xmlversion_str,
                "gramps_wiki_xml_url": URL_WIKISTRING + "Gramps_XML",
            }
            self.user.warn(_("Old xml file"), msg)

    def start_lds_ord(self, attrs):
        self.ord = LdsOrd()
        self.ord.set_type_from_xml(attrs["type"])
        self.ord.private = bool(attrs.get("priv"))
        if self.person:
            self.person.lds_ord_list.append(self.ord)
        elif self.family:
            self.family.lds_ord_list.append(self.ord)

    def start_temple(self, attrs):
        self.ord.set_temple(attrs["val"])

    def start_data_item(self, attrs):
        """
        Deprecated in 1.6.0, replaced by srcattribute
        """
        sat = SrcAttributeType(attrs["key"])
        sa = SrcAttribute()
        sa.set_type(sat)
        sa.set_value(attrs["value"])
        if self.source:
            self.source.add_attribute(sa)
        else:
            self.citation.add_attribute(sa)

    def start_status(self, attrs):
        try:
            # old xml with integer statuses
            self.ord.set_status(int(attrs["val"]))
        except ValueError:
            # string
            self.ord.set_status_from_xml(attrs["val"])

    def start_sealed_to(self, attrs):
        """
        Add a family reference to the LDS ordinance currently processed.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "family", Family)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), FAMILY_KEY, Family)
        self.ord.set_family_handle(handle)

    def start_place(self, attrs):
        """A reference to a place in an object: event or lds_ord"""
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "place", Place)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), PLACE_KEY, Place)
        if self.ord:
            self.ord.set_place_handle(handle)
        elif self.event:
            self.event.set_place_handle(handle)

    def start_placeobj(self, attrs):
        """
        Add a place object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.placeobj = Place()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle and self.db.has_place_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "place", self.placeobj)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                PLACE_KEY,
                self.pidswap,
                self.db.pid2user_format,
                self.db.find_next_place_gramps_id,
                self.db.has_place_gramps_id,
            )
            self.placeobj.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_place = self.db.get_place_from_handle(orig_handle)
                self.info.add("merge-candidate", PLACE_KEY, orig_place, self.placeobj)
        else:
            self.inaugurate_id(attrs.get("id"), PLACE_KEY, self.placeobj)
        self.placeobj.private = bool(attrs.get("priv"))
        self.placeobj.change = int(attrs.get("change", self.change))
        if self.__xml_version == (1, 6, 0):
            place_name = PlaceName()
            place_name.set_value(attrs.get("name", ""))
            self.placeobj.name = place_name
        if "type" in attrs:
            self.placeobj.place_type.set_from_xml_str(attrs.get("type"))
        self.info.add("new-object", PLACE_KEY, self.placeobj)
        self.place_names = 0

        # Gramps LEGACY: title in the placeobj tag
        self.placeobj.title = attrs.get("title", "")
        self.locations = 0
        self.update(self.p.CurrentLineNumber)
        if self.default_tag:
            self.placeobj.add_tag(self.default_tag.handle)
        return self.placeobj

    def start_location(self, attrs):
        """Bypass the function calls for this one, since it appears to
        take up quite a bit of time"""

        loc = Location()
        loc.street = attrs.get("street", "")
        loc.locality = attrs.get("locality", "")
        loc.city = attrs.get("city", "")
        loc.parish = attrs.get("parish", "")
        loc.county = attrs.get("county", "")
        loc.state = attrs.get("state", "")
        loc.country = attrs.get("country", "")
        loc.postal = attrs.get("postal", "")
        loc.phone = attrs.get("phone", "")

        if self.__xml_version < (1, 6, 0):
            if self.locations > 0:
                self.placeobj.add_alternate_locations(loc)
            else:
                location = (
                    attrs.get("street", ""),
                    attrs.get("locality", ""),
                    attrs.get("parish", ""),
                    attrs.get("city", ""),
                    attrs.get("county", ""),
                    attrs.get("state", ""),
                    attrs.get("country", ""),
                )
                self.place_import.store_location(location, self.placeobj.handle)

                for level, name in enumerate(location):
                    if name:
                        break
                place_name = PlaceName()
                place_name.set_value(name)
                self.placeobj.set_name(place_name)
                type_num = 7 - level if name else PlaceType.UNKNOWN
                self.placeobj.set_type(PlaceType(type_num))
                codes = [attrs.get("postal"), attrs.get("phone")]
                self.placeobj.set_code(" ".join(code for code in codes if code))
        else:
            self.placeobj.add_alternate_locations(loc)

        self.locations = self.locations + 1

    def start_witness(self, attrs):
        """
        Add a note about a witness to the currently processed event or add
        an event reference connecting that event with a person assigning the
        role of witness.
        """
        # Parse witnesses created by older gramps
        self.in_witness = True
        self.witness_comment = ""
        if "name" in attrs:
            note = Note()
            note.handle = create_id()
            note.set(_("Witness name: %s") % attrs["name"])
            note.type.set(NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            # set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add("new-object", NOTE_KEY, note)
            self.event.add_note(note.handle)
            return

        person = Person()
        if "hlink" in attrs:
            self.inaugurate(attrs["hlink"], "person", person)
        elif "ref" in attrs:
            self.inaugurate_id(attrs["ref"], PERSON_KEY, person)
        else:
            person = None

        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        if person:
            event_ref = EventRef()
            event_ref.ref = self.event.handle
            event_ref.role.set(EventRoleType.WITNESS)
            person.event_ref_list.append(event_ref)
            self.db.commit_person(person, self.trans, self.change)

    def start_coord(self, attrs):
        self.placeobj.lat = attrs.get("lat", "")
        self.placeobj.long = attrs.get("long", "")

    def start_event(self, attrs):
        """
        Add an event object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        if self.person or self.family:
            # Gramps LEGACY: old events that were written inside
            # person or family objects.
            self.event = Event()
            self.event.handle = create_id()
            self.event.type = EventType()
            self.event.type.set_from_xml_str(attrs["type"])
            self.db.add_event(self.event, self.trans)
            # set correct change time
            self.db.commit_event(self.event, self.trans, self.change)
            self.info.add("new-object", EVENT_KEY, self.event)
        else:
            # This is new event, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            self.event = Event()
            if "handle" in attrs:
                orig_handle = attrs["handle"].replace("_", "")
                is_merge_candidate = (
                    self.replace_import_handle and self.db.has_event_handle(orig_handle)
                )
                self.inaugurate(orig_handle, "event", self.event)
                gramps_id = self.legalize_id(
                    attrs.get("id"),
                    EVENT_KEY,
                    self.eidswap,
                    self.db.eid2user_format,
                    self.db.find_next_event_gramps_id,
                    self.db.has_event_gramps_id,
                )
                self.event.set_gramps_id(gramps_id)
                if is_merge_candidate:
                    orig_event = self.db.get_event_from_handle(orig_handle)
                    self.info.add("merge-candidate", EVENT_KEY, orig_event, self.event)
            else:  # old style XML
                self.inaugurate_id(attrs.get("id"), EVENT_KEY, self.event)
            self.event.private = bool(attrs.get("priv"))
            self.event.change = int(attrs.get("change", self.change))
            self.info.add("new-object", EVENT_KEY, self.event)
        if self.default_tag:
            self.event.add_tag(self.default_tag.handle)
        return self.event

    def start_eventref(self, attrs):
        """
        Add an event reference to the object currently processed.
        """
        self.eventref = EventRef()
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "event", Event)
        else:  # there is no old style XML
            raise GrampsImportError(
                _("The Gramps Xml you are trying to " "import is malformed."),
                _("Any event reference must have a " "'hlink' attribute."),
            )
        self.eventref.ref = handle
        self.eventref.private = bool(attrs.get("priv"))
        if "role" in attrs:
            self.eventref.role.set_from_xml_str(attrs["role"])

        # We count here on events being already parsed prior to parsing
        # people or families. This code will fail if this is not true.
        event = self.db.get_event_from_handle(self.eventref.ref)
        if not event:
            return

        if self.family:
            self.family.add_event_ref(self.eventref)
        elif self.person:
            if (
                (event.type == EventType.BIRTH)
                and (self.eventref.role == EventRoleType.PRIMARY)
                and (self.person.get_birth_ref() is None)
            ):
                self.person.set_birth_ref(self.eventref)
            elif (
                (event.type == EventType.DEATH)
                and (self.eventref.role == EventRoleType.PRIMARY)
                and (self.person.get_death_ref() is None)
            ):
                self.person.set_death_ref(self.eventref)
            else:
                self.person.add_event_ref(self.eventref)

    def start_placeref(self, attrs):
        """
        Add a place reference to the place currently being processed.
        """
        self.placeref = PlaceRef()
        handle = self.inaugurate(attrs["hlink"], "place", Place)
        self.placeref.ref = handle
        self.placeobj.add_placeref(self.placeref)

    def start_attribute(self, attrs):
        self.attribute = Attribute()
        self.attribute.private = bool(attrs.get("priv"))
        self.attribute.type = AttributeType()
        if "type" in attrs:
            self.attribute.type.set_from_xml_str(attrs["type"])
        self.attribute.value = attrs.get("value", "")
        if self.photo:
            self.photo.add_attribute(self.attribute)
        elif self.object:
            self.object.add_attribute(self.attribute)
        elif self.objref:
            self.objref.add_attribute(self.attribute)
        elif self.event:
            self.event.add_attribute(self.attribute)
        elif self.eventref:
            self.eventref.add_attribute(self.attribute)
        elif self.person:
            self.person.add_attribute(self.attribute)
        elif self.family:
            self.family.add_attribute(self.attribute)

    def start_srcattribute(self, attrs):
        self.srcattribute = SrcAttribute()
        self.srcattribute.private = bool(attrs.get("priv"))
        self.srcattribute.type = SrcAttributeType()
        if "type" in attrs:
            self.srcattribute.type.set_from_xml_str(attrs["type"])
        self.srcattribute.value = attrs.get("value", "")
        if self.source:
            self.source.add_attribute(self.srcattribute)
        elif self.citation:
            self.citation.add_attribute(self.srcattribute)

    def start_address(self, attrs):
        self.address = Address()
        self.address.private = bool(attrs.get("priv"))

    def start_bmark(self, attrs):
        """
        Add a bookmark to db.
        """
        target = attrs.get("target")
        if not target:
            # Old XML. Can be either handle or id reference
            # and this is guaranteed to be a person bookmark
            if "hlink" in attrs:
                handle = self.inaugurate(attrs["hlink"], "person", Person)
            else:
                handle = self.inaugurate_id(attrs.get("ref"), PERSON_KEY, Person)
            self.db.bookmarks.append(handle)
            return

        # This is new XML, so we are guaranteed to have a handle ref
        handle = attrs["hlink"].replace("_", "")
        handle = self.import_handles[handle][target][HANDLE]
        # Due to pre 2.2.9 bug, bookmarks might be handle of other object
        # Make sure those are filtered out.
        # Bookmarks are at end, so all handle must exist before we do bookmrks
        if target == "person":
            if (
                self.db.get_person_from_handle(handle) is not None
                and handle not in self.db.bookmarks.get()
            ):
                self.db.bookmarks.append(handle)
        elif target == "family":
            if (
                self.db.get_family_from_handle(handle) is not None
                and handle not in self.db.family_bookmarks.get()
            ):
                self.db.family_bookmarks.append(handle)
        elif target == "event":
            if (
                self.db.get_event_from_handle(handle) is not None
                and handle not in self.db.event_bookmarks.get()
            ):
                self.db.event_bookmarks.append(handle)
        elif target == "source":
            if (
                self.db.get_source_from_handle(handle) is not None
                and handle not in self.db.source_bookmarks.get()
            ):
                self.db.source_bookmarks.append(handle)
        elif target == "citation":
            if (
                self.db.get_citation_from_handle(handle) is not None
                and handle not in self.db.citation_bookmarks.get()
            ):
                self.db.citation_bookmarks.append(handle)
        elif target == "place":
            if (
                self.db.get_place_from_handle(handle) is not None
                and handle not in self.db.place_bookmarks.get()
            ):
                self.db.place_bookmarks.append(handle)
        elif target == "media":
            if (
                self.db.get_media_from_handle(handle) is not None
                and handle not in self.db.media_bookmarks.get()
            ):
                self.db.media_bookmarks.append(handle)
        elif target == "repository":
            if (
                self.db.get_repository_from_handle(handle) is not None
                and handle not in self.db.repo_bookmarks.get()
            ):
                self.db.repo_bookmarks.append(handle)
        elif target == "note":
            if (
                self.db.get_note_from_handle(handle) is not None
                and handle not in self.db.note_bookmarks.get()
            ):
                self.db.note_bookmarks.append(handle)

    def start_format(self, attrs):
        number = int(attrs["number"])
        name = attrs["name"]
        fmt_str = attrs["fmt_str"]
        active = bool(attrs.get("active", True))

        if number in self.taken_name_format_numbers:
            number = self.remap_name_format(number)

        self.name_formats.append((number, name, fmt_str, active))

    def remap_name_format(self, old_number):
        if old_number in self.name_formats_map:  # This should not happen
            return self.name_formats_map[old_number]
        # Find the lowest new number not taken yet:
        new_number = -1
        while new_number in self.taken_name_format_numbers:
            new_number -= 1
        # Add this to the taken list
        self.taken_name_format_numbers.append(new_number)
        # Set up the mapping entry
        self.name_formats_map[old_number] = new_number
        # Return new number
        return new_number

    def start_person(self, attrs):
        """
        Add a person to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.update(self.p.CurrentLineNumber)
        self.person = Person()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle and self.db.has_person_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "person", self.person)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                PERSON_KEY,
                self.idswap,
                self.db.id2user_format,
                self.db.find_next_person_gramps_id,
                self.db.has_person_gramps_id,
            )
            self.person.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_person = self.db.get_person_from_handle(orig_handle)
                self.info.add("merge-candidate", PERSON_KEY, orig_person, self.person)
        else:  # old style XML
            self.inaugurate_id(attrs.get("id"), PERSON_KEY, self.person)
        self.person.private = bool(attrs.get("priv"))
        self.person.change = int(attrs.get("change", self.change))
        self.info.add("new-object", PERSON_KEY, self.person)
        self.convert_marker(attrs, self.person)
        if self.default_tag:
            self.person.add_tag(self.default_tag.handle)
        return self.person

    def start_people(self, attrs):
        """
        Store the home person of the database.
        """
        if "home" in attrs:
            handle = self.inaugurate(attrs["home"], "person", Person)
            self.home = handle

    def start_father(self, attrs):
        """
        Add a father reference to the family currently processed.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "person", Person)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), PERSON_KEY, Person)
        self.family.set_father_handle(handle)

    def start_mother(self, attrs):
        """
        Add a mother reference to the family currently processed.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "person", Person)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), PERSON_KEY, Person)
        self.family.set_mother_handle(handle)

    def start_child(self, attrs):
        """
        Add a child reference to the family currently processed.

        Here we are handling the old XML, in which
        frel and mrel belonged to the "childof" tag
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "person", Person)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), PERSON_KEY, Person)

        # If that were the case then childref_map has the childref ready
        if (self.family.handle, handle) in self.childref_map:
            self.family.add_child_ref(self.childref_map[(self.family.handle, handle)])

    def start_childref(self, attrs):
        """
        Add a child reference to the family currently processed.

        Here we are handling the new XML, in which frel and mrel
        belong to the "childref" tag under family.
        """
        self.childref = ChildRef()
        handle = self.inaugurate(attrs["hlink"], "person", Person)
        self.childref.ref = handle
        self.childref.private = bool(attrs.get("priv"))

        mrel = ChildRefType()
        if attrs.get("mrel"):
            mrel.set_from_xml_str(attrs["mrel"])
        frel = ChildRefType()
        if attrs.get("frel"):
            frel.set_from_xml_str(attrs["frel"])

        if not mrel.is_default():
            self.childref.set_mother_relation(mrel)
        if not frel.is_default():
            self.childref.set_father_relation(frel)
        self.family.add_child_ref(self.childref)

    def start_personref(self, attrs):
        """
        Add a person reference to the person currently processed.
        """
        self.personref = PersonRef()
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "person", Person)
        else:  # there is no old style XML
            raise GrampsImportError(
                _("The Gramps Xml you are trying to " "import is malformed."),
                _("Any person reference must have a " "'hlink' attribute."),
            )
        self.personref.ref = handle
        self.personref.private = bool(attrs.get("priv"))
        self.personref.rel = attrs["rel"]
        self.person.add_person_ref(self.personref)

    def start_url(self, attrs):
        if "href" not in attrs:
            return
        url = Url()
        url.path = attrs["href"]
        url.set_description(attrs.get("description", ""))
        url.private = bool(attrs.get("priv"))
        url.type.set_from_xml_str(attrs.get("type", ""))
        if self.person:
            self.person.add_url(url)
        elif self.placeobj:
            self.placeobj.add_url(url)
        elif self.repo:
            self.repo.add_url(url)

    def start_family(self, attrs):
        """
        Add a family object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.update(self.p.CurrentLineNumber)
        self.family = Family()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle and self.db.has_family_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "family", self.family)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                FAMILY_KEY,
                self.fidswap,
                self.db.fid2user_format,
                self.db.find_next_family_gramps_id,
                self.db.has_family_gramps_id,
            )
            self.family.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_family = self.db.get_family_from_handle(orig_handle)
                self.info.add("merge-candidate", FAMILY_KEY, orig_family, self.family)
        else:  # old style XML
            self.inaugurate_id(attrs.get("id"), FAMILY_KEY, self.family)
        self.family.private = bool(attrs.get("priv"))
        self.family.change = int(attrs.get("change", self.change))
        self.info.add("new-object", FAMILY_KEY, self.family)
        # Gramps LEGACY: the type now belongs to <rel> tag
        # Here we need to support old format of <family type="Married">
        if "type" in attrs:
            self.family.type.set_from_xml_str(attrs["type"])
        self.convert_marker(attrs, self.family)
        if self.default_tag:
            self.family.add_tag(self.default_tag.handle)
        return self.family

    def start_rel(self, attrs):
        if "type" in attrs:
            self.family.type.set_from_xml_str(attrs["type"])

    def start_file(self, attrs):
        self.object.mime = attrs["mime"]
        if "description" in attrs:
            self.object.desc = attrs["description"]
        else:
            self.object.desc = ""
        # keep value of path, no longer make absolute paths on import
        src = attrs["src"]
        if src:
            self.object.path = src
            if self.all_abs and not os.path.isabs(src):
                self.all_abs = False
                self.info.add("relative-path", None, None)
        if "checksum" in attrs:
            self.object.checksum = attrs["checksum"]
        else:
            if os.path.isabs(src):
                full_path = src
            else:
                full_path = os.path.join(self.mediapath, src)
            self.object.checksum = create_checksum(full_path)

    def start_childof(self, attrs):
        """
        Add a family reference to the person currently processed in which that
        person is a child.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "family", Family)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), FAMILY_KEY, Family)

        # Here we are handling the old XML, in which
        # frel and mrel belonged to the "childof" tag
        mrel = ChildRefType()
        frel = ChildRefType()
        if "mrel" in attrs:
            mrel.set_from_xml_str(attrs["mrel"])
        if "frel" in attrs:
            frel.set_from_xml_str(attrs["frel"])

        childref = ChildRef()
        childref.ref = self.person.handle
        if not mrel.is_default():
            childref.set_mother_relation(mrel)
        if not frel.is_default():
            childref.set_father_relation(frel)
        self.childref_map[(handle, self.person.handle)] = childref
        self.person.add_parent_family_handle(handle)

    def start_parentin(self, attrs):
        """
        Add a family reference to the person currently processed in which that
        person is a parent.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "family", Family)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), FAMILY_KEY, Family)
        self.person.add_family_handle(handle)

    def start_name(self, attrs):
        if self.person:
            self.start_person_name(attrs)
        if self.placeobj:  # XML 1.7.0
            self.start_place_name(attrs)

    def start_place_name(self, attrs):
        self.place_name = PlaceName()
        self.place_name.set_value(attrs["value"])
        if "lang" in attrs:
            self.place_name.set_language(attrs["lang"])
        if self.place_names == 0:
            self.placeobj.set_name(self.place_name)
        else:
            self.placeobj.add_alternative_name(self.place_name)
        self.place_names += 1

    def start_person_name(self, attrs):
        if not self.in_witness:
            self.name = Name()
            name_type = attrs.get("type", "Birth Name")
            # Mapping "Other Name" from gramps 2.0.x to Unknown
            if (self.__xml_version == (1, 0, 0)) and (name_type == "Other Name"):
                self.name.set_type(NameType.UNKNOWN)
            else:
                self.name.type.set_from_xml_str(name_type)
            self.name.private = bool(attrs.get("priv", 0))
            self.alt_name = bool(attrs.get("alt", 0))
            try:
                sort_as = int(attrs["sort"])
                # check if these pointers need to be remapped
                # and set the name attributes
                if sort_as in self.name_formats_map:
                    self.name.sort_as = self.name_formats_map[sort_as]
                else:
                    self.name.sort_as = sort_as
            except KeyError:
                pass
            try:
                display_as = int(attrs["display"])
                # check if these pointers need to be remapped
                # and set the name attributes
                if display_as in self.name_formats_map:
                    self.name.display_as = self.name_formats_map[display_as]
                else:
                    self.name.display_as = display_as
            except KeyError:
                pass

    def start_surname(self, attrs):
        self.surname = Surname()
        self.surname.set_prefix(attrs.get("prefix", ""))
        self.surname.set_primary(attrs.get("prim", "1") == "1")
        self.surname.set_connector(attrs.get("connector", ""))
        origin_type = attrs.get("derivation", "")
        self.surname.origintype.set_from_xml_str(origin_type)

    def start_namemap(self, attrs):
        type = attrs.get("type")
        key = attrs["key"]
        value = attrs["value"]
        if type == "group_as":
            if self.db.has_name_group_key(key):
                present = self.db.get_name_group_mapping(key)
                if not value == present:
                    msg = _(
                        'Your Family Tree groups name "%(key)s" together'
                        ' with "%(parent)s", did not change this grouping to "%(value)s".'
                    ) % {"key": key, "parent": present, "value": value}
                    self.user.warn(_("Gramps ignored a name grouping"), msg)
            elif value != "None":  # None test fixes file corrupted by 11011
                self.db.set_name_group_mapping(key, value)

    def start_last(self, attrs):
        """This is the element in version < 1.4.0 to do the surname"""
        self.surname = Surname()
        self.surname.prefix = attrs.get("prefix", "")
        self.name.group_as = attrs.get("group", "")

    def start_patronymic(self, attrs):
        """This is the element in version < 1.4.0 to do the patronymic"""
        self.surnamepat = Surname()
        self.surnamepat.set_origintype(NameOriginType(NameOriginType.PATRONYMIC))

    def start_style(self, attrs):
        """
        Styled text tag in notes (v1.4.0 onwards).
        """
        tagtype = StyledTextTagType()
        tagtype.set_from_xml_str(attrs["name"].lower())
        try:
            val = attrs["value"]
            match = self.grampsuri.match(val)
            if match:
                target = {
                    "Person": "person",
                    "Family": "family",
                    "Event": "event",
                    "Place": "place",
                    "Source": "source",
                    "Citation": "citation",
                    "Repository": "repository",
                    "Media": "media",
                    "Note": "note",
                }[str(match.group("object_class"))]
                if match.group("handle") in self.import_handles:
                    if target in self.import_handles[match.group("handle")]:
                        val = "gramps://%s/handle/%s" % (
                            match.group("object_class"),
                            self.import_handles[match.group("handle")][target][HANDLE],
                        )
            tagvalue = StyledTextTagType.STYLE_TYPE[int(tagtype)](val)
        except KeyError:
            tagvalue = None
        except ValueError:
            return

        self.note_tags.append(StyledTextTag(tagtype, tagvalue))

    def start_tag(self, attrs):
        """
        Tag definition.
        """
        if self.note is not None:
            # Styled text tag in notes (prior to v1.4.0)
            self.start_style(attrs)
            return

        # Tag defintion
        self.tag = Tag()
        self.inaugurate(attrs["handle"], "tag", self.tag)
        self.tag.change = int(attrs.get("change", self.change))
        self.info.add("new-object", TAG_KEY, self.tag)
        self.tag.set_name(attrs.get("name", _("Unknown when imported")))
        self.tag.set_color(attrs.get("color", "#000000000000"))
        self.tag.set_priority(int(attrs.get("priority", 0)))
        return self.tag

    def stop_tag(self, *tag):
        if self.note is not None:
            # Styled text tag in notes (prior to v1.4.0)
            return
        self.db.commit_tag(self.tag, self.trans, self.tag.get_change_time())
        self.tag = None

    def start_tagref(self, attrs):
        """
        Tag reference in a primary object.
        """
        handle = self.inaugurate(attrs["hlink"], "tag", Tag)

        if self.person:
            self.person.add_tag(handle)

        if self.family:
            self.family.add_tag(handle)

        if self.object:
            self.object.add_tag(handle)

        if self.note:
            self.note.add_tag(handle)

        if self.event:
            self.event.add_tag(handle)

        if self.placeobj:
            self.placeobj.add_tag(handle)

        if self.repo:
            self.repo.add_tag(handle)

        if self.source:
            self.source.add_tag(handle)

        if self.citation:
            self.citation.add_tag(handle)

    def start_range(self, attrs):
        self.note_tags[-1].ranges.append((int(attrs["start"]), int(attrs["end"])))

    def start_note(self, attrs):
        """
        Add a note to db if it doesn't exist yet and assign
        id, privacy, changetime, format and type.
        """
        self.in_note = 0
        if "handle" in attrs:
            # This is new note, with ID and handle already existing
            self.update(self.p.CurrentLineNumber)
            self.note = Note()
            if "handle" in attrs:
                orig_handle = attrs["handle"].replace("_", "")
                is_merge_candidate = (
                    self.replace_import_handle and self.db.has_note_handle(orig_handle)
                )
                self.inaugurate(orig_handle, "note", self.note)
                gramps_id = self.legalize_id(
                    attrs.get("id"),
                    NOTE_KEY,
                    self.nidswap,
                    self.db.nid2user_format,
                    self.db.find_next_note_gramps_id,
                    self.db.has_note_gramps_id,
                )
                self.note.set_gramps_id(gramps_id)
                if is_merge_candidate:
                    orig_note = self.db.get_note_from_handle(orig_handle)
                    self.info.add("merge-candicate", NOTE_KEY, orig_note, self.note)
            else:
                self.inaugurate_id(attrs.get("id"), NOTE_KEY, self.note)
            self.note.private = bool(attrs.get("priv"))
            self.note.change = int(attrs.get("change", self.change))
            self.info.add("new-object", NOTE_KEY, self.note)
            self.note.format = int(attrs.get("format", Note.FLOWED))
            self.note.type.set_from_xml_str(attrs.get("type", NoteType.UNKNOWN))
            self.convert_marker(attrs, self.note)

            # Since StyledText was introduced (XML v1.3.0) the clear text
            # part of the note is moved between <text></text> tags.
            # To catch the different versions here we reset the note_text
            # variable. It will be checked in stop_note() then.
            self.note_text = None
            self.note_tags = []
        else:
            # Gramps LEGACY: old notes that were written inside other objects
            # We need to create a top-level note, it's type depends on
            #   the caller object, and inherits privacy from caller object
            # On stop_note the reference to this note will be added
            self.note = Note()
            self.note.handle = create_id()
            self.note.format = int(attrs.get("format", Note.FLOWED))
            # The order in this long if-then statement should reflect the
            # DTD: most deeply nested elements come first.
            if self.citation:
                self.note.type.set(NoteType.CITATION)
                self.note.private = self.citation.private
            elif self.address:
                self.note.type.set(NoteType.ADDRESS)
                self.note.private = self.address.private
            elif self.ord:
                self.note.type.set(NoteType.LDS)
                self.note.private = self.ord.private
            elif self.attribute:
                self.note.type.set(NoteType.ATTRIBUTE)
                self.note.private = self.attribute.private
            elif self.object:
                self.note.type.set(NoteType.MEDIA)
                self.note.private = self.object.private
            elif self.objref:
                self.note.type.set(NoteType.MEDIAREF)
                self.note.private = self.objref.private
            elif self.photo:
                self.note.type.set(NoteType.MEDIA)
                self.note.private = self.photo.private
            elif self.name:
                self.note.type.set(NoteType.PERSONNAME)
                self.note.private = self.name.private
            elif self.eventref:
                self.note.type.set(NoteType.EVENTREF)
                self.note.private = self.eventref.private
            elif self.reporef:
                self.note.type.set(NoteType.REPOREF)
                self.note.private = self.reporef.private
            elif self.source:
                self.note.type.set(NoteType.SOURCE)
                self.note.private = self.source.private
            elif self.event:
                self.note.type.set(NoteType.EVENT)
                self.note.private = self.event.private
            elif self.personref:
                self.note.type.set(NoteType.ASSOCIATION)
                self.note.private = self.personref.private
            elif self.person:
                self.note.type.set(NoteType.PERSON)
                self.note.private = self.person.private
            elif self.childref:
                self.note.type.set(NoteType.CHILDREF)
                self.note.private = self.childref.private
            elif self.family:
                self.note.type.set(NoteType.FAMILY)
                self.note.private = self.family.private
            elif self.placeobj:
                self.note.type.set(NoteType.PLACE)
                self.note.private = self.placeobj.private
            elif self.repo:
                self.note.type.set(NoteType.REPO)
                self.note.private = self.repo.private

            self.db.add_note(self.note, self.trans)
            # set correct change time
            self.db.commit_note(self.note, self.trans, self.change)
            self.info.add("new-object", NOTE_KEY, self.note)
        if self.default_tag:
            self.note.add_tag(self.default_tag.handle)
        return self.note

    def start_noteref(self, attrs):
        """
        Add a note reference to the object currently processed.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "note", Note)
        else:
            raise GrampsImportError(
                _("The Gramps Xml you are trying to " "import is malformed."),
                _("Any note reference must have a " "'hlink' attribute."),
            )

        # The order in this long if-then statement should reflect the
        # DTD: most deeply nested elements come first.
        if self.citation:
            self.citation.add_note(handle)
        elif self.address:
            self.address.add_note(handle)
        elif self.ord:
            self.ord.add_note(handle)
        elif self.attribute:
            self.attribute.add_note(handle)
        elif self.object:
            self.object.add_note(handle)
        elif self.objref:
            self.objref.add_note(handle)
        elif self.photo:
            self.photo.add_note(handle)
        elif self.name:
            self.name.add_note(handle)
        elif self.eventref:
            self.eventref.add_note(handle)
        elif self.reporef:
            self.reporef.add_note(handle)
        elif self.source:
            self.source.add_note(handle)
        elif self.event:
            self.event.add_note(handle)
        elif self.personref:
            self.personref.add_note(handle)
        elif self.person:
            self.person.add_note(handle)
        elif self.childref:
            self.childref.add_note(handle)
        elif self.family:
            self.family.add_note(handle)
        elif self.placeobj:
            self.placeobj.add_note(handle)
        elif self.repo:
            self.repo.add_note(handle)

    def __add_citation(self, citation_handle):
        """
        Add a citation to the object currently processed.
        """
        if self.photo:
            self.photo.add_citation(citation_handle)
        elif self.ord:
            self.ord.add_citation(citation_handle)
        elif self.attribute:
            self.attribute.add_citation(citation_handle)
        elif self.object:
            self.object.add_citation(citation_handle)
        elif self.objref:
            self.objref.add_citation(citation_handle)
        elif self.event:
            self.event.add_citation(citation_handle)
        elif self.eventref:
            self.eventref.add_citation(citation_handle)
        elif self.address:
            self.address.add_citation(citation_handle)
        elif self.name:
            self.name.add_citation(citation_handle)
        elif self.placeobj:
            self.placeobj.add_citation(citation_handle)
        elif self.childref:
            self.childref.add_citation(citation_handle)
        elif self.family:
            self.family.add_citation(citation_handle)
        elif self.personref:
            self.personref.add_citation(citation_handle)
        elif self.person:
            self.person.add_citation(citation_handle)

    def start_citationref(self, attrs):
        """
        Add a citation reference to the object currently processed.
        """
        handle = self.inaugurate(attrs["hlink"], "citation", Citation)

        self.__add_citation(handle)

    def start_citation(self, attrs):
        """
        Add a citation object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.update(self.p.CurrentLineNumber)
        self.citation = Citation()
        orig_handle = attrs["handle"].replace("_", "")
        is_merge_candidate = self.replace_import_handle and self.db.has_citation_handle(
            orig_handle
        )
        self.inaugurate(orig_handle, "citation", self.citation)
        gramps_id = self.legalize_id(
            attrs.get("id"),
            CITATION_KEY,
            self.cidswap,
            self.db.cid2user_format,
            self.db.find_next_citation_gramps_id,
            self.db.has_citation_gramps_id,
        )
        self.citation.set_gramps_id(gramps_id)
        if is_merge_candidate:
            orig_citation = self.db.get_citation_from_handle(orig_handle)
            self.info.add("merge-candidate", CITATION_KEY, orig_citation, self.citation)
        self.citation.private = bool(attrs.get("priv"))
        self.citation.change = int(attrs.get("change", self.change))
        self.citation.confidence = (
            self.conf if self.__xml_version >= (1, 5, 1) else 0
        )  # See bug# 7125
        self.info.add("new-object", CITATION_KEY, self.citation)
        if self.default_tag:
            self.citation.add_tag(self.default_tag.handle)
        return self.citation

    def start_sourceref(self, attrs):
        """
        Add a source reference to the object currently processed.
        """
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "source", Source)
        else:
            handle = self.inaugurate_id(attrs.get("ref"), SOURCE_KEY, Source)

        if self.citation:
            self.citation.set_reference_handle(handle)
        else:
            # Gramps LEGACY: Prior to v1.5.0 there were no citation objects.
            # We need to copy the contents of the old SourceRef into a new
            # Citation object.
            self.in_old_sourceref = True

            self.citation = Citation()
            self.citation.set_reference_handle(handle)
            self.citation.confidence = int(attrs.get("conf", self.conf))
            self.citation.private = bool(attrs.get("priv"))

            citation_handle = self.db.add_citation(self.citation, self.trans)
            self.__add_citation(citation_handle)

    def start_source(self, attrs):
        """
        Add a source object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.update(self.p.CurrentLineNumber)
        self.source = Source()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle and self.db.has_source_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "source", self.source)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                SOURCE_KEY,
                self.sidswap,
                self.db.sid2user_format,
                self.db.find_next_source_gramps_id,
                self.db.has_source_gramps_id,
            )
            self.source.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_source = self.db.get_source_from_handle(orig_handle)
                self.info.add("merge-candidate", SOURCE_KEY, orig_source, self.source)
        else:  # old style XML
            self.inaugurate_id(attrs.get("id"), SOURCE_KEY, self.source)
        self.source.private = bool(attrs.get("priv"))
        self.source.change = int(attrs.get("change", self.change))
        self.info.add("new-object", SOURCE_KEY, self.source)
        if self.default_tag:
            self.source.add_tag(self.default_tag.handle)
        return self.source

    def start_reporef(self, attrs):
        """
        Add a repository reference to the source currently processed.
        """
        self.reporef = RepoRef()
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "repository", Repository)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), REPOSITORY_KEY, Repository)
        self.reporef.ref = handle
        self.reporef.call_number = attrs.get("callno", "")
        if "medium" in attrs:
            self.reporef.media_type.set_from_xml_str(attrs["medium"])
        self.reporef.private = bool(attrs.get("priv"))
        # we count here on self.source being available
        # reporefs can only be found within source
        self.source.add_repo_reference(self.reporef)

    def start_objref(self, attrs):
        """
        Add a media object reference to the object currently processed.
        """
        self.objref = MediaRef()
        if "hlink" in attrs:
            handle = self.inaugurate(attrs["hlink"], "media", Media)
        else:  # old style XML
            handle = self.inaugurate_id(attrs.get("ref"), MEDIA_KEY, Media)
        self.objref.ref = handle
        self.objref.private = bool(attrs.get("priv"))
        if self.event:
            self.event.add_media_reference(self.objref)
        elif self.family:
            self.family.add_media_reference(self.objref)
        elif self.source:
            self.source.add_media_reference(self.objref)
        elif self.person:
            self.person.add_media_reference(self.objref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.objref)
        elif self.citation:
            self.citation.add_media_reference(self.objref)

    def start_region(self, attrs):
        rect = (
            int(attrs.get("corner1_x")),
            int(attrs.get("corner1_y")),
            int(attrs.get("corner2_x")),
            int(attrs.get("corner2_y")),
        )
        self.objref.set_rectangle(rect)

    def start_media(self, attrs):
        """
        Add a media object to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.object = Media()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle and self.db.has_media_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "media", self.object)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                MEDIA_KEY,
                self.oidswap,
                self.db.oid2user_format,
                self.db.find_next_media_gramps_id,
                self.db.has_media_gramps_id,
            )
            self.object.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_media = self.db.get_media_from_handle(orig_handle)
                self.info.add("merge-candidate", MEDIA_KEY, orig_media, self.object)
        else:
            self.inaugurate_id(attrs.get("id"), MEDIA_KEY, self.object)
        self.object.private = bool(attrs.get("priv"))
        self.object.change = int(attrs.get("change", self.change))
        self.info.add("new-object", MEDIA_KEY, self.object)

        # Gramps LEGACY: src, mime, and description attributes
        # now belong to the <file> tag. Here we are supporting
        # the old format of <object src="blah"...>
        self.object.mime = attrs.get("mime", "")
        self.object.desc = attrs.get("description", "")
        src = attrs.get("src", "")
        if src:
            self.object.path = src
        if self.default_tag:
            self.object.add_tag(self.default_tag.handle)
        return self.object

    def start_repo(self, attrs):
        """
        Add a repository to db if it doesn't exist yet and assign
        id, privacy and changetime.
        """
        self.repo = Repository()
        if "handle" in attrs:
            orig_handle = attrs["handle"].replace("_", "")
            is_merge_candidate = (
                self.replace_import_handle
                and self.db.has_repository_handle(orig_handle)
            )
            self.inaugurate(orig_handle, "repository", self.repo)
            gramps_id = self.legalize_id(
                attrs.get("id"),
                REPOSITORY_KEY,
                self.ridswap,
                self.db.rid2user_format,
                self.db.find_next_repository_gramps_id,
                self.db.has_repository_gramps_id,
            )
            self.repo.set_gramps_id(gramps_id)
            if is_merge_candidate:
                orig_repo = self.db.get_repository_from_handle(orig_handle)
                self.info.add("merge-candidate", REPOSITORY_KEY, orig_repo, self.repo)
        else:  # old style XML
            self.inaugurate_id(attrs.get("id"), REPOSITORY_KEY, self.repo)
        self.repo.private = bool(attrs.get("priv"))
        self.repo.change = int(attrs.get("change", self.change))
        self.info.add("new-object", REPOSITORY_KEY, self.repo)
        if self.default_tag:
            self.repo.add_tag(self.default_tag.handle)
        return self.repo

    def stop_people(self, *tag):
        pass

    def stop_database(self, *tag):
        self.update(self.p.CurrentLineNumber)

    def stop_media(self, *tag):
        self.db.commit_media(self.object, self.trans, self.object.get_change_time())
        self.object = None

    def stop_objref(self, *tag):
        self.objref = None

    def stop_repo(self, *tag):
        self.db.commit_repository(self.repo, self.trans, self.repo.get_change_time())
        self.repo = None

    def stop_reporef(self, *tag):
        self.reporef = None

    def start_photo(self, attrs):
        self.photo = Media()
        self.pref = MediaRef()
        self.pref.set_reference_handle(self.photo.get_handle())

        for key in list(attrs.keys()):
            if key == "descrip" or key == "description":
                self.photo.set_description(attrs[key])
            elif key == "priv":
                self.pref.set_privacy(int(attrs[key]))
                self.photo.set_privacy(int(attrs[key]))
            elif key == "src":
                src = attrs["src"]
                self.photo.set_path(src)
            else:
                attr = Attribute()
                attr.set_type(key)
                attr.set_value(attrs[key])
                self.photo.add_attribute(attr)
        self.photo.set_mime_type(get_type(self.photo.get_path()))
        self.db.add_media(self.photo, self.trans)
        # set correct change time
        self.db.commit_media(self.photo, self.trans, self.change)
        self.info.add("new-object", MEDIA_KEY, self.photo)
        if self.family:
            self.family.add_media_reference(self.pref)
        elif self.source:
            self.source.add_media_reference(self.pref)
        elif self.person:
            self.person.add_media_reference(self.pref)
        elif self.placeobj:
            self.placeobj.add_media_reference(self.pref)

    def start_daterange(self, attrs):
        self.start_compound_date(attrs, Date.MOD_RANGE)

    def start_datespan(self, attrs):
        self.start_compound_date(attrs, Date.MOD_SPAN)

    def start_compound_date(self, attrs, mode):
        if self.citation:
            date_value = self.citation.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        elif self.event:
            date_value = self.event.get_date_object()
        elif self.placeref:
            date_value = self.placeref.get_date_object()
        elif self.place_name:
            date_value = self.place_name.get_date_object()

        start = attrs["start"].split("-")
        stop = attrs["stop"].split("-")

        try:
            year = int(start[0])
        except ValueError:
            year = 0

        try:
            month = int(start[1])
        except:
            month = 0

        try:
            day = int(start[2])
        except:
            day = 0

        try:
            rng_year = int(stop[0])
        except:
            rng_year = 0

        try:
            rng_month = int(stop[1])
        except:
            rng_month = 0

        try:
            rng_day = int(stop[2])
        except:
            rng_day = 0

        if "cformat" in attrs:
            cal = Date.calendar_names.index(attrs["cformat"])
        else:
            cal = Date.CAL_GREGORIAN

        if "quality" in attrs:
            val = attrs["quality"]
            if val == "estimated":
                qual = Date.QUAL_ESTIMATED
            elif val == "calculated":
                qual = Date.QUAL_CALCULATED
            else:
                qual = Date.QUAL_NONE
        else:
            qual = Date.QUAL_NONE

        dualdated = False
        if "dualdated" in attrs:
            val = attrs["dualdated"]
            if val == "1":
                dualdated = True

        newyear = Date.NEWYEAR_JAN1
        if "newyear" in attrs:
            newyear = attrs["newyear"]
            if newyear.isdigit():
                newyear = int(newyear)
            else:
                newyear = Date.newyear_to_code(newyear)

        try:
            date_value.set(
                qual,
                mode,
                cal,
                (day, month, year, dualdated, rng_day, rng_month, rng_year, dualdated),
                newyear=newyear,
            )
        except DateError as e:
            self._set_date_to_xml_text(
                date_value,
                e,
                xml_element_name=("datespan" if mode == Date.MOD_SPAN else "daterange"),
                xml_attrs=attrs,
            )

    def start_dateval(self, attrs):
        if self.citation:
            date_value = self.citation.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        elif self.event:
            date_value = self.event.get_date_object()
        elif self.placeref:
            date_value = self.placeref.get_date_object()
        elif self.place_name:
            date_value = self.place_name.get_date_object()

        bce = 1
        val = attrs["val"]
        if val[0] == "-":
            bce = -1
            val = val[1:]
        start = val.split("-")
        try:
            year = int(start[0]) * bce
        except:
            year = 0

        try:
            month = int(start[1])
        except:
            month = 0

        try:
            day = int(start[2])
        except:
            day = 0

        if "cformat" in attrs:
            cal = Date.calendar_names.index(attrs["cformat"])
        else:
            cal = Date.CAL_GREGORIAN

        if "type" in attrs:
            val = attrs["type"]
            if val == "about":
                mod = Date.MOD_ABOUT
            elif val == "after":
                mod = Date.MOD_AFTER
            elif val == "before":
                mod = Date.MOD_BEFORE
            elif val == "from":
                mod = Date.MOD_FROM
            else:
                mod = Date.MOD_TO
        else:
            mod = Date.MOD_NONE

        if "quality" in attrs:
            val = attrs["quality"]
            if val == "estimated":
                qual = Date.QUAL_ESTIMATED
            elif val == "calculated":
                qual = Date.QUAL_CALCULATED
            else:
                qual = Date.QUAL_NONE
        else:
            qual = Date.QUAL_NONE

        dualdated = False
        if "dualdated" in attrs:
            val = attrs["dualdated"]
            if val == "1":
                dualdated = True

        newyear = Date.NEWYEAR_JAN1
        if "newyear" in attrs:
            newyear = attrs["newyear"]
            if newyear.isdigit():
                newyear = int(newyear)
            else:
                newyear = Date.newyear_to_code(newyear)

        try:
            date_value.set(
                qual, mod, cal, (day, month, year, dualdated), newyear=newyear
            )
        except DateError as e:
            self._set_date_to_xml_text(date_value, e, "dateval", attrs)

    def _set_date_to_xml_text(
        self, date_value, date_error, xml_element_name, xml_attrs
    ):
        """
        Common handling of invalid dates for the date... element handlers.

        Prints warning on console and sets date_value to a text-only date
        with the problematic XML inside.
        """
        xml = "<{element_name} {attrs}/>".format(
            element_name=xml_element_name,
            attrs=" ".join(
                [
                    '{}="{}"'.format(k, escape(v, entities={'"': "&quot;"}))
                    for k, v in xml_attrs.items()
                ]
            ),
        )
        # Translators: leave the {date} and {xml} untranslated in the format string,
        # but you may re-order them if needed.
        LOG.warning(
            _("Invalid date {date} in XML {xml}, preserving XML as text").format(
                date=date_error.date.__dict__, xml=xml
            )
        )
        date_value.set(modifier=Date.MOD_TEXTONLY, text=xml)

    def start_datestr(self, attrs):
        if self.citation:
            date_value = self.citation.get_date_object()
        elif self.ord:
            date_value = self.ord.get_date_object()
        elif self.object:
            date_value = self.object.get_date_object()
        elif self.address:
            date_value = self.address.get_date_object()
        elif self.name:
            date_value = self.name.get_date_object()
        elif self.event:
            date_value = self.event.get_date_object()
        elif self.placeref:
            date_value = self.placeref.get_date_object()
        else:
            date_value = self.place_name.get_date_object()

        date_value.set_as_text(attrs["val"])

    def start_pos(self, attrs):
        self.person.position = (int(attrs["x"]), int(attrs["y"]))

    def stop_attribute(self, *tag):
        self.attribute = None

    def stop_srcattribute(self, *tag):
        self.srcattribute = None

    def stop_comment(self, tag):
        # Parse witnesses created by older gramps
        if tag.strip():
            self.witness_comment = tag
        else:
            self.witness_comment = ""

    def stop_witness(self, tag):
        # Parse witnesses created by older gramps
        if self.witness_comment:
            text = self.witness_comment
        elif tag.strip():
            text = tag
        else:
            text = None

        if text is not None:
            note = Note()
            note.handle = create_id()
            note.set(_("Witness comment: %s") % text)
            note.type.set(NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            # set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add("new-object", NOTE_KEY, note)
            self.event.add_note(note.handle)
        self.in_witness = False

    def stop_attr_type(self, tag):
        self.attribute.set_type(tag)

    def stop_attr_value(self, tag):
        self.attribute.set_value(tag)

    def stop_address(self, *tag):
        if self.person:
            self.person.add_address(self.address)
        elif self.repo:
            self.repo.add_address(self.address)
        self.address = None

    def stop_places(self, *tag):
        self.placeobj = None

        if self.__xml_version < (1, 6, 0):
            self.place_import.generate_hierarchy(self.trans)

    def stop_photo(self, *tag):
        self.photo = None

    def stop_ptitle(self, tag):
        self.placeobj.title = tag

    def stop_code(self, tag):
        self.placeobj.code = tag

    def stop_alt_name(self, tag):
        place_name = PlaceName()
        place_name.set_value(tag)
        self.placeobj.add_alternative_name(place_name)

    def stop_placeobj(self, *tag):
        if self.placeobj.name.get_value() == "":
            self.placeobj.name.set_value(self.placeobj.title)
        self.db.commit_place(self.placeobj, self.trans, self.placeobj.get_change_time())
        self.placeobj = None

    def stop_family(self, *tag):
        self.db.commit_family(self.family, self.trans, self.family.get_change_time())
        self.family = None

    def stop_type(self, tag):
        if self.event:
            # Event type
            self.event.type.set_from_xml_str(tag)
        elif self.repo:
            # Repository type
            self.repo.type.set_from_xml_str(tag)

    def stop_childref(self, tag):
        self.childref = None

    def stop_personref(self, tag):
        self.personref = None

    def stop_eventref(self, tag):
        self.eventref = None

    def stop_placeref(self, tag):
        self.placeref = None

    def stop_event(self, *tag):
        if self.family:
            ref = EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(EventRoleType.FAMILY)
            self.family.add_event_ref(ref)
        elif self.person:
            ref = EventRef()
            ref.ref = self.event.handle
            ref.private = self.event.private
            ref.role.set(EventRoleType.PRIMARY)
            if (self.event.type == EventType.BIRTH) and (
                self.person.get_birth_ref() is None
            ):
                self.person.set_birth_ref(ref)
            elif (self.event.type == EventType.DEATH) and (
                self.person.get_death_ref() is None
            ):
                self.person.set_death_ref(ref)
            else:
                self.person.add_event_ref(ref)

        if (
            self.event.get_description() == ""
            and self.event.get_type() != EventType.CUSTOM
        ):
            if self.family:
                text = EVENT_FAMILY_STR % {
                    "event_name": str(self.event.get_type()),
                    "family": family_name(self.family, self.db),
                }
            elif self.person:
                text = EVENT_PERSON_STR % {
                    "event_name": str(self.event.get_type()),
                    "person": name_displayer.display(self.person),
                }
            else:
                text = ""
            self.event.set_description(text)

        self.db.commit_event(self.event, self.trans, self.event.get_change_time())
        self.event = None

    def stop_name(self, attrs):
        if self.person:
            self.stop_person_name(attrs)
        if self.placeobj:  # XML 1.7.0
            self.stop_place_name(attrs)

    def stop_place_name(self, tag):
        self.place_name = None

    def stop_person_name(self, tag):
        if self.in_witness:
            # Parse witnesses created by older gramps
            note = Note()
            note.handle = create_id()
            note.set(_("Witness name: %s") % tag)
            note.type.set(NoteType.EVENT)
            note.private = self.event.private
            self.db.add_note(note, self.trans)
            # set correct change time
            self.db.commit_note(note, self.trans, self.change)
            self.info.add("new-object", NOTE_KEY, note)
            self.event.add_note(note.handle)
        else:
            # first correct old xml that has no nametype set
            if self.alt_name:
                # alternate name or former aka tag
                if self.name.get_type() == "":
                    self.name.set_type(NameType.AKA)
            else:
                if self.name.get_type() == "":
                    self.name.set_type(NameType.BIRTH)

            # same logic as bsddb upgrade for xml < 1.4.0 which will
            # have a surnamepat and/or surname. From 1.4.0 surname has been
            # added to name in self.stop_surname
            if not self.surnamepat:
                # no patronymic, only add surname if present
                if self.surname:
                    self.name.add_surname(self.surname)
                    self.name.set_primary_surname(0)
            else:
                # a patronymic, if no surname, a single surname
                if not self.surname:
                    self.name.add_surname(self.surnamepat)
                    self.name.set_primary_surname(0)
                else:
                    # two surnames, first patronymic, then surname which is primary
                    self.name.add_surname(self.surnamepat)
                    self.name.add_surname(self.surname)
                    self.name.set_primary_surname(1)
            if self.alt_name:
                self.person.add_alternate_name(self.name)
            else:
                self.person.set_primary_name(self.name)
        self.name = None
        self.surname = None
        self.surnamepat = None

    def stop_aka(self, tag):
        if self.name.get_type() == "":
            self.name.set_type(NameType.AKA)
        if not self.surnamepat:
            # no patronymic, only add surname if present
            if self.surname:
                self.name.add_surname(self.surname)
                self.name.set_primary_surname(0)
        else:
            # a patronymic, if no surname, a single surname
            if not self.surname:
                self.name.add_surname(self.surnamepat)
                self.name.set_primary_surname(0)
            else:
                # two surnames, first patronymic, then surname which is primary
                self.name.add_surname(self.surnamepat)
                self.name.add_surname(self.surname)
                self.name.set_primary_surname(1)
        self.person.add_alternate_name(self.name)
        self.name = None

    def stop_rname(self, tag):
        # Repository name
        self.repo.name = tag

    def stop_ref(self, tag):
        """
        Parse witnesses created by older gramps
        """
        person = Person()
        self.inaugurate_id(tag, PERSON_KEY, person)
        # Add an EventRef from that person
        # to this event using ROLE_WITNESS role
        event_ref = EventRef()
        event_ref.ref = self.event.handle
        event_ref.role.set(EventRoleType.WITNESS)
        person.event_ref_list.append(event_ref)
        self.db.commit_person(person, self.trans, self.change)

    def stop_place(self, tag):
        """end of a reference to place, should do nothing ...
        Note, if we encounter <place>blabla</place> this method is called
             with tag='blabla
        """
        ##place = None
        ##handle = None
        ##if self.place_ref is None:  #todo, add place_ref in start and init
        ##    #legacy cody? I see no reason for this, but it was present
        ##    if tag in self.place_map:
        ##        place = self.place_map[tag]
        ##        handle = place.get_handle()
        ##        place = None
        ##    else:
        ##        place = RelLib.Place()
        ##        place.set_title(tag)
        ##        handle = place.get_handle()
        ##    if self.ord:
        ##        self.ord.set_place_handle(handle)
        ##    elif self.object:
        ##        self.object.set_place_handle(handle)
        ##    else:
        ##        self.event.set_place_handle(handle)
        ##    if place :
        ##        self.db.commit_place(self.placeobj,self.trans,self.change)
        ##self.place_ref = None
        pass

    def stop_date(self, tag):
        if tag:
            if self.address:
                set_date(self.address, tag)
            else:
                set_date(self.event, tag)

    def stop_first(self, tag):
        # bug 9242
        if len(tag.splitlines()) != 1:
            tag = "".join(tag.splitlines())
        self.name.set_first_name(tag)

    def stop_call(self, tag):
        self.name.set_call_name(tag)

    def stop_families(self, *tag):
        self.family = None

    def stop_person(self, *tag):
        self.db.commit_person(self.person, self.trans, self.person.get_change_time())
        self.person = None

    def stop_description(self, tag):
        self.event.set_description(tag)

    def stop_cause(self, tag):
        # The old event's cause is now an attribute
        attr = Attribute()
        attr.set_type(AttributeType.CAUSE)
        attr.set_value(tag)
        self.event.add_attribute(attr)

    def stop_gender(self, tag):
        t = tag
        if t == "M":
            self.person.set_gender(Person.MALE)
        elif t == "F":
            self.person.set_gender(Person.FEMALE)
        elif t == "X":
            self.person.set_gender(Person.OTHER)
        else:
            self.person.set_gender(Person.UNKNOWN)

    def stop_stitle(self, tag):
        self.source.title = tag

    def stop_sourceref(self, *tag):
        # if we are in an old style sourceref we need to commit the citation
        if self.in_old_sourceref:
            self.db.commit_citation(
                self.citation, self.trans, self.citation.get_change_time()
            )
            self.citation = None
            self.in_old_sourceref = False

    def stop_source(self, *tag):
        self.db.commit_source(self.source, self.trans, self.source.get_change_time())
        self.source = None

    def stop_citation(self, *tag):
        self.db.commit_citation(
            self.citation, self.trans, self.citation.get_change_time()
        )
        self.citation = None

    def stop_sauthor(self, tag):
        self.source.author = tag

    def stop_phone(self, tag):
        self.address.phone = tag

    def stop_street(self, tag):
        self.address.street = tag

    def stop_locality(self, tag):
        self.address.locality = tag

    def stop_city(self, tag):
        self.address.city = tag

    def stop_county(self, tag):
        self.address.county = tag

    def stop_state(self, tag):
        self.address.state = tag

    def stop_country(self, tag):
        self.address.country = tag

    def stop_postal(self, tag):
        self.address.set_postal_code(tag)

    def stop_spage(self, tag):
        # Valid for version <= 1.4.0
        self.citation.set_page(tag)

    def stop_page(self, tag):
        # Valid for version >= 1.5.0
        self.citation.set_page(tag)

    def stop_confidence(self, tag):
        # Valid for version >= 1.5.0
        self.citation.set_confidence_level(int(tag))

    def stop_lds_ord(self, *tag):
        self.ord = None

    def stop_spubinfo(self, tag):
        self.source.set_publication_info(tag)

    def stop_sabbrev(self, tag):
        self.source.set_abbreviation(tag)

    def stop_stext(self, tag):
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.stext_list)
        else:
            text = tag
        # This is old XML. We no longer have "text" attribute in soure_ref.
        # So we create a new note, commit, and add the handle to note list.
        note = Note()
        note.handle = create_id()
        note.private = self.citation.private
        note.set(text)
        note.type.set(NoteType.SOURCE_TEXT)
        self.db.add_note(note, self.trans)
        # set correct change time
        self.db.commit_note(note, self.trans, self.change)
        self.info.add("new-object", NOTE_KEY, note)
        self.citation.add_note(note.handle)

    def stop_scomments(self, tag):
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.scomments_list)
        else:
            text = tag
        note = Note()
        note.handle = create_id()
        note.private = self.citation.private
        note.set(text)
        note.type.set(NoteType.CITATION)
        self.db.add_note(note, self.trans)
        # set correct change time
        self.db.commit_note(note, self.trans, self.change)
        self.info.add("new-object", NOTE_KEY, note)
        self.citation.add_note(note.handle)

    def stop_last(self, tag):
        if self.surname:
            self.surname.set_surname(tag)
        if not tag.strip() and not self.surname.get_prefix().strip():
            # consider empty surname as no surname
            self.surname = None

    def stop_surname(self, tag):
        """Add surname to name, validating only one primary."""
        if self.name:
            self.surname.set_surname(tag)
            if any(sname.get_primary() for sname in self.name.get_surname_list()):
                self.surname.set_primary(False)
            self.name.add_surname(self.surname)
        self.surname = None

    def stop_group(self, tag):
        """group name of a name"""
        if self.name:
            self.name.set_group_as(tag)

    def stop_suffix(self, tag):
        if self.name:
            self.name.set_suffix(tag)

    def stop_patronymic(self, tag):
        if self.surnamepat:
            self.surnamepat.set_surname(tag)
        if not tag.strip():
            self.surnamepat = None

    def stop_title(self, tag):
        if self.name:
            self.name.set_title(tag)

    def stop_nick(self, tag):
        """in < 1.3.0 nick is on person and mapped to attribute
        from 1.4.0 it is a name element
        """
        if self.name:
            self.name.set_nick_name(tag)
        elif self.person:
            attr = Attribute()
            attr.set_type(AttributeType.NICKNAME)
            attr.set_value(tag)
            self.person.add_attribute(attr)

    def stop_familynick(self, tag):
        if self.name:
            self.name.set_family_nick_name(tag)

    def stop_text(self, tag):
        self.note_text = tag

    def stop_note(self, tag):
        self.in_note = 0
        if self.use_p:
            self.use_p = 0
            text = fix_spaces(self.note_list)
        elif self.note_text is not None:
            text = self.note_text
        else:
            text = tag

        self.note.set_styledtext(StyledText(text, self.note_tags))

        # The order in this long if-then statement should reflect the
        # DTD: most deeply nested elements come first.
        if self.address:
            self.address.add_note(self.note.handle)
        elif self.ord:
            self.ord.add_note(self.note.handle)
        elif self.attribute:
            self.attribute.add_note(self.note.handle)
        elif self.object:
            self.object.add_note(self.note.handle)
        elif self.objref:
            self.objref.add_note(self.note.handle)
        elif self.photo:
            self.photo.add_note(self.note.handle)
        elif self.name:
            self.name.add_note(self.note.handle)
        elif self.eventref:
            self.eventref.add_note(self.note.handle)
        elif self.reporef:
            self.reporef.add_note(self.note.handle)
        elif self.source:
            self.source.add_note(self.note.handle)
        elif self.event:
            self.event.add_note(self.note.handle)
        elif self.personref:
            self.personref.add_note(self.note.handle)
        elif self.person:
            self.person.add_note(self.note.handle)
        elif self.childref:
            self.childref.add_note(self.note.handle)
        elif self.family:
            self.family.add_note(self.note.handle)
        elif self.placeobj:
            self.placeobj.add_note(self.note.handle)
        elif self.repo:
            self.repo.add_note(self.note.handle)

        self.db.commit_note(self.note, self.trans, self.note.get_change_time())
        self.note = None

    def stop_note_asothers(self, *tag):
        self.db.commit_note(self.note, self.trans, self.note.get_change_time())
        self.note = None

    def stop_research(self, tag):
        self.owner.set_name(self.resname)
        self.owner.set_address(self.resaddr)
        self.owner.set_locality(self.reslocality)
        self.owner.set_city(self.rescity)
        self.owner.set_state(self.resstate)
        self.owner.set_country(self.rescon)
        self.owner.set_postal_code(self.respos)
        self.owner.set_phone(self.resphone)
        self.owner.set_email(self.resemail)

    def stop_resname(self, tag):
        self.resname = tag

    def stop_resaddr(self, tag):
        self.resaddr = tag

    def stop_reslocality(self, tag):
        self.reslocality = tag

    def stop_rescity(self, tag):
        self.rescity = tag

    def stop_resstate(self, tag):
        self.resstate = tag

    def stop_rescountry(self, tag):
        self.rescon = tag

    def stop_respostal(self, tag):
        self.respos = tag

    def stop_resphone(self, tag):
        self.resphone = tag

    def stop_resemail(self, tag):
        self.resemail = tag

    def stop_mediapath(self, tag):
        self.mediapath = tag

    def stop_ptag(self, tag):
        self.use_p = 1
        if self.in_note:
            self.note_list.append(tag)
        elif self.in_stext:
            self.stext_list.append(tag)
        elif self.in_scomments:
            self.scomments_list.append(tag)

    def startElement(self, tag, attrs):
        self.func_list[self.func_index] = (self.func, self.tlist)
        self.func_index += 1
        self.tlist = []

        try:
            f, self.func = self.func_map[tag]
            if f:
                f(attrs)
        except KeyError:
            self.func_map[tag] = (None, None)
            self.func = None

    def endElement(self, tag):
        if self.func:
            self.func("".join(self.tlist))
        self.func_index -= 1
        self.func, self.tlist = self.func_list[self.func_index]

    def characters(self, data):
        if self.func:
            self.tlist.append(data)

    def convert_marker(self, attrs, obj):
        """
        Convert markers into tags.

        Old and new markers: complete=1 and marker=word
        """
        if attrs.get("complete"):  # this is only true for complete=1
            tag_name = "Complete"
        else:
            tag_name = attrs.get("marker")

        if tag_name is not None:
            tag_name = _(tag_name)
            tag = self.db.get_tag_from_name(tag_name)
            if tag is None:
                tag = Tag()
                tag.set_name(tag_name)
                tag.set_priority(self.db.get_number_of_tags())
                tag_handle = self.db.add_tag(tag, self.trans)
            else:
                tag_handle = tag.get_handle()
            obj.add_tag(tag_handle)

    def fix_not_instantiated(self):
        uninstantiated = []
        for orig_handle in self.import_handles.keys():
            tglist = [
                target
                for target in self.import_handles[orig_handle].keys()
                if not self.import_handles[orig_handle][target][INSTANTIATED]
            ]
            for target in tglist:
                uninstantiated += [(orig_handle, target)]
        if uninstantiated:
            expl_note = create_explanation_note(self.db)
            self.db.commit_note(expl_note, self.trans, time.time())
            self.info.expl_note = expl_note.get_gramps_id()
            for orig_handle, target in uninstantiated:
                class_arg = {"handle": orig_handle, "id": None, "priv": False}
                if target == "family":
                    objs = make_unknown(
                        class_arg,
                        expl_note.handle,
                        self.func_map[target][0],
                        self.func_map[target][1],
                        self.trans,
                        db=self.db,
                    )
                elif target == "citation":
                    objs = make_unknown(
                        class_arg,
                        expl_note.handle,
                        self.func_map[target][0],
                        self.func_map[target][1],
                        self.trans,
                        source_class_func=self.func_map["source"][0],
                        source_commit_func=self.func_map["source"][1],
                        source_class_arg={
                            "handle": create_id(),
                            "id": None,
                            "priv": False,
                        },
                    )
                elif target == "note":
                    objs = make_unknown(
                        class_arg,
                        expl_note.handle,
                        self.func_map[target][0],
                        self.stop_note_asothers,
                        self.trans,
                    )
                else:
                    if target == "place":
                        target = "placeobj"
                    elif target == "media":
                        target = "object"
                    objs = make_unknown(
                        class_arg,
                        expl_note.handle,
                        self.func_map[target][0],
                        self.func_map[target][1],
                        self.trans,
                    )
                for obj in objs:
                    key = CLASS_TO_KEY_MAP[obj.__class__.__name__]
                    self.info.add("unknown-object", key, obj)

    def fix_families(self):
        # Fix any imported families where there is a link from the family to an
        # individual, but no corresponding link from the individual to the
        # family.
        for orig_handle in list(self.import_handles.keys()):
            for target in list(self.import_handles[orig_handle].keys()):
                if target == "family":
                    family_handle = self.import_handles[orig_handle][target][HANDLE]
                    family = self.db.get_family_from_handle(family_handle)
                    father_handle = family.get_father_handle()
                    mother_handle = family.get_mother_handle()

                    if father_handle:
                        father = self.db.get_person_from_handle(father_handle)
                        if (
                            father
                            and family_handle not in father.get_family_handle_list()
                        ):
                            father.add_family_handle(family_handle)
                            self.db.commit_person(father, self.trans)
                            txt = _(
                                "Error: family '%(family)s'"
                                " father '%(father)s'"
                                " does not refer"
                                " back to the family."
                                " Reference added."
                                % {
                                    "family": family.gramps_id,
                                    "father": father.gramps_id,
                                }
                            )
                            self.info.add("unlinked-family", txt, None)
                            LOG.warning(txt)

                    if mother_handle:
                        mother = self.db.get_person_from_handle(mother_handle)
                        if (
                            mother
                            and family_handle not in mother.get_family_handle_list()
                        ):
                            mother.add_family_handle(family_handle)
                            self.db.commit_person(mother, self.trans)
                            txt = _(
                                "Error: family '%(family)s'"
                                " mother '%(mother)s'"
                                " does not refer"
                                " back to the family."
                                " Reference added."
                                % {
                                    "family": family.gramps_id,
                                    "mother": mother.gramps_id,
                                }
                            )
                            self.info.add("unlinked-family", txt, None)
                            LOG.warning(txt)

                    for child_ref in family.get_child_ref_list():
                        child_handle = child_ref.ref
                        child = self.db.get_person_from_handle(child_handle)
                        if child:
                            if (
                                family_handle
                                not in child.get_parent_family_handle_list()
                            ):
                                # The referenced child has no reference to the
                                # family. There was a link from the FAM record
                                # to the child, but no FAMC link from the child
                                # to the FAM.
                                child.add_parent_family_handle(family_handle)
                                self.db.commit_person(child, self.trans)
                                txt = _(
                                    "Error: family '%(family)s'"
                                    " child '%(child)s'"
                                    " does not "
                                    "refer back to the family. "
                                    "Reference added."
                                    % {
                                        "family": family.gramps_id,
                                        "child": child.gramps_id,
                                    }
                                )
                                self.info.add("unlinked-family", txt, None)
                                LOG.warning(txt)


def append_value(orig, val):
    if orig:
        return "%s, %s" % (orig, val)
    else:
        return val


def build_place_title(loc):
    "Builds a title from a location"
    value = ""
    if loc.parish:
        value = loc.parish
    if loc.city:
        value = append_value(value, loc.city)
    if loc.county:
        value = append_value(value, loc.county)
    if loc.state:
        value = append_value(value, loc.state)
    if loc.country:
        value = append_value(value, loc.country)
    return value
