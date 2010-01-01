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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

"""
All of the models for the grampsdb Django data schema.
This requires initial data for all of the Types, which
is loaded by the fixtures/initial_data.json, which is
created by init.py.
"""

_DEBUG = True

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from gen.lib.date import Date as GDate, Today
from Utils import create_id, create_uid

#---------------------------------------------------------------------------
#
# Support functions
#
#---------------------------------------------------------------------------

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
        if new and _DEBUG:
            print "DEBUG: Made new type:", the_type, data
        return obj
    else:
        return the_type.objects.get(val=data[0])

def get_default_type(the_type):
    """
    Gets the default row for a given Type.
    """
    val, name = the_type._DEFAULT
    return the_type.objects.get(val=val, name=name)

def get_datamap(grampsclass):
    return [(x[0],x[2]) for x in grampsclass._DATAMAP]

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
    
    def __unicode__(self): return self.name

    def get_default_type(self):
        """ return a tuple default (val,name) """
        return self._DATAMAP[self._DEFAULT]

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

class MarkerType(mGrampsType):
    from gen.lib.markertype import MarkerType
    _DATAMAP = get_datamap(MarkerType)
    _CUSTOM = MarkerType._CUSTOM
    _DEFAULT = _DATAMAP[MarkerType._DEFAULT]
    val = models.IntegerField('marker', choices=_DATAMAP, blank=False)

class NameType(mGrampsType):
    from gen.lib.nametype import NameType
    _DATAMAP = get_datamap(NameType)
    _CUSTOM = NameType._CUSTOM
    _DEFAULT = _DATAMAP[NameType._DEFAULT]
    val = models.IntegerField('name type', choices=_DATAMAP, blank=False)

class AttributeType(mGrampsType):
    from gen.lib.attrtype import AttributeType
    _DATAMAP = get_datamap(AttributeType)
    _CUSTOM = AttributeType._CUSTOM
    _DEFAULT = _DATAMAP[AttributeType._DEFAULT]
    val = models.IntegerField('attribute type', choices=_DATAMAP, blank=False)

class UrlType(mGrampsType):
    from gen.lib.urltype import UrlType
    _DATAMAP = get_datamap(UrlType)
    _CUSTOM = UrlType._CUSTOM
    _DEFAULT = _DATAMAP[UrlType._DEFAULT]
    val = models.IntegerField('url type', choices=_DATAMAP, blank=False)

class ChildRefType(mGrampsType):
    from gen.lib.childreftype import ChildRefType
    _DATAMAP = get_datamap(ChildRefType)
    _CUSTOM = ChildRefType._CUSTOM
    _DEFAULT = _DATAMAP[ChildRefType._DEFAULT]
    val = models.IntegerField('child reference type', choices=_DATAMAP, 
                              blank=False)

class RepositoryType(mGrampsType):
    from gen.lib.repotype import RepositoryType
    _DATAMAP = get_datamap(RepositoryType)
    _CUSTOM = RepositoryType._CUSTOM
    _DEFAULT = _DATAMAP[RepositoryType._DEFAULT]
    val = models.IntegerField('repository type', choices=_DATAMAP, blank=False)

class EventType(mGrampsType):
    from gen.lib.eventtype import EventType
    _DATAMAP = get_datamap(EventType)
    _CUSTOM = EventType._CUSTOM
    _DEFAULT = _DATAMAP[EventType._DEFAULT]
    BIRTH = 12
    DEATH = 13
    val = models.IntegerField('event type', choices=_DATAMAP, blank=False)

class FamilyRelType(mGrampsType):
    from gen.lib.familyreltype import FamilyRelType
    _DATAMAP = get_datamap(FamilyRelType)
    _CUSTOM = FamilyRelType._CUSTOM
    _DEFAULT = _DATAMAP[FamilyRelType._DEFAULT]
    val = models.IntegerField('family relation type', choices=_DATAMAP, 
                              blank=False)

class SourceMediaType(mGrampsType):
    from gen.lib.srcmediatype import SourceMediaType
    _DATAMAP = get_datamap(SourceMediaType)
    _CUSTOM = SourceMediaType._CUSTOM
    _DEFAULT = _DATAMAP[SourceMediaType._DEFAULT]
    val = models.IntegerField('source medium type', choices=_DATAMAP, 
                              blank=False)

class EventRoleType(mGrampsType):
    from gen.lib.eventroletype import EventRoleType
    _DATAMAP = get_datamap(EventRoleType)
    _CUSTOM = EventRoleType._CUSTOM
    _DEFAULT = _DATAMAP[EventRoleType._DEFAULT]
    val = models.IntegerField('event role type', choices=_DATAMAP, blank=False)

class NoteType(mGrampsType):
    from gen.lib.notetype import NoteType
    _DATAMAP = get_datamap(NoteType)
    _CUSTOM = NoteType._CUSTOM
    _DEFAULT = _DATAMAP[NoteType._DEFAULT]
    val = models.IntegerField('note type', choices=_DATAMAP, blank=False)

class MarkupType(mGrampsType):
    from gen.lib.notetype import NoteType
    _DATAMAP = [(0, "Custom")]
    _CUSTOM = 0
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('note type', choices=_DATAMAP, blank=False)

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

    _DEFAULT = _DATAMAP[CAL_GREGORIAN]
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

    _DEFAULT = _DATAMAP[MOD_NONE]
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

    _DEFAULT = _DATAMAP[NEWYEAR_JAN1]
    val = models.IntegerField('New Year start date', choices=_DATAMAP, blank=False)
    
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
    setting = models.CharField('config setting', max_length=25)
    description = models.TextField('description')
    value_type = models.CharField('type of value', max_length=25)
    value = models.TextField('value')

class PrimaryObject(models.Model):
    """
    Common attribute of all primary objects with key on the handle
    """
    class Meta: abstract = True

    ## Fields:
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=19, unique=True)
    gramps_id =  models.CharField('gramps id', max_length=25, blank=True)
    last_saved = models.DateTimeField('last changed', auto_now=True) 
    last_changed = models.DateTimeField('last changed', null=True,
                                        blank=True) # user edits
    private = models.BooleanField('private')
    #attributes = models.ManyToManyField("Attribute", blank=True, null=True)

    ## Keys:
    marker_type = models.ForeignKey('MarkerType')

    def __unicode__(self): return "%s: %s" % (self.__class__.__name__,
                                              self.gramps_id)

class Person(PrimaryObject):
    """
    The model for the person object
    """
    gender_type = models.ForeignKey('GenderType')
    probably_alive = models.BooleanField("Probably alive")
    families = models.ManyToManyField('Family', blank=True, null=True)
    parent_families = models.ManyToManyField('Family', 
                                             related_name="parent_families",
                                             blank=True, null=True)
    #addresses = models.ManyToManyField('Address', null=True, blank=True)
    references = generic.GenericRelation('PersonRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")
    birth = models.ForeignKey("Event", related_name="birth", blank=True, null=True)
    death = models.ForeignKey("Event", related_name="death", blank=True, null=True)

    # Others keys here:
    #   .name_set 
    #   .address_set
    #   .lds_set
    #   .url_set

    def get_primary_name(self):
        """
        Return the preferred name of a person.
        """
        return self.name_set.get(preferred=True)

class Family(PrimaryObject):
    father = models.ForeignKey('Person', related_name="father_ref", 
                               null=True, blank=True)
    mother = models.ForeignKey('Person', related_name="mother_ref", 
                               null=True, blank=True)
    family_rel_type = models.ForeignKey('FamilyRelType')
    #lds_list = models.ManyToManyField('Lds', null=True, blank=True)

    # Others keys here:
    #   .lds_set

class Source(PrimaryObject):
    title = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True)
    pubinfo = models.CharField(max_length=50, blank=True)
    abbrev = models.CharField(max_length=50, blank=True)
    #datamaps = models.ManyToManyField('Datamap', null=True, blank=True)
    references = generic.GenericRelation('SourceRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")
    # Other keys here:
    #   .datamap_set

class Event(DateObject, PrimaryObject):
    event_type = models.ForeignKey('EventType')
    description = models.CharField('description', max_length=50, blank=True)
    place = models.ForeignKey('Place', null=True)
    references = generic.GenericRelation('EventRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Repository(PrimaryObject):
    repository_type = models.ForeignKey('RepositoryType')
    name = models.TextField(blank=True)
    #addresses = models.ManyToManyField('Address', null=True, blank=True)
    references = generic.GenericRelation('RepositoryRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")
    #url_list = models.ManyToManyField('Url', null=True, blank=True)

    # Others keys here:
    #   .address_set
    #   .url_set

class Place(PrimaryObject):
    title = models.TextField(blank=True)
    #locations = models.ManyToManyField('Location', null=True, blank=True)
    long = models.TextField(blank=True)
    lat = models.TextField(blank=True)
    #url_list = models.ManyToManyField('Url', null=True, blank=True)

    # Others keys here:
    #   .url_set
    #   .location_set

class Media(DateObject, PrimaryObject):
    path = models.TextField(blank=True)
    mime = models.TextField(blank=True, null=True)
    desc = models.TextField(blank=True)
    references = generic.GenericRelation('MediaRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Note(PrimaryObject):
    note_type = models.ForeignKey('NoteType')
    text  = models.TextField(blank=True)
    preformatted = models.BooleanField('preformatted')
    references = generic.GenericRelation('NoteRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

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

    private = models.BooleanField()
    last_saved = models.DateTimeField('last changed', auto_now=True)
    last_changed = models.DateTimeField('last changed', null=True,
                                        blank=True) # user edits
    order = models.PositiveIntegerField(default=1)

class Name(DateObject, SecondaryObject):
    name_type = models.ForeignKey('NameType', 
                                  related_name="name_code",
                                  default=2)
    preferred = models.BooleanField('Preferred name?')
    first_name = models.TextField(blank=True)
    surname = models.TextField(blank=True)
    suffix = models.TextField(blank=True)
    title = models.TextField(blank=True)
    prefix = models.TextField(blank=True)
    patronymic = models.TextField(blank=True)
    call = models.TextField(blank=True)
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

    def __unicode__(self):
        return "%s%s%s, %s" % (self.prefix, 
                               ["", " "][bool(self.prefix)],
                               self.surname, 
                               self.first_name)
    @staticmethod
    def get_dummy():
        name = Name()
        #name.

    def sanitize(self):
        if not self._sanitized:
            self._sanitized = True
            if self.person.probably_alive:
                self.first_name = "[Living]"
                self.call = ""
                self.group_as = ""
                self.title = ""

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
    markup_type = models.ForeignKey('MarkupType')
    order = models.PositiveIntegerField()
    string = models.TextField(blank=True, null=True)
    start_stop_list = models.TextField(default="[]")

class Datamap(models.Model):
    key = models.CharField(max_length=80, blank=True)
    value = models.CharField(max_length=80, blank=True)

    source = models.ForeignKey("Source", null=True, blank=True)

class Address(DateObject, SecondaryObject):
    #locations = models.ManyToManyField('Location', null=True)
    person = models.ForeignKey('Person', null=True, blank=True)
    repository = models.ForeignKey('Repository', null=True, blank=True)

    # Others keys here:
    #   .location_set


class Location(models.Model):
    street = models.TextField(blank=True)
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
    private = models.BooleanField('private url?')
    path = models.TextField(blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    url_type = models.ForeignKey('UrlType') 
    order = models.PositiveIntegerField()

    person = models.ForeignKey("Person", null=True, blank=True)
    place = models.ForeignKey("Place", null=True, blank=True)
    repository = models.ForeignKey("Repository", null=True, blank=True)

class Attribute(models.Model):
    private = models.BooleanField('private attribute?')
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
    #attributes = models.ManyToManyField("Attribute", null=True)
    private = models.BooleanField()
  
class NoteRef(BaseRef):
    ref_object = models.ForeignKey('Note') 

    def __unicode__(self):
        return "NoteRef to " + str(self.ref_object)

class SourceRef(DateObject, BaseRef):
    ref_object = models.ForeignKey('Source')
    page = models.CharField(max_length=50)
    confidence = models.IntegerField()

    def __unicode__(self):
        return "SourceRef to " + str(self.ref_object)

class EventRef(BaseRef):
    ref_object = models.ForeignKey('Event')
    role_type = models.ForeignKey('EventRoleType')

    def __unicode__(self):
        return "EventRef to " + str(self.ref_object)

class RepositoryRef(BaseRef):
    ref_object = models.ForeignKey('Repository')
    source_media_type = models.ForeignKey('SourceMediaType')
    call_number = models.CharField(max_length=50)

    def __unicode__(self):
        return "RepositoryRef to " + str(self.ref_object)

class PersonRef(BaseRef):
    ref_object = models.ForeignKey('Person')
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return "PersonRef to " + str(self.ref_object)

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey('ChildRefType', 
                                        related_name="child_father_rel")
    mother_rel_type = models.ForeignKey('ChildRefType', 
                                        related_name="child_mother_rel")
    ref_object = models.ForeignKey('Person')

    def __unicode__(self):
        return "ChildRef to " + str(self.ref_object)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    ref_object = models.ForeignKey('Media')

    def __unicode__(self):
        return "MediaRef to " + str(self.ref_object)

TABLES = [
    ("abstract", mGrampsType),
    ("type", MarkerType),
    ("type", MarkupType),
    ("type", NameType),
    ("type", NameFormatType),
    ("type", AttributeType),
    ("type", UrlType),
    ("type", ChildRefType),
    ("type", RepositoryType),
    ("type", EventType),
    ("type", FamilyRelType),
    ("type", SourceMediaType),
    ("type", EventRoleType),
    ("type", NoteType),
    ("type", GenderType),
    ("type", LdsType),
    ("type", LdsStatus),
    ("abstract", DateObject),
    ("meta", Config),
    ("abstract", PrimaryObject),
    ("primary", Person),
    ("primary", Family),
    ("primary", Source),
    ("primary", Event),
    ("primary", Repository),
    ("primary", Place),
    ("primary", Media),
    ("primary", Note),
    ("abstract", SecondaryObject),
    ("secondary", Attribute),
    ("secondary", Datamap),
    ("secondary", Name),
    ("secondary", Lds),
    ("secondary", Markup),
    ("secondary", Address),
    ("secondary", Location),
    ("secondary", Url),
    ("abstract", BaseRef),
    ("ref", NoteRef),
    ("ref", SourceRef),
    ("ref", EventRef),
    ("ref", RepositoryRef),
    ("ref", PersonRef),
    ("ref", ChildRef),
    ("ref", MediaRef)
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
    "abstract", "type", "ref", "meta", "primary" and "secondary".
    """
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
        print ("%-25s" % pair[1].__name__), ":", \
            pair[1].objects.all().count()

def get_tables(*categories):
    return [pair for pair in TABLES if (pair[0] in categories) or 
            ("all" in categories) and pair[0] != "abstract"]

