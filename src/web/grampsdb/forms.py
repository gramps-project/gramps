# forms.py forms for Django web project 

from django import forms
from web.grampsdb.models import *
from django.forms.models import inlineformset_factory
from django.forms.models import BaseModelFormSet
from django.forms.widgets import TextInput
import datetime

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person

        exclude = ["death", "birth", "handle"]

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
    surname = forms.CharField(required=False, 
                              widget=TextInput(attrs={'size':'30'}))
    first_name = forms.CharField(label="Given", 
                                 required=False, 
                                 widget=TextInput(attrs={'size':'30'}))
    title = forms.CharField(required=False, 
                            widget=TextInput(attrs={'size':'30'}))
    prefix = forms.CharField(required=False, 
                             widget=TextInput(attrs={'size':'30'}))
    suffix = forms.CharField(required=False, 
                             widget=TextInput(attrs={'size':'30'}))
    call = forms.CharField(label="Callname", 
                           required=False, 
                           widget=TextInput(attrs={'size':'30'}))
    patronymic = forms.CharField(required=False, 
                                 widget=TextInput(attrs={'size':'30'}))
    group_as = forms.CharField(required=False, 
                               widget=TextInput(attrs={'size':'30'}))
    text = forms.CharField(label="Date",
                           required=False, 
                           widget=TextInput(attrs={'size':'30'}))

class NameFormFromPerson(NameForm):
    class Meta:
        model = Name
        # Exclude these, so they don't get checked:
        exclude = ["order", "calendar", "modifier", 
                   "quality",
                   #"quality_estimated", "quality_calculated", 
                   #"quality_interpreted", 
                   "year1", "day1", "month1",
                   "sortval", "newyear", "person", 
                   "sort_as", "display_as"]
