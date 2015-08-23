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
from gramps.webapp.utils import _, boolean, update_last_changed, build_search
from gramps.webapp.grampsdb.models import Citation
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_citation(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Citation")
    context["tviews"] = _("Citations")
    context["action"] = "view"
    view_template = "view_citation_detail.html"

    if handle == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete, share, save-share
    if act == "share":
        item, handle = add_to
        context["pickform"] = PickForm("Pick citation",
                                       Citation,
                                       (),
                                       request.POST)
        context["object_handle"] = handle
        context["object_type"] = item
        return render_to_response("pick.html", context)
    elif act == "save-share":
        item, handle = add_to
        pickform = PickForm("Pick citation",
                            Citation,
                            (),
                            request.POST)
        if pickform.data["picklist"]:
            parent_model = dji.get_model(item) # what model?
            parent_obj = parent_model.objects.get(handle=handle) # to add
            ref_handle = pickform.data["picklist"]
            ref_obj = Citation.objects.get(handle=ref_handle)
            dji.add_citation_ref_default(parent_obj, ref_obj)
            parent_obj.save_cache() # rebuild cache
            return redirect("/%s/%s%s#tab-citations" % (item, handle, build_search(request)))
        else:
            context["pickform"] = pickform
            context["object_handle"] = handle
            context["object_type"] = item
            return render_to_response("pick.html", context)
    elif act == "add":
        source = Source(gramps_id=dji.get_next_id(Source, "S"))
        sourceform = SourceForm(instance=source)
        sourceform.model = source
        citation = Citation(source=source, gramps_id=dji.get_next_id(Citation, "C"))
        citationform = CitationForm(instance=citation)
        citationform.model = citation
    elif act in ["view", "edit"]:
        citation = Citation.objects.get(handle=handle)
        citationform = CitationForm(instance=citation)
        citationform.model = citation
        source = citation.source
        sourceform = SourceForm(instance=source)
        sourceform.model = source
    elif act == "save":
        citation = Citation.objects.get(handle=handle)
        citationform = CitationForm(request.POST, instance=citation)
        citationform.model = citation
        if citationform.is_valid():
            update_last_changed(citation, request.user.username)
            citation = citationform.save()
            act = "view"
        else:
            act = "edit"
    elif act == "create":
        source = Source(handle=create_id())
        sourceform = SourceForm(request.POST, instance=source)
        sourceform.model = source
        citation = Citation(handle=create_id(), source=source)
        citationform = CitationForm(request.POST, instance=citation)
        citationform.model = citation
        if citationform.is_valid() and sourceform.is_valid():
            update_last_changed(source, request.user.username)
            source = sourceform.save()
            citation.source = source
            update_last_changed(citation, request.user.username)
            citation = citationform.save(save_cache=False)
            source.save_cache()
            citation.save_cache()
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_citation_ref(obj, citation.handle)
                obj.save_cache()
                return redirect("/%s/%s#tab-citations" % (item, handle))
            act = "view"
        else:
            act = "add"
    elif act == "delete":
        citation = Citation.objects.get(handle=handle)
        citation.delete()
        return redirect("/citation/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["citationform"] = citationform
    context["sourceform"] = sourceform
    context["object"] = citation
    context["citation"] = citation
    context["source"] = source
    context["action"] = act

    return render_to_response(view_template, context)
