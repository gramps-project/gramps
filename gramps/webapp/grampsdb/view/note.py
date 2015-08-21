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
from gramps.webapp.utils import _, boolean, update_last_changed, StyledNoteFormatter, parse_styled_text, build_search, db
from gramps.webapp.grampsdb.models import Note
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.libdjango import DjangoInterface
from gramps.webapp.djangodb import DbDjango

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()
snf = StyledNoteFormatter(db)

# add a note to a person:
# /note/add/person/c51759195496de06da3ca5ba2c1

def process_note_on_name(request, action, handle, order):
    # add, edit, delete
    raise Exception("testing")

def process_note(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Note")
    context["tviews"] = _("Notes")
    context["action"] = "view"
    view_template = "view_note_detail.html"

    if handle == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete, share, save-share
    if act == "share":
        item, handle = add_to
        context["pickform"] = PickForm("Pick note",
                                       Note,
                                       (),
                                       request.POST)
        context["object_handle"] = handle
        context["object_type"] = item
        return render_to_response("pick.html", context)
    elif act == "save-share":
        item, handle = add_to
        pickform = PickForm("Pick note",
                            Note,
                            (),
                            request.POST)
        if pickform.data["picklist"]:
            parent_model = dji.get_model(item) # what model?
            parent_obj = parent_model.objects.get(handle=handle) # to add
            ref_handle = pickform.data["picklist"]
            ref_obj = Note.objects.get(handle=ref_handle)
            dji.add_note_ref(parent_obj, ref_obj)
            parent_obj.save_cache() # rebuild cache
            return redirect("/%s/%s%s#tab-notes" % (item, handle, build_search(request)))
        else:
            context["pickform"] = pickform
            context["object_handle"] = handle
            context["object_type"] = item
            return render_to_response("pick.html", context)
    elif act == "add":
        note = Note(gramps_id=dji.get_next_id(Note, "N"))
        notetext = ""
        noteform = NoteForm(instance=note, initial={"notetext": notetext})
        noteform.model = note
    elif act in ["view", "edit"]:
        note = Note.objects.get(handle=handle)
        genlibnote = db.get_note_from_handle(note.handle)
        notetext = snf.format(genlibnote)
        noteform = NoteForm(instance=note, initial={"notetext": notetext})
        noteform.model = note
    elif act == "save":
        note = Note.objects.get(handle=handle)
        notetext = ""
        noteform = NoteForm(request.POST, instance=note, initial={"notetext": notetext})
        noteform.model = note
        if noteform.is_valid():
            update_last_changed(note, request.user.username)
            notedata = parse_styled_text(noteform.data["notetext"])
            note.text = notedata[0]
            note = noteform.save()
            dji.save_note_markup(note, notedata[1])
            note.save_cache()
            notetext = noteform.data["notetext"]
            act = "view"
        else:
            notetext = noteform.data["notetext"]
            act = "edit"
    elif act == "create":
        note = Note(handle=create_id())
        notetext = ""
        noteform = NoteForm(request.POST, instance=note, initial={"notetext": notetext})
        noteform.model = note
        if noteform.is_valid():
            update_last_changed(note, request.user.username)
            notedata = parse_styled_text(noteform.data["notetext"])
            note.text = notedata[0]
            note = noteform.save()
            dji.save_note_markup(note, notedata[1])
            note.save_cache()
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_note_ref(obj, note)
                obj.save_cache()
                return redirect("/%s/%s#tab-notes" % (item, handle))
            notetext = noteform.data["notetext"]
            act = "view"
        else:
            notetext = noteform.data["notetext"]
            act = "add"
    elif act == "delete":
        # FIXME: delete markup too for this note
        note = Note.objects.get(handle=handle)
        note.delete()
        return redirect("/note/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["noteform"] = noteform
    context["object"] = note
    context["notetext"] = notetext
    context["note"] = note
    context["action"] = act

    return render_to_response(view_template, context)
