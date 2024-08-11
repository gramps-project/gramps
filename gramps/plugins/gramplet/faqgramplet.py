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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# Register Gramplet
#
# ------------------------------------------------------------------------
class FAQGramplet(Gramplet):
    def init(self):
        self.set_use_markup(True)
        self.clear_text()
        """
        The "wiki" HTTP "anchor type" is gramps-specific, and causes
        GuiGramplet's on_button_press method to invoke gui/display.py's
        display_help method, which prepends URL_WIKISTRING before it then
        calls gui/display.py's display_url method.  So no URL_WIKISTRING
        is needed in this code.
        """
        faq_dict = {
            "bold_start": "<b>",
            "bold_end": "</b>",
            "gramps_wiki_html_start": "<a wiki='",
            "gramps_manual_html_start": "<a wiki='" + URL_MANUAL_PAGE + "_-_",
            "gramps_FAQ_html_start": "<a wiki='" + URL_MANUAL_PAGE + "_-_FAQ",
            "html_middle": "'>",
            "html_end": "</a>",
        }
        self.render_text(
            _(
                "%(bold_start)s%(gramps_FAQ_html_start)s%(html_middle)s"
                "Frequently Asked Questions"
                "%(html_end)s%(bold_end)s"
                "\n(needs a connection to the internet)\n"
            )
            % faq_dict
        )

        self.render_text("\n<b>%s</b>\n\n" % _("Editing Spouses"))

        faq_dict.update({"faq_section": "#How_do_I_change_the_order_of_spouses.3F'>"})
        self.render_text(
            _(
                "  1. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do I change the order of spouses?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"faq_section": "#How_do_I_add_an_additional_spouse.3F'>"})
        self.render_text(
            _(
                "  2. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do I add an additional spouse?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"faq_section": "#How_do_I_remove_a_spouse.3F'>"})
        self.render_text(
            _(
                "  3. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do I remove a spouse?"
                "%(html_end)s\n"
            )
            % faq_dict
        )

        self.render_text("\n<b>%s</b>\n\n" % _("Backups and Updates"))

        faq_dict.update({"faq_section": "#How_do_I_keep_backups.3F'>"})
        self.render_text(
            _(
                "  4. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do I make backups safely?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"faq_section": "#How_do_I_upgrade_GRAMPS.3F'>"})
        self.render_text(
            _(
                "  5. %(gramps_FAQ_html_start)s%(faq_section)s"
                "Is it necessary to update Gramps "
                "every time an update is released?"
                "%(html_end)s\n"
            )
            % faq_dict
        )

        self.render_text("\n<b>%s</b>\n\n" % _("Data Entry"))

        faq_dict.update(
            {
                "section": "Entering_and_Editing_Data:_Detailed_-_part_1"
                "#Editing_Information_About_Relationships'>"
            }
        )
        self.render_text(
            _(
                "  6. %(gramps_manual_html_start)s%(section)s"
                "How should information about marriages be entered?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update(
            {
                "faq_section": "#What_is_the_difference_"
                "between_a_residence_and_an_address.3F'>"
            }
        )
        self.render_text(
            _(
                "  7. %(gramps_FAQ_html_start)s%(faq_section)s"
                "What's the difference between a residence and an address?"
                "%(html_end)s\n"
            )
            % faq_dict
        )

        self.render_text("\n<b>%s</b>\n\n" % _("Media Files"))

        faq_dict.update({"faq_section": "#How_do_you_add_photos_to_an_item.3F'>"})
        self.render_text(
            _(
                "  8. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do you add a photo of a person/source/event?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"faq_section": "#How_do_you_find_unused_media.3F'>"})
        self.render_text(
            _(
                "  9. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How do you find unused media objects?"
                "%(html_end)s\n"
            )
            % faq_dict
        )

        self.render_text("\n<b>%s</b>\n\n" % _("Miscellaneous"))

        faq_dict.update(
            {"faq_section": "#How_can_I_publish_web_sites_" "generated_by_GRAMPS.3F'>"}
        )
        self.render_text(
            _(
                " 10. %(gramps_FAQ_html_start)s%(faq_section)s"
                "How can I make a website with Gramps and my tree?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update(
            {
                "web_html_start": "<a href='http://sourceforge.net/mailarchive"
                "/message.php?msg_id=21487967'>"
            }
        )
        self.render_text(
            _(
                " 11. %(web_html_start)s"
                "How do I record one's occupation?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"faq_section": "#What_do_I_do_if_I_have_found_a_bug.3F'>"})
        self.render_text(
            _(
                " 12. %(gramps_FAQ_html_start)s%(faq_section)s"
                "What do I do if I have found a bug?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"section": "Portal:Using_GRAMPS'>"})
        self.render_text(
            _(
                " 13. %(gramps_wiki_html_start)s%(section)s"
                "Is there a manual for Gramps?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"section": "Category:Tutorials'>"})
        self.render_text(
            _(
                " 14. %(gramps_wiki_html_start)s%(section)s"
                "Are there tutorials available?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"section": "Category:How_do_I...'>"})
        self.render_text(
            _(
                " 15. %(gramps_wiki_html_start)s%(section)s"
                "How do I ...?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        faq_dict.update({"section": "How_you_can_help'>"})
        self.render_text(
            _(
                " 16. %(gramps_wiki_html_start)s%(section)s"
                "How can I help with Gramps?"
                "%(html_end)s\n"
            )
            % faq_dict
        )
        self.append_text("", scroll_to="begin")
