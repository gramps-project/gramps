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
from webapp.utils import _, boolean, update_last_changed, build_search
from webapp.grampsdb.models import Family
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface
from gen.utils.id import create_id

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_family(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Family")
    context["tviews"] = _("Familes")

    if handle == "add":
        act = "add"
    if request.POST.has_key("action"):
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete, share, save-share
    if act == "share":
        # Adds a person to an existing family
        item, handle = add_to
        context["pickform"] = PickForm("Pick family", 
                                       Family, 
                                       (),
                                       request.POST)     
        context["object_handle"] = handle
        context["object_type"] = "person"
        return render_to_response("pick.html", context)
    elif act == "save-share":
        item, handle = add_to 
        pickform = PickForm("Pick family", 
                            Family, 
                            (),
                            request.POST)
        if pickform.data["picklist"]:
            person = Person.objects.get(handle=handle) # to add
            ref_handle = pickform.data["picklist"]
            ref_obj = Family.objects.get(handle=ref_handle) 
            if item == "child":
                dji.add_child_ref_default(ref_obj, person) # add person to family
                person.parent_families.add(ref_obj) # add family to child
            elif item == "spouse":
                if person.gender_type.name == "Female":
                    ref_obj.mother = person
                elif person.gender_type.name == "Male":
                    ref_obj.father = person
                else:
                    ref_obj.father = person # FIXME: Unknown gender, add to open
                person.families.add(ref_obj) # add family to person
            ref_obj.save()
            person.save()
            dji.rebuild_cache(person) # rebuild child
            dji.rebuild_cache(ref_obj) # rebuild cache
            return redirect("/%s/%s%s#tab-references" % ("person", handle, build_search(request)))
        else:
            context["pickform"] = pickform
            context["object_handle"] = handle
            context["object_type"] = "person"
            return render_to_response("pick.html", context)
    elif act == "add":
        family = Family(
            gramps_id=dji.get_next_id(Family, "F"),
            family_rel_type=FamilyRelType.objects.get(
                val=FamilyRelType._DEFAULT[0]))
        if add_to:
            what, phandle = add_to
            person = Person.objects.get(handle=phandle)
            gender = person.gender_type.name # Male, Female, Unknown
            if what == "spouse":
                if gender == "Male":
                    family.father = person
                elif gender == "Female":
                    family.mother = person
            elif what == "child":
                pass # FIXME: can't show child in table? 
                     # Table from children_table
            else: # unknown gender!
                family.father = person
        familyform = FamilyForm(instance=family)
        familyform.model = family
    elif act in ["view", "edit"]: 
        family = Family.objects.get(handle=handle)
        familyform = FamilyForm(instance=family)
        familyform.model = family
    elif act == "save": 
        family = Family.objects.get(handle=handle)
        familyform = FamilyForm(request.POST, instance=family)
        familyform.model = family
        if familyform.is_valid():
            update_last_changed(family, request.user.username)
            family = familyform.save()
            # FIXME: multiple families with same parents?
            # FIXME: remove family from previous mother/father?
            if family.mother:
                if family not in family.mother.families.all():
                    family.mother.families.add(family)
            if family.father:
                if family not in family.father.families.all():
                    family.father.families.add(family)
            dji.rebuild_cache(family)
            act = "view"
        else:
            act = "edit"
    elif act == "create": 
        family = Family(family_rel_type=FamilyRelType.objects.get(
                val=FamilyRelType._DEFAULT[0]),
                        handle=create_id())
        familyform = FamilyForm(request.POST, instance=family)
        familyform.model = family
        if familyform.is_valid():
            update_last_changed(family, request.user.username)
            family = familyform.save()
            # FIXME: multiple families with same parents?
            # FIXME: remove family from previous mother/father?
            if family.mother:
                if family not in family.mother.families.all():
                    family.mother.families.add(family)
            if family.father:
                if family not in family.father.families.all():
                    family.father.families.add(family)
            dji.rebuild_cache(family)
            if add_to: # add child or spouse to family
                item, handle = add_to
                person = Person.objects.get(handle=handle)
                if item == "child":
                    dji.add_child_ref_default(family, person) # add person to family
                    person.parent_families.add(family) # add family to child
                elif item == "spouse":
                    if person.gender_type.name == "Female":
                        family.mother = person
                    elif person.gender_type.name == "Male":
                        family.father = person
                    else:
                        family.father = person # FIXME: Unknown gender, add to open
                    person.families.add(family) # add family to person
                family.save()
                person.save()
                dji.rebuild_cache(person) # rebuild child
                dji.rebuild_cache(family) # rebuild cache
                return redirect("/%s/%s" % ("person", handle))
            act = "view"
        else:
            act = "add"
    elif act == "delete": 
        family = Family.objects.get(handle=handle)
        family.delete()
        return redirect("/family/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["familyform"] = familyform
    context["object"] = family
    context["family"] = family
    context["action"] = act
    view_template = "view_family_detail.html"
    
    return render_to_response(view_template, context)
