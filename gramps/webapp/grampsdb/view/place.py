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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Views for Person, Name, and Surname """

## Gramps Modules
from gramps.webapp.utils import _, boolean, update_last_changed
from gramps.webapp.grampsdb.models import Place
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_place(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Place")
    context["tviews"] = _("Places")
    context["action"] = "view"
    view_template = "view_place_detail.html"

    if handle == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if act == "add":
        place = Place(gramps_id=dji.get_next_id(Place, "P"))
        placeform = PlaceForm(instance=place)
        placeform.model = place
    elif act in ["view", "edit"]:
        place = Place.objects.get(handle=handle)
        placeform = PlaceForm(instance=place)
        placeform.model = place
    elif act == "save":
        place = Place.objects.get(handle=handle)
        placeform = PlaceForm(request.POST, instance=place)
        placeform.model = place
        if placeform.is_valid():
            update_last_changed(place, request.user.username)
            place = placeform.save()
            act = "view"
        else:
            act = "edit"
    elif act == "create":
        place = Place(handle=create_id())
        placeform = PlaceForm(request.POST, instance=place)
        placeform.model = place
        if placeform.is_valid():
            update_last_changed(place, request.user.username)
            place = placeform.save()
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_place_ref(obj, place.handle)
                obj.save_cache()
                return redirect("/%s/%s#tab-places" % (item, handle))
            act = "view"
        else:
            act = "add"
    elif act == "delete":
        place = Place.objects.get(handle=handle)
        place.delete()
        return redirect("/place/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["placeform"] = placeform
    context["object"] = place
    context["place"] = place
    context["action"] = act

    return render_to_response(view_template, context)
