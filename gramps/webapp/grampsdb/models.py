# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  B. Malengier <benny.malengier@gmail.com>
# Copyright (C) 2009  Douglas S. Blank <doug.blank@gmail.com>
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
All of the models for the grampsdb Django data schema.
This requires initial data for all of the Types, which
is loaded by the fixtures/initial_data.json, which is
created by init.py.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from gramps.gen.lib.date import Date as GDate, Today
from gramps.gen.utils.id import create_id, create_uid

from gramps.webapp.grampsdb.profile import Profile

import pickle
import base64

#---------------------------------------------------------------------------
#
# Support functions
#
#---------------------------------------------------------------------------

def get_type_from_name(the_type, name):
    """
    Gets the type for a given name.
    >>> get_type_from_name(GenderType, "Female")
    <GenderType: Female>
    >>> get_type_from_name(GenderType, "Male")
    <GenderType: Male>
    """
    return the_type.objects.get(name=name)

def get_type(the_type, data, get_or_create=False):
    """
    Gets the default row for a given Type and data. Data is
    a pair, (VAL, NAME). VAL + NAME should be unique. Will create
    one if it doesn't already exist.
    """
    if type(data) == type(1):
        return the_type.objects.get(val=data)
    elif data[0] == the_type._CUSTOM or get_or_create:
        (obj, new) = the_type.objects.get_or_create(val=data[0],
                                                    name=data[1])
        return obj
    else:
        return the_type.objects.get(val=data[0])

def get_default_type(the_type):
    """
    Gets the default database object for a given GrampsType.
    """
    val, name = the_type._DEFAULT
    return the_type.objects.get(val=val, name=name)

def get_default_type_value(the_type):
    """
    Gets the default value for a given gen.lib.GrampsType.
    """
    return [x for x in the_type._DATAMAP if x[0] == the_type._DEFAULT][0]

def get_datamap(grampsclass):
    return sorted([(x[0],x[2]) for x in grampsclass._DATAMAP],
                  key=lambda item: item[1])

#---------------------------------------------------------------------------
#
# Types
#
#---------------------------------------------------------------------------

class mGrampsType(models.Model):
    """
    The abstract base class for all types.
    Types are enumerated integers. One integer corresponds with custom, then
    custom_type holds the type name
    """
    class Meta: abstract = True

    _CUSTOM = 0
    _DEFAULT = 0
    _DATAMAP = []

    name = models.CharField(max_length=40)

    def __str__(self):
        return str(self.name)

    def get_default_type(self):
        """ return a tuple default (val,name) """
        return self._DEFAULT

    def __len__(self):
        """ For use as a sequence for getting (val, name) """
        return 2

    def __getitem__(self, pos):
        """ for getting the parts as if they were the original tuples."""
        if pos == 0:
            return self.val
        elif pos == 1:
            return self.name
        else:
            raise IndexError("type index is out of range (use 0 or 1)")

class NameType(mGrampsType):
    from gramps.gen.lib.nametype import NameType
    _DATAMAP = get_datamap(NameType)
    _CUSTOM = NameType._CUSTOM
    _DEFAULT = get_default_type_value(NameType)
    val = models.IntegerField('name type', choices=_DATAMAP, blank=False)

class NameOriginType(mGrampsType):
    from gramps.gen.lib.nameorigintype import NameOriginType
    _DATAMAP = get_datamap(NameOriginType)
    _CUSTOM = NameOriginType._CUSTOM
    _DEFAULT = get_default_type_value(NameOriginType)
    val = models.IntegerField('name origin type', choices=_DATAMAP, blank=False)

class AttributeType(mGrampsType):
    from gramps.gen.lib.attrtype import AttributeType
    _DATAMAP = get_datamap(AttributeType)
    _CUSTOM = AttributeType._CUSTOM
    _DEFAULT = get_default_type_value(AttributeType)
    val = models.IntegerField('attribute type', choices=_DATAMAP, blank=False)

class UrlType(mGrampsType):
    from gramps.gen.lib.urltype import UrlType
    _DATAMAP = get_datamap(UrlType)
    _CUSTOM = UrlType._CUSTOM
    _DEFAULT = get_default_type_value(UrlType)
    val = models.IntegerField('url type', choices=_DATAMAP, blank=False)

class ChildRefType(mGrampsType):
    from gramps.gen.lib.childreftype import ChildRefType
    _DATAMAP = get_datamap(ChildRefType)
    _CUSTOM = ChildRefType._CUSTOM
    _DEFAULT = get_default_type_value(ChildRefType)
    val = models.IntegerField('child reference type', choices=_DATAMAP,
                              blank=False)

class RepositoryType(mGrampsType):
    from gramps.gen.lib.repotype import RepositoryType
    _DATAMAP = get_datamap(RepositoryType)
    _CUSTOM = RepositoryType._CUSTOM
    _DEFAULT = get_default_type_value(RepositoryType)
    val = models.IntegerField('repository type', choices=_DATAMAP, blank=False)

class PlaceType(mGrampsType):
    from gramps.gen.lib.placetype import PlaceType
    _DATAMAP = get_datamap(PlaceType)
    _CUSTOM = PlaceType._CUSTOM
    _DEFAULT = get_default_type_value(PlaceType)
    val = models.IntegerField('place type', choices=_DATAMAP, blank=False)

class EventType(mGrampsType):
    from gramps.gen.lib.eventtype import EventType
    _DATAMAP = get_datamap(EventType)
    _CUSTOM = EventType._CUSTOM
    _DEFAULT = get_default_type_value(EventType)
    BIRTH = 12
    DEATH = 13
    val = models.IntegerField('event type', choices=_DATAMAP, blank=False)

    def get_url(self):
        return "/event/?search=type%%3D%s" % self.name

    def get_link(self):
        return "<a href='%s'>%s</a>" % (self.get_url(), self.name)


class FamilyRelType(mGrampsType):
    from gramps.gen.lib.familyreltype import FamilyRelType
    _DATAMAP = get_datamap(FamilyRelType)
    _CUSTOM = FamilyRelType._CUSTOM
    _DEFAULT = get_default_type_value(FamilyRelType)
    val = models.IntegerField('family relation type', choices=_DATAMAP,
                              blank=False)

class SourceMediaType(mGrampsType):
    from gramps.gen.lib.srcmediatype import SourceMediaType
    _DATAMAP = get_datamap(SourceMediaType)
    _CUSTOM = SourceMediaType._CUSTOM
    _DEFAULT = get_default_type_value(SourceMediaType)
    val = models.IntegerField('source medium type', choices=_DATAMAP,
                              blank=False)

class EventRoleType(mGrampsType):
    from gramps.gen.lib.eventroletype import EventRoleType
    _DATAMAP = get_datamap(EventRoleType)
    _CUSTOM = EventRoleType._CUSTOM
    _DEFAULT = get_default_type_value(EventRoleType)
    val = models.IntegerField('event role type', choices=_DATAMAP, blank=False)

class NoteType(mGrampsType):
    from gramps.gen.lib.notetype import NoteType
    _DATAMAP = get_datamap(NoteType)
    _CUSTOM = NoteType._CUSTOM
    _DEFAULT = get_default_type_value(NoteType)
    val = models.IntegerField('note type', choices=_DATAMAP, blank=False)

class StyledTextTagType(mGrampsType):
    from gramps.gen.lib.styledtexttagtype import StyledTextTagType
    _DATAMAP = get_datamap(StyledTextTagType)
    _CUSTOM = None
    _DEFAULT = None
    val = models.IntegerField('styled text tag type', choices=_DATAMAP, blank=False)

class GenderType(mGrampsType):
    _DATAMAP = [(2, 'Unknown'), (1, 'Male'), (0, 'Female')]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('gender type', choices=_DATAMAP, blank=False)

class LdsType(mGrampsType):
    _DATAMAP = [(0, "Baptism"        ),
                (1, "Endowment"      ),
                (2, "Seal to Parents"),
                (3, "Seal to Spouse"),
                (4, "Confirmation")]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('lds type', choices=_DATAMAP, blank=False)

class LdsStatus(mGrampsType):
    _DATAMAP = [(0, "None"),
                (1, "BIC"),
                (2, "Canceled"),
                (3, "Child"),
                (4, "Cleared"),
                (5, "Completed"),
                (6, "Dns"),
                (7, "Infant"),
                (8, "Pre 1970"),
                (9, "Qualified"),
                (10, "DNSCAN"),
                (11, "Stillborn"),
                (12, "Submitted"),
                (13, "Uncleared")]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('lds status', choices=_DATAMAP, blank=False)

class NameFormatType(mGrampsType):
    _DATAMAP = [(0, "Default format"),
                (1, "Surname, Given Patronymic"),
                (2, "Given Surname"),
                (3, "Patronymic, Given"),]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('Name formats', choices=_DATAMAP, blank=False)

class CalendarType(mGrampsType):
    CAL_GREGORIAN  = 0 # CODE
    CAL_JULIAN     = 1
    CAL_HEBREW     = 2
    CAL_FRENCH     = 3
    CAL_PERSIAN    = 4
    CAL_ISLAMIC    = 5
    CAL_SWEDISH    = 6

    _DATAMAP = [(CAL_GREGORIAN, "Gregorian"),
                (CAL_JULIAN, "Julian"),
                (CAL_HEBREW, "Hebrew"),
                (CAL_FRENCH, "French Republican"),
                (CAL_PERSIAN, "Persian"),
                (CAL_ISLAMIC, "Islamic"),
                (CAL_SWEDISH, "Swedish")]

    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('Calendar', choices=_DATAMAP, blank=False)

class DateModifierType(mGrampsType):
    MOD_NONE       = 0  # CODE
    MOD_BEFORE     = 1
    MOD_AFTER      = 2
    MOD_ABOUT      = 3
    MOD_RANGE      = 4
    MOD_SPAN       = 5
    MOD_TEXTONLY   = 6

    _DATAMAP = [(MOD_NONE, ""),
                (MOD_BEFORE, "Before"),
                (MOD_AFTER, "After"),
                (MOD_ABOUT, "About"),
                (MOD_RANGE, "Range"),
                (MOD_SPAN, "Span"),
                (MOD_TEXTONLY, "Text only")]

    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('Date modifier', choices=_DATAMAP, blank=False)

class DateNewYearType(mGrampsType):
    NEWYEAR_JAN1   = 0 # CODE
    NEWYEAR_MAR1   = 1
    NEWYEAR_MAR25  = 2
    NEWYEAR_SEP1   = 3

    _DATAMAP = [(NEWYEAR_JAN1, ""),
                (NEWYEAR_MAR1, "March 1"),
                (NEWYEAR_MAR25, "March 25"),
                (NEWYEAR_SEP1, "September 1")]

    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('New Year start date', choices=_DATAMAP, blank=False)

class ThemeType(mGrampsType):
    _DATAMAP = list(enumerate(["Web_Mainz.css",
                               "Web_Basic-Ash.css",
                               "Web_Basic-Cypress.css",
                               "Web_Nebraska.css",
                               "Web_Basic-Lilac.css",
                               "Web_Print-Default.css",
                               "Web_Basic-Peach.css",
                               "Web_Visually.css",
                               "Web_Basic-Spruce.css",]))
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('Theme', choices=_DATAMAP, blank=False)

#---------------------------------------------------------------------------
#
# Support definitions
#
#---------------------------------------------------------------------------

class DateObject(models.Model):
    class Meta: abstract = True

    calendar = models.IntegerField(default=0)
    modifier = models.IntegerField(default=0)
    quality = models.IntegerField(default=0)
    #quality_estimated   = models.BooleanField()
    #quality_calculated  = models.BooleanField()
    #quality_interpreted = models.BooleanField()
    day1 = models.IntegerField(default=0)
    month1 = models.IntegerField(default=0)
    year1 = models.IntegerField(default=0)
    slash1 = models.BooleanField(default=False)
    day2 = models.IntegerField(blank=True, null=True)
    month2 = models.IntegerField(blank=True, null=True)
    year2 = models.IntegerField(blank=True, null=True)
    slash2 = models.NullBooleanField(blank=True, null=True)
    text = models.CharField(max_length=80, blank=True)
    sortval = models.IntegerField(default=0)
    newyear = models.IntegerField(default=0)

    def set_date_from_datetime(self, date_time, text=""):
        """
        Sets Date fields from an object that has year, month, and day
        properties.
        """
        y, m, d = date_time.year, date_time.month, date_time.day
        self.set_ymd(self, y, m, d, text=text)

    def set_date_from_ymd(self, y, m, d, text=""):
        """
        Sets Date fields from a year, month, and day.
        """
        gdate = GDate(y, m, d)
        gdate.text = text
        self.set_date_from_gdate(gdate)

    def set_date_from_gdate(self, gdate):
        """
        Sets Date fields from a Gramps date object.
        """
        (self.calendar, self.modifier, self.quality, dateval, self.text,
         self.sortval, self.newyear) = gdate.serialize()
        if dateval is None:
            (self.day1, self.month1, self.year1, self.slash1) = 0, 0, 0, False
            (self.day2, self.month2, self.year2, self.slash2) = 0, 0, 0, False
        elif len(dateval) == 8:
            (self.day1, self.month1, self.year1, self.slash1,
             self.day2, self.month2, self.year2, self.slash2) = dateval
        elif len(dateval) == 4:
            (self.day1, self.month1, self.year1, self.slash1) = dateval
            (self.day2, self.month2, self.year2, self.slash2) = 0, 0, 0, False

#---------------------------------------------------------------------------
#
# Primary Tables
#
#---------------------------------------------------------------------------

class Config(models.Model):
    """
    All of the meta config items for the entire system.
    """
    setting = models.CharField('config setting', max_length=50)
    description = models.TextField('description', null=True, blank=True)
    value_type = models.CharField('type of value', max_length=80)
    value = models.TextField('value')

    def __str__(self):
        return str(self.setting)

class Tag(models.Model):
    handle = models.CharField(max_length=19, unique=True)
    gramps_id = models.TextField(blank=True, null=True)
    last_saved = models.DateTimeField('last changed', auto_now=True)
    last_changed = models.DateTimeField('last changed', null=True,
                                        blank=True) # user edits
    last_changed_by = models.TextField(blank=True, null=True)

    name = models.TextField('name')
    color = models.CharField(max_length=13, blank=True, null=True) # "#000000000000" # Black
    priority = models.IntegerField('priority', blank=True, null=True)
    cache = models.TextField(blank=True, null=True)
    dji = None

    def __str__(self):
        return str(self.name)

    def get_url(self):
        return "/tag/%s" % self.handle

    def get_link(self):
        return "<a href='%s'>%s</a>" % (self.get_url(), self.name)

    def make_cache(self):
        from gramps.webapp.libdjango import DjangoInterface
        if self.dji is None:
            self.dji = DjangoInterface()
        raw = self.dji.get_tag(self)
        return str(base64.encodebytes(pickle.dumps(raw)), "utf-8")

    def from_cache(self):
        return pickle.loads(base64.decodebytes(bytes(self.cache, "utf-8")))

    def save_cache(self):
        cache = self.make_cache()
        if cache != self.cache:
            self.cache = cache
            models.Model.save(self)

    def save(self, *args, **kwargs):
        if "save_cache" in kwargs:
            self.save_cache_q = kwargs.pop("save_cache")
        if hasattr(self, "save_cache_q") and self.save_cache_q:
            # Tag doesn't have a cache
            self.cache = self.make_cache()
        models.Model.save(self, *args, **kwargs) # save to db


# Just the following have tag lists:
# ---------------------------------
#src/gen/lib/family.py
#src/gen/lib/mediaobj.py
#src/gen/lib/note.py
#src/gen/lib/person.py

class PrimaryObject(models.Model):
    """
    Common attribute of all primary objects with key on the handle
    """
    class Meta: abstract = True

    ## Fields:
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=19, unique=True)
    gramps_id =  models.CharField('ID', max_length=25, blank=True)
    last_saved = models.DateTimeField('last changed', auto_now=True)
    last_changed = models.DateTimeField('last changed', null=True,
                                        blank=True) # user edits
    last_changed_by = models.TextField(blank=True, null=True)

    private = models.BooleanField('private', default=True)
    public = models.BooleanField('public', default=True)
    #attributes = models.ManyToManyField("Attribute", blank=True, null=True)
    cache = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    dji = None
    save_cache_q = False

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__,
                           self.gramps_id)

    def get_url(self):
        return "/%s/%s" % (self.__class__.__name__.lower(),
                           self.handle)

    def get_tag_list(self):
        return [tag.handle for tag in self.tags.all()]

    def make_cache(self):
        from gramps.webapp.libdjango import DjangoInterface
        if self.dji is None:
            self.dji = DjangoInterface()

        if isinstance(self, Person):
            raw = self.dji.get_person(self)
        elif isinstance(self, Family):
            raw = self.dji.get_family(self)
        elif isinstance(self, Place):
            raw = self.dji.get_place(self)
        elif isinstance(self, Media):
            raw = self.dji.get_media(self)
        elif isinstance(self, Source):
            raw = self.dji.get_source(self)
        elif isinstance(self, Citation):
            raw = self.dji.get_citation(self)
        elif isinstance(self, Repository):
            raw = self.dji.get_repository(self)
        elif isinstance(self, Note):
            raw = self.dji.get_note(self)
        elif isinstance(self, Event):
            raw = self.dji.get_event(self)
        elif isinstance(self, Tag):
            raw = self.dji.get_tag(self)
        else:
            raise Exception("Don't know how to get raw '%s'" % type(item))
        return str(base64.encodebytes(pickle.dumps(raw)), "utf-8")

    def from_cache(self):
        return pickle.loads(base64.decodebytes(bytes(self.cache, "utf-8")))

    def save_cache(self):
        cache = self.make_cache()
        if cache != self.cache:
            self.cache = cache
            models.Model.save(self)

    def save(self, *args, **kwargs):
        if "save_cache" in kwargs:
            self.save_cache_q = kwargs.pop("save_cache")
        if self.save_cache_q:
            self.cache = self.make_cache()
        models.Model.save(self, *args, **kwargs) # save to db

class MyFamilies(models.Model):
    person = models.ForeignKey("Person")
    family = models.ForeignKey("Family")
    order = models.PositiveIntegerField(default=1)

class MyParentFamilies(models.Model):
    person = models.ForeignKey("Person")
    family = models.ForeignKey("Family")
    order = models.PositiveIntegerField(default=1)

class Person(PrimaryObject):
    """
    The model for the person object
    """
    gender_type = models.ForeignKey('GenderType', verbose_name="Gender")
    probably_alive = models.BooleanField("Probably alive", default=True)
    families = models.ManyToManyField('Family', blank=True, null=True, through="MyFamilies")
    parent_families = models.ManyToManyField('Family',
                                             related_name="parent_families",
                                             blank=True, null=True,
                                             through='MyParentFamilies')
    #addresses = models.ManyToManyField('Address', null=True, blank=True)
    references = generic.GenericRelation('PersonRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")
    birth = models.ForeignKey("Event", related_name="birth", blank=True, null=True)
    death = models.ForeignKey("Event", related_name="death", blank=True, null=True)

    birth_ref_index = models.IntegerField("Birth Reference Index", default=-1)
    death_ref_index = models.IntegerField("Death Reference Index", default=-1)

    # Others keys here:
    #   .name_set
    #   .address_set
    #   .lds_set
    #   .url_set

    def get_primary_name(self):
        """
        Return the preferred name of a person.
        """
        try:
            return self.name_set.get(preferred=True)
        except:
            return ""

    def __str__(self):
        return "%s [%s]" % (self.get_primary_name(), self.gramps_id)

    def get_selection_string(self):
        return self.name_set.get(preferred=True).get_selection_string()

    def save(self, *args, **kwargs):
        from gramps.webapp.utils import probably_alive
        compute_probably_alive = self.save_cache_q
        PrimaryObject.save(self, *args, **kwargs)
        # expensive! only do this if also saving cache
        if compute_probably_alive:
            pa = probably_alive(self.handle)
            if self.probably_alive != pa:
                self.probably_alive = pa
                PrimaryObject.save(self, *args, **kwargs)

class Family(PrimaryObject):
    father = models.ForeignKey('Person', related_name="father_ref",
                               null=True, blank=True)
    mother = models.ForeignKey('Person', related_name="mother_ref",
                               null=True, blank=True)
    family_rel_type = models.ForeignKey('FamilyRelType', verbose_name="Type")

    #lds_list = models.ManyToManyField('Lds', null=True, blank=True)

    # Others keys here:
    #   .lds_set

    def get_children(self):
        """
        Return all children from this family, in order.
        """
        obj_type = ContentType.objects.get_for_model(self)
        childrefs = ChildRef.objects.filter(object_id=self.id,
                                            object_type=obj_type).order_by("order")
        return [childref.ref_object for childref in childrefs]

    def __str__(self):
        father = self.father.get_primary_name() if self.father else "No father"
        mother = self.mother.get_primary_name() if self.mother else "No mother"
        return "%s and %s" % (father, mother)

class Citation(DateObject, PrimaryObject):
    confidence = models.IntegerField(blank=True, null=True)
    page = models.CharField("Volume/Page", max_length=50, blank=True, null=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    references = generic.GenericRelation('CitationRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

    def __str__(self):
        return "[%s] (%s, %s) to %s" % (self.gramps_id,
                                        self.confidence,
                                        self.page,
                                        self.source)

    # Other keys here:
    #   .datamap_set

class Source(PrimaryObject):
    title = models.CharField(max_length=50, blank=True, null=True)
    author = models.CharField(max_length=50, blank=True, null=True)
    pubinfo = models.CharField("Pub. info.", max_length=50, blank=True, null=True)
    abbrev = models.CharField("Abbreviation", max_length=50, blank=True, null=True)

    def __str__(self):
        return "[%s] %s" % (self.gramps_id,
                            self.title)

    # Other keys here:
    #   .datamap_set

class Event(DateObject, PrimaryObject):
    event_type = models.ForeignKey('EventType', verbose_name="Type")
    description = models.CharField('description', max_length=50, blank=True)
    place = models.ForeignKey('Place', null=True, blank=True)
    references = generic.GenericRelation('EventRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

    def __str__(self):
        return "[%s] (%s) %s" % (self.gramps_id,
                                 self.event_type,
                                 self.description)

class Repository(PrimaryObject):
    repository_type = models.ForeignKey('RepositoryType', verbose_name="Type")
    name = models.TextField(blank=True)
    #addresses = models.ManyToManyField('Address', null=True, blank=True)
    references = generic.GenericRelation('RepositoryRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")
    #url_list = models.ManyToManyField('Url', null=True, blank=True)

    def __str__(self):
        return "[%s] %s" % (self.gramps_id, self.name)

    # Others keys here:
    #   .address_set
    #   .url_set

class Place(DateObject, PrimaryObject):
    place_type = models.ForeignKey('PlaceType', verbose_name="Type")
    title = models.TextField(blank=True)
    #locations = models.ManyToManyField('Location', null=True, blank=True)
    long = models.TextField(blank=True)
    lat = models.TextField(blank=True)
    name = models.TextField(blank=True)
    lang = models.TextField(blank=True)
    code = models.TextField(blank=True) # zipcode

    #url_list = models.ManyToManyField('Url', null=True, blank=True)

    def get_selection_string(self):
        return "%s [%s]" % (self.title, self.gramps_id)

    def __str__(self):
        return str(self.title)

    # Others keys here:
    #   .url_set
    #   .location_set

class Media(DateObject, PrimaryObject):
    path = models.TextField(blank=True)
    mime = models.TextField(blank=True, null=True)
    desc = models.TextField("Title", blank=True)
    checksum = models.TextField(blank=True)
    references = generic.GenericRelation('MediaRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

    def __str__(self):
        return str(self.desc)

class Note(PrimaryObject):
    note_type = models.ForeignKey('NoteType', verbose_name="Type")
    text  = models.TextField(blank=True)
    preformatted = models.BooleanField('preformatted', default=True)
    references = generic.GenericRelation('NoteRef', #related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

    def __str__(self):
        return str(self.gramps_id)

#---------------------------------------------------------------------------
#
# Secondary Tables
#
#---------------------------------------------------------------------------

class SecondaryObject(models.Model):
    """
    We use interlinked objects, secondary object is the table for primary
    objects to refer to when linking to non primary objects
    """
    class Meta: abstract = True

    private = models.BooleanField(default=True)
    last_saved = models.DateTimeField('last changed', auto_now=True)
    last_changed = models.DateTimeField('last changed', null=True,
                                        blank=True) # user edits
    last_changed_by = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)

class Surname(models.Model):
    """
    Surname table, which links to name.
    """
    name_origin_type = models.ForeignKey('NameOriginType',
                                         verbose_name="Origin",
                                         related_name="name_origin_code",
                                         default=2)
    surname = models.TextField(blank=True)
    prefix = models.TextField(blank=True)
    primary = models.BooleanField('Primary surname?', default=True)
    connector = models.TextField(blank=True)
    name = models.ForeignKey("Name")
    order = models.PositiveIntegerField()

    def __str__(self):
        return str(self.surname)

    def get_url(self):
        # /person/handle/name/1/surname/2
        return "/person/%s/name/%s/surname/%s" % (self.name.person.handle,
                                                  self.name.order,
                                                  self.order)

class Name(DateObject, SecondaryObject):
    name_type = models.ForeignKey('NameType', verbose_name="Type",
                                  related_name="name_code",
                                  default=2)
    preferred = models.BooleanField('Preferred name?', default=True)
    first_name = models.TextField(blank=True)
    suffix = models.TextField(blank=True)
    title = models.TextField(blank=True)
    call = models.TextField(blank=True)
    nick = models.TextField(blank=True)
    famnick = models.TextField(blank=True)
    group_as = models.TextField(blank=True)
    sort_as =  models.ForeignKey('NameFormatType',
                                 related_name="sort_as",
                                 default=1)
    display_as = models.ForeignKey('NameFormatType',
                                   related_name="display_as",
                                   default=1)
    ## Key:
    person = models.ForeignKey("Person")
    _sanitized = False

    def __str__(self):
        try:
            surname = self.surname_set.get(primary=True)
        except:
            surname = "[No primary surname]"
        return "%s, %s" % (surname, self.first_name)

    def get_selection_string(self):
        try:
            surname = self.surname_set.get(primary=True)
        except:
            surname = "[No primary surname]"
        return "%s, %s [%s]" % (surname, self.first_name, self.person.gramps_id)

    @staticmethod
    def get_dummy():
        name = Name()
        #name.

    def sanitize(self):
        if not self._sanitized:
            self._sanitized = True
            if self.person.probably_alive:
                self.first_name = "[Living]"
                self.nick = ""
                self.call = ""
                self.group_as = ""
                self.title = ""

    def make_surname_list(self):
        return [(x.surname, x.prefix, x.primary,
                 tuple(x.name_origin_type), x.connector) for x in
                self.surname_set.all()]

    def get_url(self):
        # /person/handle/name/1
        return "/person/%s/name/%s" % (self.person.handle, self.order)

class Lds(DateObject, SecondaryObject):
    """
    BAPTISM         = 0
    ENDOWMENT       = 1
    SEAL_TO_PARENTS = 2
    SEAL_TO_SPOUSE  = 3
    CONFIRMATION    = 4

    DEFAULT_TYPE = BAPTISM


    STATUS_NONE      = 0
    STATUS_BIC       = 1
    STATUS_CANCELED  = 2
    STATUS_CHILD     = 3
    STATUS_CLEARED   = 4
    STATUS_COMPLETED = 5
    STATUS_DNS       = 6
    STATUS_INFANT    = 7
    STATUS_PRE_1970  = 8
    STATUS_QUALIFIED = 9
    STATUS_DNS_CAN   = 10
    STATUS_STILLBORN = 11
    STATUS_SUBMITTED = 12
    STATUS_UNCLEARED = 13

    DEFAULT_STATUS = STATUS_NONE
    """
    lds_type = models.ForeignKey('LdsType')
    place = models.ForeignKey('Place', null=True)
    famc = models.ForeignKey('Family', related_name="famc", null=True)
    temple = models.TextField(blank=True)
    status = models.ForeignKey('LdsStatus')

    person = models.ForeignKey("Person", null=True, blank=True)
    family = models.ForeignKey("Family", null=True, blank=True)

class Markup(models.Model):
    note = models.ForeignKey('Note')
    styled_text_tag_type = models.ForeignKey('StyledTextTagType')
    order = models.PositiveIntegerField()
    string = models.TextField(blank=True, null=True)
    start_stop_list = models.TextField(default="[]")

class SourceAttribute(models.Model):
    key = models.CharField(max_length=80, blank=True)
    value = models.CharField(max_length=80, blank=True)
    source = models.ForeignKey("Source")
    private = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

class CitationAttribute(models.Model):
    key = models.CharField(max_length=80, blank=True)
    value = models.CharField(max_length=80, blank=True)
    citation = models.ForeignKey("Citation")
    private = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

class Address(DateObject, SecondaryObject):
    #locations = models.ManyToManyField('Location', null=True)
    person = models.ForeignKey('Person', null=True, blank=True)
    repository = models.ForeignKey('Repository', null=True, blank=True)

    # Others keys here:
    #   .location_set


class Location(models.Model):
    street = models.TextField(blank=True)
    locality = models.TextField(blank=True)
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    state = models.TextField(blank=True)
    country = models.TextField(blank=True)
    postal = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    parish = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()

    place = models.ForeignKey("Place", null=True, blank=True)
    address = models.ForeignKey("Address", null=True, blank=True)

class Url(models.Model):
    private = models.BooleanField('private url?', default=True)
    path = models.TextField(blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    url_type = models.ForeignKey('UrlType')
    order = models.PositiveIntegerField()

    person = models.ForeignKey("Person", null=True, blank=True)
    place = models.ForeignKey("Place", null=True, blank=True)
    repository = models.ForeignKey("Repository", null=True, blank=True)

class Attribute(models.Model):
    private = models.BooleanField('private attribute?', default=True)
    attribute_type = models.ForeignKey('AttributeType')
    value = models.TextField(blank=True, null=True)

    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    attribute_of = generic.GenericForeignKey("object_type", "object_id")

## consider using:
## URLField

#---------------------------------------------------------------------------
#
# Reference Objects
#
#---------------------------------------------------------------------------

class BaseRef(models.Model):
    class Meta: abstract = True

    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    referenced_by = generic.GenericForeignKey("object_type", "object_id")

    order = models.PositiveIntegerField()
    last_saved = models.DateTimeField('last changed', auto_now=True)
    last_changed = models.DateTimeField('last changed', null=True) # user edits
    last_changed_by = models.TextField(blank=True, null=True)

    #attributes = models.ManyToManyField("Attribute", null=True)
    private = models.BooleanField(default=True)

    def get_url(self):
        # /person/3536453463/reference/event/2
        ref_by = self.object_type.model_class().objects.get(id=self.object_id)
        ref_to = self.get_reference_to()
        return "/%s/%s/reference/%s/%s" % (ref_by.__class__.__name__.lower(),
                                           ref_by.handle,
                                           ref_to.__class__.__name__.lower(),
                                           self.order)
class Log(BaseRef):
    log_type = models.CharField(max_length=10) # edit, delete, add
    reason = models.TextField() # must be filled in
    cache = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s: %s on %s by %s" % (self.log_type,
                                       self.referenced_by,
                                       self.last_changed,
                                       self.last_changed_by)

class NoteRef(BaseRef):
    ref_object = models.ForeignKey('Note')

    def get_reference_to(self):
        return self.ref_object

    def __str__(self):
        return "NoteRef to " + str(self.ref_object)

class EventRef(BaseRef):
    ref_object = models.ForeignKey('Event')
    role_type = models.ForeignKey('EventRoleType')

    def __str__(self):
        return str(self.ref_object)

    def get_reference_to(self):
        return self.ref_object

    def get_url(self):
        # /person/3536453463/reference/event/2
        ref_by = self.object_type.model_class().objects.get(id=self.object_id)
        ref_to = self.ref_object
        return "/%s/%s/reference/%s/%s" % (ref_by.__class__.__name__.lower(),
                                           ref_by.handle,
                                           ref_to.__class__.__name__.lower(),
                                           self.order)

class RepositoryRef(BaseRef):
    ref_object = models.ForeignKey('Repository')
    source_media_type = models.ForeignKey('SourceMediaType')
    call_number = models.CharField(max_length=50)

    def get_reference_to(self):
        return self.ref_object

    def __str__(self):
        return "RepositoryRef to " + str(self.ref_object)

class PlaceRef(BaseRef, DateObject):
    ref_object = models.ForeignKey('Place')

    def get_reference_to(self):
        return self.ref_object

    def __str__(self):
        return "PlaceRef to " + str(self.ref_object)

class PersonRef(BaseRef):
    ref_object = models.ForeignKey('Person')
    description = models.CharField(max_length=50, blank=True, null=True)

    def get_reference_to(self):
        return self.ref_object

    def __str__(self):
        return "PersonRef to " + str(self.ref_object)

class CitationRef(BaseRef):
    citation = models.ForeignKey('Citation')

    def __str__(self):
        return "CitationRef to " + str(self.citation)

    def get_reference_to(self):
        return self.citation

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey('ChildRefType',
                                        related_name="child_father_rel")
    mother_rel_type = models.ForeignKey('ChildRefType',
                                        related_name="child_mother_rel")
    ref_object = models.ForeignKey('Person')

    def get_reference_to(self):
        return self.ref_object

    def get_url(self):
        # FIXME: go to child reference
        return "/person/%s" % self.ref_object.handle

    def __str__(self):
        return "ChildRef to " + str(self.ref_object)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    ref_object = models.ForeignKey('Media')

    def get_reference_to(self):
        return self.ref_object

    def __str__(self):
        return "MediaRef to " + str(self.ref_object)

class Report(models.Model):
    gramps_id = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    handle = models.TextField(blank=True, null=True) # report_id
    report_type = models.TextField(blank=True, null=True)
    options = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Result(models.Model):
    name = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    run_on = models.DateTimeField('run on', auto_now=True)
    run_by = models.TextField('run by', blank=True, null=True)
    status = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Metadata(models.Model):
    setting = models.TextField(blank=False, null=False)
    value = models.BinaryField()

class GenderStats(models.Model):
    # GenderStats (name, female, male, unknown)
    name = models.TextField(null=False)
    female = models.IntegerField(blank=False)
    male = models.IntegerField(blank=False)
    unknown = models.IntegerField(blank=False)

class Reference(models.Model):
    # Reference (obj_handle, obj_class, ref_handle, ref_class)
    obj_handle = models.CharField(max_length=19)
    obj_class = models.TextField(null=False)
    ref_handle = models.CharField(max_length=19)
    ref_class = models.TextField(null=False)

class NameGroup(models.Model):
    # NameGroup table (name, grouping)
    name = models.TextField(blank=False, null=False)
    grouping = models.TextField(null=False)

TABLES = [
    ("abstract", mGrampsType),
    ("type", NameType),
    ("type", NameOriginType),
    ("type", NameFormatType),
    ("type", AttributeType),
    ("type", UrlType),
    ("type", ChildRefType),
    ("type", RepositoryType),
    ("type", PlaceType),
    ("type", EventType),
    ("type", FamilyRelType),
    ("type", SourceMediaType),
    ("type", EventRoleType),
    ("type", NoteType),
    ("type", GenderType),
    ("type", LdsType),
    ("type", LdsStatus),
    ("type", ThemeType),
    ("type", StyledTextTagType),
    ("abstract", DateObject),
    ("abstract", PrimaryObject),
    ("primary", Person),
    ("primary", Family),
    ("primary", Citation),
    ("primary", Source),
    ("primary", Event),
    ("primary", Repository),
    ("primary", Place),
    ("primary", Media),
    ("primary", Note),
    ("primary", Tag),
    ("abstract", SecondaryObject),
    ("secondary", Attribute),
    ("secondary", SourceAttribute),
    ("secondary", CitationAttribute),
    ("secondary", Name),
    ("secondary", Surname),
    ("secondary", Lds),
    ("secondary", Markup),
    ("secondary", Address),
    ("secondary", Location),
    ("secondary", Url),
    ("abstract", BaseRef),
    ("ref", CitationRef),
    ("ref", NoteRef),
    ("ref", EventRef),
    ("ref", RepositoryRef),
    ("ref", PlaceRef),
    ("ref", PersonRef),
    ("ref", ChildRef),
    ("ref", MediaRef),
    ("ref", MyFamilies),
    ("ref", MyParentFamilies),
    ("system", Config),
    ("system", Report),
    ("system", Result),
    ]

def no_style():
    """Returns a Django Style object that has no colors."""
    class dummy(object):
        def __getattr__(self, attr):
            return lambda x: x
    return dummy()

def clear_tables(*categories):
    """
    Clear the entries of categories of tables. Category is:
    "abstract", "type", "ref", "system", "primary" and "secondary".
    """
    # FIXME: I don't think this works anymore...
    from django.db import connection, transaction
    cursor = connection.cursor()
    flush_tables = []
    for (category, model) in get_tables(*categories):
        flush_tables.append(model._meta.db_table)
    # tables = connection.introspection.table_names()
    # flush_tables = [table for table in tables if not table.endswith("type")]
    statements = connection.ops.sql_flush(no_style(),
                                          flush_tables,
                                          connection.introspection.sequence_list())
    for statement in statements:
        cursor.execute(statement)
        transaction.commit_unless_managed()

def table_stats(*categories):
    """
    Shows the record counts for each table category.
    """
    tables = get_tables(*categories)
    tables.sort()
    for pair in tables:
        print(("%-25s" % pair[1].__name__), ":", \
            pair[1].objects.all().count())

def get_tables(*categories):
    return [pair for pair in TABLES if (pair[0] in categories) or
            ("all" in categories) and pair[0] != "abstract"]

