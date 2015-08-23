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

# webapp/grampsdb/templatetags/my_tags.py

import re

from django import template
from django.template import Library
from django.utils.safestring import mark_safe
from gramps.webapp.utils import *
from gramps.webapp.grampsdb.views import VIEWS
import gramps.webapp.utils

#escape = lambda text: text

register = Library()

def eval_template_exp(item, context):
    """
    Wrapper to allow negation of variables in templates. Use
    "!variable".
    """
    if item.var.startswith("!"):
        return not template.Variable(item.var[1:]).resolve(context)
    else:
        return item.resolve(context)

class TemplateNode(template.Node):
    def __init__(self, args, var_name, func):
        self.args = list(map(template.Variable, args))
        self.var_name = var_name
        self.func = func

    def render(self, context):
        value = self.func(*[eval_template_exp(item, context)
                            for item in self.args])
        if self.var_name:
            context[self.var_name] = value
            return ''
        else:
            return value

def parse_tokens(tokens):
    items = tokens.split_contents()
    # {% tag_name arg1 arg2 arg3 as variable %}
    # {% tag_name arg1 arg2 arg3 %}
    tag_name = items[0]
    if "as" == items[-2]:
        var_name = items[-1]
        args = items[1:-2]
    else:
        var_name = None
        args = items[1:]
    return (tag_name, args, var_name)

def make_tag(func):
    def do_func(parser, tokens):
        tag_name, args, var_name = parse_tokens(tokens)
        return TemplateNode(args, var_name, func)
    return do_func

for filter_name in util_filters:
    func = getattr(gramps.webapp.utils, filter_name)
    func.is_safe = True
    register.filter(filter_name, func)

for tag_name in util_tags:
    func = getattr(gramps.webapp.utils, tag_name)
    register.tag(tag_name, make_tag(func))

probably_alive.is_safe = True
register.filter('probably_alive', probably_alive)

format_number.is_safe = True
register.filter('format_number', format_number)

table_count.is_safe = True
register.filter('table_count', table_count)

person_get_birth_date.is_safe = True
register.filter('person_get_birth_date', person_get_birth_date)

person_get_death_date.is_safe = True
register.filter('person_get_death_date', person_get_death_date)

display_date.is_safe = True
register.filter('display_date', display_date)

person_get_event.is_safe = True
register.filter('person_get_events', person_get_event)

def preview(text, width=40):
    text = text.replace("\n", " ")
    #return escape(text[:width])
    if len(text) > width:
        return text[:width] + "..."
    return text
#preview.is_safe = True
register.filter('preview', preview)

make_name.is_safe = True
register.filter('make_name', make_name)

def preferred(person):
    try:
        name = person.name_set.get(preferred=True)
    except:
        name = None
    return name
preferred.is_safe = True
register.filter('preferred', preferred)

def missing(data):
    if data.strip() == "":
        return "[Missing]"
    #return escape(data)
    return data
#missing.is_safe = True
register.filter('missing', missing)

def getViewName(item):
    for view in VIEWS:
        if view[1] == item:
            return view[0]
    if item == "name":
        return "Names"
    return "Unknown View"

def breadcrumb(path, arg=None):
    if arg:
        path = path.replace("{0}", arg)
    retval = ""
    for item in path.split("||"):
        p, name = item.split("|", 1)
        if retval != "":
            retval += " > "
        retval += '<a href="%s"><b>%s</b></a>' % (p.strip(), name.strip())
    return "<p>%s</p>" % retval
breadcrumb.is_safe = True
register.filter('breadcrumb', breadcrumb)

def format(string, arg0=None, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None):
    try:
        if arg0 is None:
            return string
        elif arg1 is None:
            return string % arg0
        elif arg2 is None:
            return string % (arg0, arg1)
        elif arg3 is None:
            return string % (arg0, arg1, arg2)
        elif arg4 is None:
            return string % (arg0, arg1, arg2, arg3)
        elif arg5 is None:
            return string % (arg0, arg1, arg2, arg3, arg4)
        elif arg6 is None:
            return string % (arg0, arg1, arg2, arg3, arg4, arg5)
        else:
            return string % (arg0, arg1, arg2, arg3, arg4, arg5, arg6)
    except:
        return string
format.is_safe = True
register.simple_tag(format)

def make_args(search, page):
    return gramps.webapp.utils.build_args(search=search, page=page)
make_args.is_safe = True
register.simple_tag(make_args)

def format_color(color):
    return color[0:3] + color[5:7] + color[9:11]
format_color.is_safe = True
register.filter("format_color", format_color)

def currentSection(view1, view2): # tview, menu
    if view1.strip().lower() in [view[1] for view in VIEWS] and view2 == "browse":
        return "class=CurrentSection"
    elif view1.strip().lower() == view2.strip().lower():
        return "class=CurrentSection"
    return ""
currentSection.is_safe = True
register.filter('currentSection', currentSection)

def row_count(row, page):
    return row + (page.number - 1) * page.paginator.per_page

register.filter('row_count', row_count)

def table_header(context, headers = None):
    # add things for the header here
    if headers:
        context["headers"] = headers
    return context

register.inclusion_tag('table_header.html',
                       takes_context=True)(table_header)

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    results_this_page = context["page"].object_list.count()
    context.update({'results_this_page': results_this_page,})
    return context

register.inclusion_tag('paginator.html',
                       takes_context=True)(paginator)
