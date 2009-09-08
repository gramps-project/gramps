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
from xml.dom import minidom, Node
# FIXME For Python 3:
# Change:
# import urllib
# To:
# import urllib.request
# Change:
# url_info = urllib.urlopen(URL)
# To:
# url_info = urllib.request.urlopen(URL)
import sys
from htmlentitydefs import name2codepoint as n2cp
import re

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
# Local functions
#
#------------------------------------------------------------------------
def substitute(match):
    ent = match.group(2)
    if match.group(1) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)
        if cp:
            return unichr(cp)
        else:
            return match.group()

def decode_html(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute, string)[0]

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
        self.limit = 5
        # Description, Type, URL, Pretty URL for User
        self.feeds = [
            ("GRAMPS Wiki Headline News", "wiki", (self.RAW % "HeadlineNews"), (self.URL % "HeadlineNews")),
            ("GRAMPS Blog Comments", "rss", "http://blog.gramps-project.org/?feed=comments-rss2", None),
            ("GRAMPS Blog Posts",    "rss", "http://blog.gramps-project.org/?feed=rss", None),
            ("GRAMPS Wiki Changes",  "rss", "http://www.gramps-project.org/wiki/index.php?title=Special:RecentChanges&feed=rss", None),
            ("GRAMPS Bugtracker Issues", "rss", "http://www.gramps-project.org/bugs/issues_rss.php?key=ece7d21451d76337acf776c9a4384773", None),
            ("GRAMPS SVN Commits",   "rss", "http://cia.vc/stats/project/Gramps/.rss", None),
            ]
        self.set_tooltip(_("Read GRAMPS headline news"))
        self.update_interval = 3600 * 1000 # in miliseconds (1 hour)
        self.set_use_markup(True)
        self.set_wrap(False)
        self.set_text(_("No Family Tree loaded."))
        self.timer = gobject.timeout_add(self.update_interval, 
                                         self.update_by_timer)

    def update_by_timer(self):
        """
        Update, and return True to continually update on interval.
        """
        self.update()
        return True # keep updating!

    def main(self):
        self.set_text("Loading GRAMPS Headline News...\n")
        fresh = True
        yield True
        for (feed_description, feed_type, feed_url, pretty_url) in self.feeds:
            fp = urllib.urlopen(feed_url)
            if feed_type == "wiki":
                text = fp.read()
                if fresh:
                    self.clear_text()
                    fresh = False
                self.render_text("""<u><b>%s</b></u> [<a href="%s">wiki</a>]\n""" % (feed_description, pretty_url))
                self.render_text(self.decode_wiki(text).strip())
                self.append_text("\n")
                yield True
            elif feed_type == "rss":
                try:
                    xmldoc = minidom.parse(fp)
                except Exception, e:
                    print "Headline News Gramplet Error: RSS parse failed on '%s': %s" % (feed_description, e)
                    continue
                if fresh:
                    self.clear_text()
                    fresh = False
                self.render_text("""<u><b>%s</b></u> [<a href="%s">RSS</a>]\n""" % (feed_description, feed_url))
                yield True
                rootNode = xmldoc.documentElement
                for node in rootNode.childNodes:
                    #print "> ", node.nodeName
                    if (node.nodeName == "channel"):
                        count = 1
                        for node2 in node.childNodes:
                            if count > 5: break
                            if (node2.nodeName == "item"):
                                title = ""
                                link = ""
                                desc = u""
                                # Gather up the data:
                                for item_node in node2.childNodes:
                                    #print "---> ", item_node.nodeName
                                    if (item_node.nodeName == "title"):
                                        for text_node in item_node.childNodes:
                                            if (text_node.nodeType == node.TEXT_NODE):
                                                title += text_node.nodeValue
                                    elif (item_node.nodeName == "link"):
                                        for text_node in item_node.childNodes:
                                            if (text_node.nodeType == node.TEXT_NODE):
                                                link += text_node.nodeValue
                                    elif (item_node.nodeName == "description"):
                                        for text_node in item_node.childNodes:
                                            if (text_node.nodeType == node.TEXT_NODE):
                                                desc += text_node.nodeValue
                                if title:
                                    if link:
                                        self.render_text("   %d. " % count)
                                        self.link(title, "URL", link, tooltip=link)
                                    else:
                                        self.render_text("   %d. %s" % (count, title))
                                    self.append_text(" - ")
                                    self.append_text(self.first_line(desc))
                                    self.append_text("\n")
                                    count += 1
                                    yield True
            self.append_text("\n")
        self.append_text("", scroll_to="begin")

    def first_line(self, text):
        text = self.strip_html(text)
        text = decode_html(text)
        text = text.split("\n")[0]
        if len(text) > 30:
            text = text[:30] 
        return text + "..."

    def strip_html(self, text):
        text = text.replace("nbsp;", " ")
        retval = u""
        last_c = None
        state = "plain"
        for c in text:
            if c == "<":
                state = "skip"
            if state == "plain":
                if c in ["\t", " ", "\n"]:
                    if (c == last_c):
                        continue
                retval += c
                last_c = c
            if c == ">":
                state = "plain"
        return retval

    def decode_wiki(self, text):
        # final text
        text = text.replace("<BR>", "\n")
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        text = text.strip()
        ## Wiki text:
        ## Templates:
        pattern = '{{.*?}}'
        matches = re.findall(pattern, text)
        for match in matches:
            page = match[2:-2]
            oldtext = match
            if "|" in page:
                template, heading, body = page.split("|", 2)
                if template.lower() == "release":
                    newtext = "GRAMPS " + heading + " released.\n\n"
                else:
                    #newtext = "<B>%s</B>\n\n" % heading
                    newtext = ""
                text = text.replace(oldtext, newtext)
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
        return text

    def wiki(self, title):
        return (self.URL % title)

    def nice_title(self, title):
        return title.replace("_", " ")
        
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
         gramps="3.1.0",
         version="1.0.2",
         )
