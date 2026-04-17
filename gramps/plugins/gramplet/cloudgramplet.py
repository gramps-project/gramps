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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------

from abc import abstractmethod

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# ------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------

_YIELD_INTERVAL = 350


# ------------------------------------------------------------------------
#
# Local functions
#
# ------------------------------------------------------------------------
def make_tag_size(rank, total_rank, mins=8, maxs=20):
    # return font sizes mins to maxs
    diff = maxs - mins
    position = diff - (diff * (rank / (total_rank + 1)))
    return int(position) + mins


# ------------------------------------------------------------------------
#
# CloudGramplet class
#
# ------------------------------------------------------------------------
class CloudGramplet(Gramplet):
    """A gramplet class that displays a list of values, with each value's size determined by how many times it appears in the database. 
    They are displayed as clickable or non-clickable links depending on the information you want to display about them.
    """

    def init(self):
        self.set_tooltip(_("Double-click surname for details"))
        self.top_size = 150  # will be overwritten in load
        self.min_font = 8
        self.max_font = 20
        self.set_text(_("No Family Tree loaded."))
        self.value_name = "default_value_name"
        self.item_name = "default_item_name"
        self.preference_no_value = ""
        self.link_type = "None"

    def set_value_name(self,value_name):
        """What the cloud displays. For a name cloud, `value_name` is "name" """
        self.value_name = _(value_name)

    def set_item_name(self,item_name):
        """What the cloud analyzes. For a keyword cloud, the value of "value_name" could be "person." """
        self.item_name = _(item_name)

    def set_preference_no_value(self,preference_no_value):
        """When there is a default configuration to display if no values are provided"""
        self.preference_no_value = preference_no_value

    def set_link_type(self,link_type):
        """The type of link that appears when a user double-clicks on a value"""
        self.link_type = link_type
        

    @abstractmethod
    def db_changed(self):
        """Connect the cloud with db. 
            See the exemple in surnamecloudgramplet.py 
        """
        pass
        
    @abstractmethod
    def get_items(self) -> list:
        """How to access data in the cloud. Must return an iterator of type (value, related_data).
            See the example in surnamecloudgramplet.py
        """
        pass

    def on_load(self):
        if len(self.gui.data) == 3:
            self.top_size = int(self.gui.data[0])
            self.min_font = int(self.gui.data[1])
            self.max_font = int(self.gui.data[2])

    def save_update_options(self, widget=None):
        self.top_size = int(self.get_option(_("Number of " + self.value_name)).get_value())
        self.min_font = int(self.get_option(_("Min font size")).get_value())
        self.max_font = int(self.get_option(_("Max font size")).get_value())
        self.gui.data = [self.top_size, self.min_font, self.max_font]
        self.update()

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True

        yield_counter = 0

        values_counts = {}
        values_linked_data = {}
        total_item = 0

        # Initialise dict variables and total 
        for value, linked_data in self.get_items():
            if value not in values_counts:

                values_linked_data[value] = linked_data
                values_counts[value] = 1
            else : 
                values_counts[value] +=1

            total_item += 1
            yield_counter += 1
            if not yield_counter % _YIELD_INTERVAL:
                yield True
        yield_counter = 0


        # count order : [(value,count),...]
        sorted_values = sorted(list(values_counts.items()), key= (lambda k : k[1]), reverse=True)
        total_unique = len(sorted_values)

        ## limit counts to only include those that we can display (<= self.top_size)
        acc = 0
        selected_values = []
        for value, count in sorted_values:
            if acc + count  > self.top_size:
                break
            acc += count
            selected_values.append((value,count))
            if not yield_counter % _YIELD_INTERVAL:
                    yield True
        yield_counter = 0
        
        # Define rank of each value (start at 0)
        values_rank = {}
        curr_rank = 0

        if selected_values != []:
            curr_count = selected_values[0][1] # first max value
            for value, count in selected_values:
                if curr_count > count:
                    curr_count = count
                    curr_rank += 1
                values_rank[value] = curr_rank  
                if not yield_counter % _YIELD_INTERVAL:
                    yield True
            yield_counter = 0

        # alpha order 
        selected_values.sort(key= lambda k : k[0])
        
        # Display
        mins = self.min_font
        maxs = self.max_font
        
        showing = 0
        self.set_text("")
        for value, count in selected_values:
            if len(value) == 0:
                if self.preference_no_value != "":
                    text = config.get(self.preference_no_value)
                else:
                    text = _(f"[Missing %s]") % self.value_name
            else:
                text = value
            size = make_tag_size(values_rank[value],curr_rank , mins=mins, maxs=maxs)
            self.link(
                text,
                self.link_type,
                values_linked_data[value],
                size,
                "%s, %d%% (%d)"
                % (text, int((float(count) / total_item) * 100), count),
            )
            self.append_text(" ")
            showing += 1
        self.append_text(
            ("\n\n" + _("Total unique %s") + ": %d\n") % (self.value_name, total_unique)
        )
        self.append_text((_("Total %s showing") + ": %d\n") % (self.value_name,showing))
        self.append_text((_("Total %s") + ": %d") % (self.item_name,total_item), "begin")

    def build_options(self):
        from gramps.gen.plug.menu import NumberOption

        self.top_size_option = NumberOption(
            _("Number of %s") % self.value_name, self.top_size, 1, 150
        )
        self.add_option(self.top_size_option)
        self.min_option = NumberOption(_("Min font size"), self.min_font, 1, 50)
        self.add_option(self.min_option)
        self.max_option = NumberOption(_("Max font size"), self.max_font, 1, 50)
        self.add_option(self.max_option)

    def save_options(self):
        self.top_size = int(self.get_option(_("Number of %s") % self.value_name).get_value())
        self.min_font = int(self.get_option(_("Min font size")).get_value())
        self.max_font = int(self.get_option(_("Max font size")).get_value())
