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

"""
HTML operations.

This module exports one class and two functions.

"""

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
#
class Html(list):
    """
    HTML class.
    """
    __slots__ = ['items','indent','inline','end']
#
    def __init__(self, tag='html', *args, **keywargs):
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
                exec '%s = %s' % (keyw, arg)                # keep these settings
            elif keyw == 'attr':                            # pass attributes along
                attr += ' ' + arg
            elif keyw[-1] == '_':                           # avoid Python conflicts
                attr += ' %s="%s"' % (keyw[:-1], arg)       # pass keyword arg along
            else:
                attr += ' %s="%s"' % (keyw, arg)            # pass keyword arg along
#
        self.indent = indent                                
        self.inline = inline
        self.end = close
#
        if tag[0] == '<':               # did caller provide preformatted tag?
            self += [tag]
            self.end = None
        else: 
            if tag in _START_CLOSE:     # is tag in special list that need no closer?
                self.end = close = False
            begin = '<%s%s%s>' % (      # build opening tag, passing in attributes
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
        if isinstance(value, Html) or not hasattr(value, '__iter__'):
            value = [value]
        index = len(self) - (1 if self.end else 0)
        self[index:index] = value
        return self
#
    __iadd__ = append = extend = __add__
#
    def replace(self, cur_value, value):
        self[self.index(cur_value)] = value
#
    def __sub__(self, value):
        del self[self.index(value)]
        return self
#
    __isub__ = remove = __sub__
#
    def print_(data):
        print data
#
    def __str__(self):
        return '%s'*len(self) % tuple(self[:])
#
    def __iter__(self):
        for item in self[:]:                    # loop through all list elements
            if isinstance(item, self.Html):     # if nested list found
                for sub_item in item:           #     recurse
                    yield sub_item
            else:
                yield item
#
    iterkeys = itervalues = iteritems = __iter__
#
    def write(self, method=print_, tabs=''):
        tabs += '\t' if self.indent else ''
        if self.inline:                         # if inline, write all list and
            method('%s%s' % (tabs,self))        # nested list elements
#
        else:
            for item in self[:]:                # not inline: write one at a time
                if isinstance(item, Html):
                    item.write(method=method, tabs=tabs)    # recurse if nested
                else:
                    method('%s%s' % (tabs, item))           # write the line if not
#
    def addXML(self, version=1.0, encoding="UTF-8", standalone="no"):
        xml = XML(version=version, encoding=encoding, standalone=standalone)
        self.insert(0, xml)
#
    def addDOCTYPE(self, name='html', external_id=_XHTML10_STRICT, *args):
        doctype = DOCTYPE(name='html', external_id=external_id, *args)
        if len(self) and self[0][:6] == '<?xml ':
            self.insert(1, doctype)
        else:
            self.insert(0, doctype)
#
def XML(version=1.0, encoding="UTF-8", standalone="no"):
    return '<?xml %s %s %s?>' % (
        'version="%s"' % version,
        'encoding="%s"' % encoding,
        'standalone="%s"' % standalone
        )
#
def DOCTYPE(name='html', external_id=_XHTML10_STRICT, *args):
    return '<!DOCTYPE %s %s%s>' % (
        name, 
        external_id,
        ' %s'*len(args) % args
        )

