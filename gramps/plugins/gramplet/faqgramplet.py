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
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_PAGE

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
class FAQGramplet(Gramplet):
    def init(self):
        self.set_use_markup(True)
        self.clear_text()
        WIKI = URL_MANUAL_PAGE
        self.render_text(_("<b><a wiki='%s_-_FAQ'>Frequently Asked Questions</a></b>\n(needs a connection to the internet)\n") % WIKI)
        self.render_text("\n<b>%s</b>\n\n" % _("Editing Spouses"))

        self.render_text(_("  1. <a wiki='%s_-_FAQ#How_do_I_change_the_order_of_spouses.3F'>How do I change the order of spouses?</a>\n") % WIKI)
        self.render_text(_("  2. <a wiki='%s_-_FAQ#How_do_I_add_an_additional_spouse.3F'>How do I add an additional spouse?</a>\n") % WIKI)
        self.render_text(_("  3. <a wiki='%s_-_FAQ#How_do_I_remove_a_spouse.3F'>How do I remove a spouse?</a>\n") % WIKI)

        self.render_text("\n<b>%s</b>\n\n" % _("Backups and Updates"))

        self.render_text(_("  4. <a wiki='%s_-_FAQ#How_do_I_keep_backups.3F'>How do I make backups safely?</a>\n") % WIKI)
        self.render_text(_("  5. <a wiki='%s_-_FAQ#How_do_I_upgrade_GRAMPS.3F'>Is it necessary to update Gramps every time an update is released?</a>\n") % WIKI)

        self.render_text("\n<b>%s</b>\n\n" % _("Data Entry"))

        self.render_text(_("  6. <a wiki='%s_-_Entering_and_Editing_Data:_Detailed_-_part_1#Editing_Information_About_Relationships'>How should information about marriages be entered?</a>\n") % WIKI)
        self.render_text(_("  7. <a wiki='%s_-_FAQ#What_is_the_difference_between_a_residence_and_an_address.3F'>What's the difference between a residence and an address?</a>\n") % WIKI)

        self.render_text("\n<b>%s</b>\n\n" % _("Media Files"))

        self.render_text(_("  8. <a wiki='%s_-_FAQ#How_do_you_add_photos_to_an_item.3F'>How do you add a photo of a person/source/event?</a>\n") % WIKI) 
        self.render_text(_("  9. <a wiki='%s_-_FAQ#How_do_you_find_unused_media_objects.3F'>How do you find unused media objects?</a>\n") % WIKI) 

        self.render_text("\n<b>%s</b>\n\n" % _("Miscellaneous"))

        self.render_text(_(" 10. <a wiki='%s_-_FAQ#How_can_I_publish_web_sites_generated_by_GRAMPS.3F'>How can I make a website with Gramps and my tree?</a>\n") % WIKI)
        self.render_text(_(" 11. <a href='http://sourceforge.net/mailarchive/message.php?msg_id=21487967'>How do I record one's occupation?</a>\n"))
        self.render_text(_(" 12. <a wiki='%s_-_FAQ#What_do_I_do_if_I_have_found_a_bug.3F'>What do I do if I have found a bug?</a>\n") % WIKI)
        self.render_text(_(" 13. <a wiki='Portal:Using_GRAMPS'>Is there a manual for Gramps?</a>\n"))
        self.render_text(_(" 14. <a wiki='Category:Tutorials'>Are there tutorials available?</a>\n"))
        self.render_text(_(" 15. <a wiki='Category:How_do_I...'>How do I ...?</a>\n"))
        self.render_text(_(" 16. <a wiki='How_you_can_help'>How can I help with Gramps?</a>\n"))
        self.append_text("", scroll_to='begin')

    def post_init(self):
        self.disconnect("active-changed")
