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
# constants
#
#------------------------------------------------------------------------
_XHTML1_STRICT = 'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n' \
          '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'

class Html(list):
    """
    HTML class.
    """
    __slots__ = ['items','indent','inline','end']
#
    def __init__(self, tag='html', *args, **keywargs):
        super(Html, self).__init__([])
        attr, indent, close, inline = '', False, True, False
        for keyw, arg in keywargs.iteritems():
            if keyw in ['indent', 'close', 'inline'] and arg in [True, False, None]:
                exec '%s = %s' % (keyw, arg)
            elif keyw == 'attr':
                attr += ' ' + arg
            elif keyw[0] == '_':
                attr += ' %s="%s"' % (keyw[1:], arg)
            else:
                attr += ' %s="%s"' % (keyw, arg)
#
        self.indent = indent
        self.inline = inline
        self.end = close
#
        if tag[0] == '<':
            self += [tag]
            self.end = None
        else: 
            if tag in ['area', 'base', 'br', 'frame', 'hr',
                       'img', 'input', 'link', 'meta', 'param']:
                self.end = close = False
            begin = '<%s%s%s>' % (
                tag,
                attr,
                ('' if close or close is None else ' /')
                )
            self += [begin] + list(args)
            super(Html, self).extend(['</%s>' % tag] if close else [])
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
    def _print(data):
        print data
#
    def __str__(self):
        return '%s'*len(self) % tuple(self[:])
#
    def __iter__(self):
        for item in self[:]:
            if isinstance(item, self.Html):
                for sub_item in item:
                    yield sub_item
            else:
                yield item
#
    iterkeys = itervalues = iteritems = __iter__
#
    def write(self, method=_print, tabs=''):
        tabs += '\t' if self.indent else ''
        if self.inline:
            method('%s%s' % (tabs,self))
#
        else:
            for item in self[:]:
                if isinstance(item, Html):
                    item.write(method=method, tabs=tabs)
                else:
                    method('%s%s' % (tabs, item))
#
    def addXML(self, version=1.0, encoding="UTF-8", standalone="no"):
        xml = XML(version=version, encoding=encoding, standalone=standalone)
        self.insert(0, xml)
#
    def addDOCTYPE(self, name='html', external_id=_XHTML1_STRICT, *args):
        doctype = DOCTYPE(name='html', external_id=_XHTML1_STRICT, *args)
        if len(self) and self[0][:6] == '<?xml ':
            self.insert(1, doctype)
        else:
            self.insert(0, doctype)

def XML(version=1.0, encoding="UTF-8", standalone="no"):
    return '<?xml %s %s %s?>' % (
        'version="%s"' % version,
        'encoding="%s"' % encoding,
        'standalone="%s"' % standalone
        )

def DOCTYPE(name='html', external_id=_XHTML1_STRICT, *args):
    return '<!DOCTYPE %s %s%s>' % (
        name, 
        external_id,
        ' %s'*len(args) % args
        )

