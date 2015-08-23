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
from gramps.webapp.grampsdb.models import Tag
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_tag(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Tag")
    context["tviews"] = _("Tags")
    context["action"] = "view"
    view_template = "view_tag_detail.html"

    if handle == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if act == "add":
        tag = Tag()
        tagform = TagForm(instance=tag)
        tagform.model = tag
    elif act in ["view", "edit"]:
        tag = Tag.objects.get(handle=handle)
        tagform = TagForm(instance=tag)
        tagform.model = tag
    elif act == "save":
        tag = Tag.objects.get(handle=handle)
        tagform = TagForm(request.POST, instance=tag)
        tagform.model = tag
        if tagform.is_valid():
            update_last_changed(tag, request.user.username)
            tag = tagform.save()
            act = "view"
        else:
            act = "edit"
    elif act == "create":
        tag = Tag(handle=create_id())
        tagform = TagForm(request.POST, instance=tag)
        tagform.model = tag
        if tagform.is_valid():
            update_last_changed(tag, request.user.username)
            tag = tagform.save()
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_tag_ref_default(obj, tag)
                obj.save_cache()
                return redirect("/%s/%s#tab-tags" % (item, handle))
            act = "view"
        else:
            act = "add"
    elif act == "delete":
        tag = Tag.objects.get(handle=handle)
        tag.delete()
        return redirect("/tag/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["tagform"] = tagform
    context["object"] = tag
    context["tag"] = tag
    context["action"] = act

    return render_to_response(view_template, context)
