#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# webapp/grampsdb/forms.py

# forms.py forms for Django web project

# Django Modules:
from django import forms
from django.forms.models import inlineformset_factory
from django.forms.models import BaseModelFormSet
from django.forms.widgets import TextInput, HiddenInput

# Gramps Modules:
from gramps.webapp.grampsdb.models import *
from gramps.gen.mime import get_type

# Python Modules:
import datetime

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ["death", "birth", "handle", "birth_ref_index",
                   "death_ref_index", "families", "parent_families",
                   "cache"]
    def save(self, *args, **kwargs):
        self.instance.save_cache_q = kwargs.pop("save_cache", True)
        return super().save(*args, **kwargs)

class NameForm(forms.ModelForm):
    class Meta:
        model = Name
        # Exclude these, so they don't get checked:
        exclude = ["order", "calendar", "modifier",
                   "quality",
                   #"quality_estimated", "quality_calculated",
                   #"quality_interpreted",
                   "year1", "day1", "month1",
                   "sortval", "newyear", "person"]
    # Add these because they are TextFields, which render as
    # Textareas:
    first_name = forms.CharField(label="Given",
                                 required=False,
                                 widget=TextInput(attrs={'size':'60'}))
    title = forms.CharField(required=False,
                            widget=TextInput(attrs={'size':'15'}))
    call = forms.CharField(label="Call",
                           required=False,
                           widget=TextInput(attrs={'size':'15'}))
    nick = forms.CharField(label="Nick",
                           required=False,
                           widget=TextInput(attrs={'size':'15'}))
    group_as = forms.CharField(label="Group as",
                               required=False,
                               widget=TextInput(attrs={'size':'30'}))
    suffix = forms.CharField(required=False,
                             initial=' suffix ',
                             widget=TextInput(attrs={'size':'15',
                                                     'style': 'font-style: italic; color: gray; ',
                                                     'onFocus': """if (this.value == ' suffix ') {
                                                                      this.value = '';
                                                                   }
                                                                   this.style.color = "black";
                                                                   this.style.fontStyle = 'normal';
                                                                """,
                                                     'onBlur': """if (this.value == '') {
                                                                     this.value = ' suffix ';
                                                                     this.style.color = "gray";
                                                                     this.style.fontStyle = 'italic';
                                                                  }
                                                               """}))

class NameFormFromPerson(NameForm):
    class Meta:
        model = Name
        # Exclude these, so they don't get checked:
        # Excludes sort_as and display_as
        exclude = ["order", "calendar", "modifier",
                   "quality",
                   #"quality_estimated", "quality_calculated",
                   #"quality_interpreted",
                   "year1", "day1", "month1",
                   "sortval", "newyear", "person",
                   "group_as", "sort_as", "display_as"]

class SurnameForm(forms.ModelForm):
    class Meta:
        model = Surname
        exclude = ['name', 'order']

    surname = forms.CharField(label="Surname",
                              required=False,
                              widget=TextInput(attrs={'size':'30'}))

    connector = forms.CharField(label="Connector",
                              required=False,
                              widget=TextInput(attrs={'size':'30'}))

    prefix = forms.CharField(label="Prefix",
                             required=False,
                             initial=' prefix ',
                             widget=TextInput(attrs={'size':'15',
                                                     'style': 'font-style: italic; color: gray; ',
                                                     'onFocus': """if (this.value == ' prefix ') {
                                                                      this.value = '';
                                                                   }
                                                                   this.style.color = "black";
                                                                   this.style.fontStyle = 'normal';
                                                                """,
                                                     'onBlur': """if (this.value == '') {
                                                                     this.value = ' prefix ';
                                                                     this.style.color = "gray";
                                                                     this.style.fontStyle = 'italic';
                                                                   }
                                                                """}))
class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        exclude = ["handle", "cache", "mother", "father"]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ["handle", "sortval", "month1", "year1", "day1",
                   "newyear", "calendar", "modifier", "quality", "cache",
                   "place"]

    def clean(self):
        from gramps.webapp.utils import dp
        data = super(EventForm, self).clean()
        dobj = dp(data.get('text'))
        if not dobj.is_valid():
            msg = "Invalid date format"
            self._errors["date"] = self.error_class([msg])
            del data["text"]
        return data

    def save(self, commit=True):
        from gramps.webapp.utils import dp
        from gramps.webapp.libdjango import DjangoInterface
        dji = DjangoInterface()
        model = super(EventForm, self).save(commit=False)
        dobj = dp(self.cleaned_data['text'])
        dji.add_date(model, dobj.serialize())
        if commit:
            model.save()
        return model

    text = forms.CharField(label="Date",
                           required=False,
                           widget=TextInput(attrs={'size':'45'}))

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ["handle", "text"]

    notetext = forms.CharField(label="Text",
                               widget=forms.widgets.Textarea(attrs={'rows':'10', 'cols': '80', 'class':'wysiwyg'}))

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        exclude = ["handle", "sortval", "month1", "year1", "day1",
                   "newyear", "calendar", "modifier", "quality", "cache"]

    def clean(self):
        from gramps.webapp.utils import dp
        data = super(MediaForm, self).clean()
        dobj = dp(data.get('text'))
        if not dobj.is_valid():
            msg = "Invalid date format"
            self._errors["date"] = self.error_class([msg])
            del data["text"]
        return data

    def save(self, commit=True):
        from gramps.webapp.utils import dp
        from gramps.webapp.libdjango import DjangoInterface
        dji = DjangoInterface()
        model = super(MediaForm, self).save(commit=False)
        model.mime = get_type(model.path)
        dobj = dp(self.cleaned_data['text'])
        dji.add_date(model, dobj.serialize())
        if commit:
            model.save()
        return model

    text = forms.CharField(label="Date",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))
    desc = forms.CharField(label="Title",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))
    path = forms.CharField(label="Path",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))

class CitationForm(forms.ModelForm):
    class Meta:
        model = Citation
        exclude = ["handle", "sortval", "month1", "year1", "day1",
                   "newyear", "calendar", "modifier", "quality", "cache"]

    def clean(self):
        from gramps.webapp.utils import dp
        data = super(CitationForm, self).clean()
        dobj = dp(data.get('text'))
        if not dobj.is_valid():
            msg = "Invalid date format"
            self._errors["date"] = self.error_class([msg])
            del data["text"]
        return data

    def save(self, commit=True):
        from gramps.webapp.utils import dp
        from gramps.webapp.libdjango import DjangoInterface
        dji = DjangoInterface()
        model = super(CitationForm, self).save(commit=False)
        dobj = dp(self.cleaned_data['text'])
        dji.add_date(model, dobj.serialize())
        if commit:
            model.save()
        return model

    text = forms.CharField(label="Date",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        exclude = ["handle", "cache"]

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        exclude = ["handle", "cache"]

    title = forms.CharField(label="Title",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))
    long = forms.CharField(label="Longitude",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))
    lat = forms.CharField(label="Latitude",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))

class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        exclude = ["handle", "cache"]

    name = forms.CharField(label="Name",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ["handle"]

    name = forms.CharField(label="Name",
                           required=False,
                           widget=TextInput(attrs={'size':'70'}))

class EventRefForm(forms.ModelForm):
    class Meta:
        model = EventRef

class LogForm(forms.ModelForm):
    error_css_class = 'error'

    class Meta:
        model = Log
        fields = ["reason"]

    reason = forms.CharField(label="Reason for change",
                             widget=forms.widgets.Textarea(attrs={'rows':'2',
                                                                  'cols': '65'}))
class PickForm(forms.Form):
    picklist = forms.ChoiceField()
    def __init__(self, label, item, order_by, *args, **kwargs):
        super(PickForm, self).__init__(*args, **kwargs)
        self.fields['picklist'].choices = \
            [("", "---------")] + [(p.handle, p) for p in item.objects.all() \
                                .order_by(*order_by)]
