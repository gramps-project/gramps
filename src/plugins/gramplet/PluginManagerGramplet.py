# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Douglas S. Blank <doug.blank@gmail.com>
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
import urllib

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from gen.ggettext import sgettext as _

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class PluginManagerGramplet(Gramplet):
    """
    Headlines News Gramplet reads the Headline News every hour.
    """
    URL = "http://www.gramps-project.org/wiki/index.php?title=Plugins&action=raw"
    def init(self):
        """
        Initializes the Gramplet
        """
        self.set_use_markup(True)

    def main(self):
        """
        The main code of the Gramplet. (iterator)
        """
        self.set_text(_("Reading") + " '%s'..." % self.URL)
        yield True
        fp = urllib.urlopen(self.URL)
        state = "read"
        headings = []
        rows = []
        row = []
        for line in fp.readlines():
            yield True
            if line.startswith("|-") or line.startswith("|}"):
                if row != []:
                    rows.append(row)
                state = "row"
                row = []
            elif state == "row":
                if line.startswith("!"):
                    headings.append(line[1:].strip())
                elif line.startswith("|"):
                    row.append(line[1:].strip())
            else:
                state = "read"
        types = {}
        for row in rows:
            types[row[1]] = 1
        self.set_text("")
        # name, type, ver, desc, use, rating, contact, download
        for type in types:
            self.render_text("<b>%s Plugins</b>\n" % _(type))
            row_count = 1
            for row in rows:
                if type == row[1]:
                    if "|" in row[0][2:-2]:
                        link, text = row[0][2:-2].split("|", 1)
                        self.append_text("%d) " % row_count)
                        self.link(text, "WIKI", link)
                        self.append_text(" (%s)\n" % row[2]) # version
                        self.append_text("   %s\n" % row[3])
                        self.append_text("   [")
                        if row[-1].startswith("[["):
                            url, text = row[-1][2:-2].split("|", 1)
                            self.link("Download", "WIKI", url)
                        elif row[-1].startswith("["):
                            url, text = row[-1][1:-1].split(" ", 1)
                            self.link("Download", "URL", url)
                        else:
                            self.append_text("Download unavailable")
                        self.append_text("]\n\n")
                        row_count += 1
                    else:
                        text = row[0][2:-2]
                        self.append_text("%d) " % row_count)
                        self.link(text, "WIKI", text)
                        self.append_text(" (%s)\n" % row[2]) # version
                        self.append_text("   %s\n" % row[3])
                        self.append_text("   [")
                        if row[-1].startswith("[["):
                            url, text = row[-1][2:-2].split("|", 1)
                            self.link("Download", "WIKI", url)
                        elif row[-1].startswith("["):
                            url, text = row[-1][1:-1].split(" ", 1)
                            self.link("Download", "URL", url)
                        else:
                            self.append_text("Download unavailable")
                        self.append_text("]\n\n")
                        row_count += 1

            self.append_text("\n", scroll_to="begin")
