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
from webapp.utils import _, boolean, update_last_changed, StyledNoteFormatter, parse_styled_text
from webapp.grampsdb.models import Note
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface
from webapp.dbdjango import DbDjango

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()
db = DbDjango()
snf = StyledNoteFormatter(db)

def process_note(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Note")
    context["tviews"] = _("Notes")
    context["action"] = "view"
    view_template = "view_note_detail.html"

    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        note = Note(gramps_id=dji.get_next_id(Note, "N"))
        notetext = ""
        noteform = NoteForm(instance=note, initial={"notetext": notetext})
        noteform.model = note
    elif action in ["view", "edit"]: 
        note = Note.objects.get(handle=handle)
        genlibnote = db.get_note_from_handle(note.handle)
        notetext = snf.format(genlibnote)
        noteform = NoteForm(instance=note, initial={"notetext": notetext})
        noteform.model = note
    elif action == "save": 
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
            dji.rebuild_cache(note)
            notetext = noteform.data["notetext"] 
            action = "view"
        else:
            notetext = noteform.data["notetext"] 
            action = "edit"
    elif action == "create": 
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
            dji.rebuild_cache(note)
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_note_ref(obj, note)
                return redirect("/%s/%s#tab-notes" % (item, handle))
            notetext = noteform.data["notetext"] 
            action = "view"
        else:
            notetext = noteform.data["notetext"] 
            action = "add"
    elif action == "delete": 
        # FIXME: delete markup too for this note
        note = Note.objects.get(handle=handle)
        note.delete()
        return redirect("/note/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["noteform"] = noteform
    context["object"] = note
    context["notetext"] = notetext
    context["note"] = note
    context["action"] = action
    
    return render_to_response(view_template, context)
