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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# webapp/grampsdb/forms.py
# $Id$

# forms.py forms for Django web project 

from django import forms
from webapp.grampsdb.models import *
from django.forms.models import inlineformset_factory
from django.forms.models import BaseModelFormSet
from django.forms.widgets import TextInput
import datetime

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ["death", "birth", "handle", "birth_ref_index", "death_ref_index"]

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
    surname = forms.CharField(label="Surname", 
                              required=False, 
                              widget=TextInput(attrs={'size':'30'}))
    first_name = forms.CharField(label="Given", 
                                 required=False, 
                                 widget=TextInput(attrs={'size':'60'}))
    title = forms.CharField(required=False, 
                            widget=TextInput(attrs={'size':'15'}))
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
    call = forms.CharField(label="Call", 
                           required=False, 
                           widget=TextInput(attrs={'size':'15'}))
    nick = forms.CharField(label="Nick", 
                           required=False, 
                           widget=TextInput(attrs={'size':'15'}))
    origin = forms.CharField(required=False, 
                             widget=TextInput(attrs={'size':'15'}))

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
                   "sort_as", "display_as"]

