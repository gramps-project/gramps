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
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from gen.ggettext import sgettext as _

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
class FAQGramplet(Gramplet):
    def init(self):
        self.set_use_markup(True)
        self.clear_text()
        self.render_text(_("<a wiki='Gramps_3.2_Wiki_Manual_-_FAQ'>Frequently Asked Questions</a> (need connection to internet)\n\n"))
        self.render_text(_("  1. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#How_do_I_change_the_order_of_spouses.3F'>How do I change the order of spouses?</a>\n"))
        self.render_text(_("  2. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#How_do_I_upgrade_GRAMPS.3F'>Is it necessary to update Gramps every time an update is released?</a>\n"))
        self.render_text(_("  3. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#How_do_I_keep_backups.3F'>How do I make backups safely?</a>\n"))
        self.render_text(_("  4. <a wiki='Gramps_3.2_Wiki_Manual_-_Entering_and_Editing_Data:_Detailed_-_part_1#Editing_Information_About_Relationships'>How should information about marriages be entered?</a>\n"))
        self.render_text(_("  5. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#What_is_the_difference_between_a_residence_and_an_address.3F'>What's the difference between a residence and an address?</a>\n"))
        self.render_text(_("  6. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#How_can_I_publish_web_sites_generated_by_GRAMPS.3F'>How can I make a website with Gramps and my tree?</a>\n"))
        self.render_text(_("  7. <a href='http://old.nabble.com/German-translation-of-%22occupation%22-ts21786114.html#a21786114'>How do I record one's occupation?</a>\n"))
        self.render_text(_("  8. <a wiki='Gramps_3.2_Wiki_Manual_-_FAQ#What_do_I_do_if_I_have_found_a_bug.3F'>What do I do if I have found a bug?</a>\n"))
        self.render_text(_("  9. <a wiki='Portal:Using_GRAMPS'>Is there a manual for Gramps?</a>\n"))
        self.render_text(_(" 10. <a wiki='Category:Tutorials'>Are there tutorials available?</a>\n"))
        self.render_text(_(" 11. <a wiki='Category:How_do_I...'>How do I ...?</a>\n"))
        self.render_text(_(" 12. <a wiki='How_you_can_help'>How can I help with Gramps?</a>\n"))

    def post_init(self):
        self.disconnect("active-changed")
