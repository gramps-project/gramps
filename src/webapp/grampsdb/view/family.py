# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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
# $Id: utils.py 19637 2012-05-24 17:22:14Z dsblank $
#

""" Views for Person, Name, and Surname """

## Gramps Modules
from webapp.utils import _, boolean, update_last_changed
from webapp.grampsdb.models import Family
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface
from Utils import create_id

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_family(request, context, handle, action): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Family")
    context["tviews"] = _("Familes")

    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        family = Family(
            family_rel_type=FamilyRelType.objects.get(
                val=FamilyRelType._DEFAULT[0]))
        familyform = FamilyForm(instance=family)
        familyform.model = family
    elif action in ["view", "edit"]: 
        family = Family.objects.get(handle=handle)
        familyform = FamilyForm(instance=family)
        familyform.model = family
    elif action == "save": 
        family = Family.objects.get(handle=handle)
        familyform = FamilyForm(request.POST, instance=family)
        familyform.model = family
        if familyform.is_valid():
            update_last_changed(family, request.user.username)
            family = familyform.save()
            dji.rebuild_cache(family)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        family = Family(family_rel_type=FamilyRelType.objects.get(
                val=FamilyRelType._DEFAULT[0]),
                        handle=create_id())
        familyform = FamilyForm(request.POST, instance=family)
        familyform.model = family
        if familyform.is_valid():
            update_last_changed(family, request.user.username)
            family = familyform.save()
            dji.rebuild_cache(family)
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        family = Family.objects.get(handle=handle)
        family.delete()
        return redirect("/family/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["familyform"] = familyform
    context["object"] = family
    context["family"] = family
    context["action"] = action
    view_template = "view_family_detail.html"
    
    return render_to_response(view_template, context)
