 #
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Gerald Britton <gerald.britton@gmail.com>
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

# $Id: html.py 10874 2009-03-03 18:00:00Z gbritton $

#------------------------------------------------------------------------
#
# Html
#
#------------------------------------------------------------------------

"""
HTML operations.

This module exports one class and one function.

"""

__all__ = ['Html','newpage']

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------

from gen.plug import PluginManager, Plugin

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# XHTML DOCTYPE constants to be used in <!DOCTYPE ... > statements
#
#------------------------------------------------------------------------
_XHTML10_STRICT = 'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n' \
                  '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'
_XTHML10_TRANS = 'PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"'
_XHTML10_FRAME = 'PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'
_XHTML11 = 'PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n' \
           '\t"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
_XHTML10_BASIC = 'PUBLIC "-//W3C//DTD XHTML Basic 1.0//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml-basic/xhtml-basic10.dtd"'
_XHTML11_BASIC = 'PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"\n ' \
                 '\t"http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd"'

#------------------------------------------------------------------------
#
# XML Namespace constant for use in <html xmlns=...> tags 
#
#------------------------------------------------------------------------

_XMLNS = "http://www.w3.org/1999/xhtml"

#------------------------------------------------------------------------
#
# local constants.
#
#------------------------------------------------------------------------

_START_CLOSE = (
    'area', 
    'base', 
    'br', 
    'frame', 
    'hr',
    'img', 
    'input', 
    'link', 
    'meta', 
    'param'
    )

#------------------------------------------------------------------------
#
# helper functions.
#
#------------------------------------------------------------------------

def print_(line):
    """
    Print function
    """
    print line

def newpage(title='Title', encoding='utf-8', lang='en'):
    """
    This function prepares a new Html class based page and returns

    @type  title: string
    @param title: title for HTML page. Default='Title'
    @type  encoding: string
    @param encoding: encoding to be used. Default = 'utf-8'
    @type  lang: string
    @param lang: language to be used. Defaul = 'en'
    @rtype:   three object references
    @return:  references to the newly-created Html instances for
              page, head and body
    """
    meta1 = 'http-equiv="content-type" content="text/html;charset=%s"'
    meta2 = 'http-equiv="Content-Style-Type" content="text/css"'
    page = Html(
         xmlns=_XMLNS, 
         attr='xml:lang="%s" lang="%s"' % ((lang,)*2)
         )
    page.addXML(encoding=encoding)
    page.addDOCTYPE()
    head = Html('head')
    head += Html('title', title, inline=True, indent=True)
    head += Html('meta', attr=meta1 % encoding, indent=True)
    head += Html('meta', attr=meta2, indent=True)
    body = Html('body')
    page += (head, body)
    return page, head, body

#------------------------------------------------------------------------
#
# Html class.
#
#------------------------------------------------------------------------

class Html(list):
    """
    HTML class: Manages a rooted tree of HTML objects
    """
    __slots__ = ['items', 'indent', 'inline', 'end']
#
    def __init__(self, tag='html', *args, **keywargs):
        """
        Class Constructor: Returns a new instance of the Html class
        
        @type  tag: string
        @param tag: The HTML tag. Default is 'html'
        @type  args: optional positional parameters
        @param args: 0 more positional arguments to be inserted between
                     opening and closing HTML tags.
        @type  indent: boolean
        @param indent: True  ==> indent this object with respect to its parent
                       False ==> do not indent this object
                       Defauls to False
        @type  inline: boolean
        @param inline: True  ==> instructs the write() method to output this
                                 object and any child objects as a single string
                       False ==> output this object and its contents one string
                                 at a time
                       Defaults to False
        @type  close: boolean or None
        @param close: True  ==> this tag should be closed normally
                                e.g. <tag>...</tag>
                      False ==> this tag should be automatically closed
                                e.g. <tag />
                      None  ==> do not provide any closing for this tag
        @type  keywargs: optional keyword parameters
        @param keywargs: 0 or more keyword=argument pairs that should be
                         copied into the opening tag as keyword="argument"
                         attributes
        @rtype:   object reference
        @return:  reference to the newly-created Html instance
        """
#
        super(Html, self).__init__([])
        attr, indent, close, inline = '', False, True, False
#
#       Handle keyword arguments passed to this constructor.
#       Keywords that we process directly are handled. 
#       Keywords we don't recognize are passed into the 
#       opening tag.
#
        for keyw, arg in keywargs.iteritems():
            if keyw in ['indent', 'close', 'inline'] and \
               arg in [True, False, None]:
                exec '%s = %s' % (keyw, arg)            # keep these settings
            elif keyw == 'attr':                        # pass attributes along
                attr += ' ' + arg
            elif keyw[-1] == '_':                       # avoid Python conflicts
                attr += ' %s="%s"' % (keyw[:-1], arg)   # pass keyword arg along
            else:
                attr += ' %s="%s"' % (keyw, arg)        # pass keyword arg along
#
        self.indent = indent                                
        self.inline = inline
        self.end = close
#
        if tag[0] == '<':               # did caller provide preformatted tag?
            self += [tag]
            self.end = None
        else: 
            if tag in _START_CLOSE:         # if tag in special list
                self.end = close = False    #   it needs no closing tag
            begin = '<%s%s%s>' % (      # build opening tag; pass in attributes
                tag,
                attr,
                ('' if close or close is None else ' /')
                )
            self += [begin] + list(args)    # add beginning tag to list
            super(Html, self).extend(       # add closing tag if necessary
                ['</%s>' % tag] if close else []
                )
#
    def __add__(self, value):
        """
        Overload function for + and += operators

        @type  value: object
        @param value: object to be added

        @rtype:  object reference
        @return: reference to object with new value added
        """
        if isinstance(value, Html) or not hasattr(value, '__iter__'):
            value = [value]
        index = len(self) - (1 if self.end else 0)
        self[index:index] = value
        return self
#
    __iadd__ = append = extend = __add__
#
    def replace(self, cur_value, value):
        """
        Replace current value with new value

        @type  cur_value: object
        @param cur_value: value of object to be replaced
        @type  value: object
        @param value: replacement value

        @rtype:  object reference
        @return: reference to object with new value added
        """
        self[self.index(cur_value)] = value
#
    def __sub__(self, value):
        """
        Overload function for - and -= operators
        @type  value: object
        @param value: object to be removed

        @rtype:  object reference
        @return: reference to object with value removed
        """
        del self[self.index(value)]
        return self
#
    __isub__ = remove = __sub__
#
    def __str__(self):
        """
        Returns string representation

        @rtype:  string
        @return: string representatiof object
        """
        return '%s'*len(self) % tuple(self[:])
#
    def __iter__(self):
        """
        Iterator function: returns a generator that performs an
        insertion-order tree traversal and yields each item found.
        """
        for item in self[:]:                    # loop through all list elements
            if isinstance(item, Html):     # if nested list found
                for sub_item in item:           #     recurse
                    yield sub_item
            else:
                yield item
#
    iterkeys = itervalues = iteritems = __iter__
#
    def write(self, method=print_, tabs=''):
        """
        Output function: performs an insertion-order tree traversal
        and calls supplied method for each item found.

        @type  method: function reference
        @param method: function to call with each item found
        @type  tabs: string
        @oaram tabs: starting indentation
        """
        tabs += '\t' if self.indent else ''
        if self.inline:                         # if inline, write all list and
            method('%s%s' % (tabs, self))       # nested list elements
#
        else:
            for item in self[:]:                # else write one at a time
                if isinstance(item, Html):
                    item.write(method=method, tabs=tabs)  # recurse if nested
                else:
                    method('%s%s' % (tabs, item))         # else write the line
#
    def addXML(self, version=1.0, encoding="UTF-8", standalone="no"):
        """
        Add an XML statement to the start of the list for this object

        @type  version: decimal number
        @param version: version of XML to be used. Defaults to 1.0
        @type  encoding: string
        @param encoding: encoding method to be used. Defaults to "UTF-8"
        @type  standalone: string
        @param standalone: "yes" or "no".  Defaults to "no"
        """
        xml = '<?xml %s %s %s?>' % (
            'version="%s"' % version,
            'encoding="%s"' % encoding,
            'standalone="%s"' % standalone
            )
        self.insert(0, xml)
#
    def addDOCTYPE(self, name='html', external_id=_XHTML10_STRICT, *args):
        """
        Add a DOCTYPE statement to the start of the list

        @type  name: string
        @param name: name of this DOCTYPE. Defaults to "html"
        @type  external_id: string
        @param external_id: external identifier of this DOCTYPE. 
                            Defaults to XHTML 1.0 STRICT
        @type  args: object
        @param args: 0 or more positional parameters to be added to this    
                     DOCTYPE.
        """
        doctype = '<!DOCTYPE %s %s%s>' % (
            name, 
            external_id,
            ' %s'*len(args) % args
            )
        if len(self) and self[0][:6] == '<?xml ':
            self.insert(1, doctype)
        else:
            self.insert(0, doctype)

# ------------------------------------------
#
#            Register Plugin
#
# -------------------------------------------
PluginManager.get_instance().register_plugin( 
Plugin(
    name = __name__,
    description = _("Manages an HTML DOM tree."),
    module_name = __name__ 
      )
)

