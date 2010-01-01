import re

from django import template
from django.template import escape, Library
from django.utils.safestring import mark_safe
from web.utils import *
import web.utils

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
        self.args = map(template.Variable, args)
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
    func = getattr(web.utils, filter_name)
    func.is_safe = True
    register.filter(filter_name, func)

for tag_name in util_tags:
    func = getattr(web.utils, tag_name)
    register.tag(tag_name, make_tag(func))

probably_alive.is_safe = True
register.filter('probably_alive', probably_alive)

format_number.is_safe = True
register.filter('format_number', format_number)

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
    return escape(text[:width])
preview.is_safe = True
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
    return escape(data)
missing.is_safe = True
register.filter('missing', missing)

def currentSection(view1, view2):
    if view1.strip().lower() == view2.strip().lower():
        return "CurrentSection"
    return "OtherSection"
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
