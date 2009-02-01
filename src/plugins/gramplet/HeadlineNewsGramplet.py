# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

# $Id$

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import re
import gobject
import urllib
import sys

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from const import URL_WIKISTRING
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class HeadlineNewsGramplet(Gramplet):
    """
    Headlines News Gramplet reads the Headline News every hour.
    """
    RAW = URL_WIKISTRING + "%s&action=raw"
    URL = URL_WIKISTRING + "%s"

    def init(self):
        """
        Initialize gramplet. Start up update timer.
        """
        self.set_tooltip(_("Read headline news from the GRAMPS wiki"))
        self.update_interval = 3600 * 1000 # in miliseconds (1 hour)
        self.timer = gobject.timeout_add(self.update_interval, 
                                         self.update_by_timer)

    def update_by_timer(self):
        """
        Update, and return True to continually update on interval.
        """
        self.update()
        return True # keep updating!

    def main(self):
        continuation = self.process('HeadlineNews')
        retval = True
        while retval:
            retval, text = continuation.next()
            self.set_text(text)
            yield True
        self.cleanup(text)
        yield False

    def cleanup(self, text):
        # final text
        text = text.replace("<BR>", "\n")
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        text = text.strip()
        ## Wiki text:
        ### Internal wiki URL with title:
        pattern = re.compile('\[\[(.*?)\|(.*?)\]\]')
        matches = pattern.findall(text)
        for (g1, g2) in matches:
            text = text.replace("[[%s|%s]]" % (g1, g2), 
                                ("""<A HREF="%s">%s</A>""" % 
                                 (self.wiki(g1), self.nice_title(g2))))
        ### Internal wiki URL:
        pattern = re.compile('\[\[(.*?)\]\]')
        matches = pattern.findall(text)
        for match in matches:
            text = text.replace("[[%s]]" % match, 
                                ("""<A HREF="%s">%s</A>""" % 
                                 (self.wiki(match), self.nice_title(match))))
        ### URL with title:
        pattern = re.compile('\[http\:\/\/(.*?) (.*?)\]')
        matches = pattern.findall(text)
        for (g1, g2) in matches:
            text = text.replace("[http://%s %s]" % (g1, g2), 
                                ("""<A HREF="http://%s">%s</A>""" % 
                                 (g1, g2)))
        ### URL:
        pattern = re.compile('\[http\:\/\/(.*?)\]')
        matches = pattern.findall(text)
        count = 1
        for g1 in matches:
            text = text.replace("[http://%s]" % (g1), 
                                ("""<A HREF="http://%s">%s</A>""" % 
                                 (g1, ("[%d]" % count))))
            count += 1
        ### Bold:
        pattern = re.compile("'''(.*?)'''")
        matches = pattern.findall(text)
        for match in matches:
            text = text.replace("'''%s'''" % match, "<B>%s</B>" % match)
        text = """<I>Live update from <A HREF="http://gramps-project.org/">www.gramps-project.org</A></I>:\n\n""" + text
        self.clear_text()
        self.set_use_markup(True)
        try:
            self.render_text(text)
        except:
            cla, exc, trbk = sys.exc_info()
            self.append_text(_("Error") + (" : %s %s\n\n" %(cla, exc)))
            self.append_text(text)
        self.append_text("", scroll_to="begin")

    def wiki(self, title):
        return (self.URL % title)

    def nice_title(self, title):
        return title.replace("_", " ")
        
    def process(self, title):
        #print "processing '%s'..." % title
        title = self.nice_title(title)
        yield True, (_("Reading") + " '%s'..." % title)
        fp = urllib.urlopen(self.RAW % title)
        text = fp.read()
        #text = text.replace("\n", " ")
        html = re.findall('<.*?>', text)
        for exp in html:
            text = text.replace(exp, "")
        text = text.replace("\n", "<BR>")
        fp.close()
        pattern = '{{.*?}}'
        matches = re.findall(pattern, text)
        #print "   before:", text
        for match in matches:
            page = match[2:-2]
            oldtext = match
            if "|" in page:
                template, heading, body = page.split("|", 2)
                if template.lower() == "release":
                    newtext = "GRAMPS " + heading + " released.<BR><BR>"
                else:
                    newtext = "<B>%s</B><BR><BR>" % heading
                newtext += body + "<BR>"
                text = text.replace(oldtext, newtext)
            else: # a macro/redirect
                continuation = self.process("Template:" + page)
                retval = True
                while retval:
                    retval, newtext = continuation.next()
                    yield True, newtext
                text = text.replace(oldtext, newtext)
        #print "    after:", text
        pattern = '#REDIRECT \[\[.*?\]\]'
        matches = re.findall(pattern, text)
        #print "   before:", text
        for match in matches:
            page = match[12:-2]
            oldtext = match
            continuation = self.process(page)
            retval = True
            while retval:
                retval, newtext = continuation.next()
                yield True, newtext
            text = text.replace(oldtext, newtext)
        #print "    after:", text
        yield False, text

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Headline News Gramplet", 
         tname=_("Headline News Gramplet"), 
         height=300,
         expand=True,
         content = HeadlineNewsGramplet,
         title=_("Headline News"),
         )
