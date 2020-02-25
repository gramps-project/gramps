#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Douglas Blank <doug.blank@gmail.com>
# Copyright (C) 2011 Rob G. Healey <robhealey1@gmail.com>
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
#

#------------------------------------------------
#    python modules
#------------------------------------------------
import os
import re
from gramps.gen.const import VERSION_DIR, IMAGE_DIR, DATA_DIR, USER_CSS
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

def make_css_dict(tup):
    """
    Basically, make a named tuple.
    """
    return {
        "id": tup[0],
        "user"        : tup[1],
        "translation" : tup[2],
        "filename"    : tup[3],
        "navigation"  : tup[4],
        "images"      : tup[5],
        "javascript"  : tup[6],
        }

def load_on_reg(dbstate, uistate, plugin):
    """
    Runs when plugin is registered.
    """
    from functools import partial
    path_css = partial(os.path.join, DATA_DIR, "css")
    path_img = partial(os.path.join, IMAGE_DIR, "webstuff")
    path_img_48x48 = partial(os.path.join, IMAGE_DIR, "hicolor/48x48/actions")
    CSS_FILES = [

        # id, user selectable?, translated_name, option name, fullpath,
        # navigation target name, images, javascript
        # "default" is used as default

        # default style sheet in the options
        # Basic Ash style sheet
        ["Basic-Ash", 1, _("Basic-Ash"),
         path_css('Web_Basic-Ash.css'), None, [], []],

        # Basic Blue style sheet with navigation menus
        ["Basic-Blue", 1, _("Basic-Blue"),
         path_css('Web_Basic-Blue.css'), None, [], []],

        # Basic Cypress style sheet
        ["Basic-Cypress", 1, _("Basic-Cypress"),
         path_css('Web_Basic-Cypress.css'), None, [], []],

        # basic Lilac style sheet
        ["Basic-Lilac", 1, _("Basic-Lilac"),
         path_css('Web_Basic-Lilac.css'), None, [], []],

        # basic Peach style sheet
        ["Basic-Peach", 1, _("Basic-Peach"),
         path_css('Web_Basic-Peach.css'), None, [], []],

        # basic Spruce style sheet
        ["Basic-Spruce", 1, _("Basic-Spruce"),
         path_css('Web_Basic-Spruce.css'), None, [], []],

        # Mainz style sheet with its images
        ["Mainz", 1, _("Mainz"),
         path_css('Web_Mainz.css'), None,
         [path_img("Web_Mainz_Bkgd.png"),
          path_img("Web_Mainz_Header.png"),
          path_img("Web_Mainz_Mid.png"),
          path_img("Web_Mainz_MidLight.png")], []],

        # Nebraska style sheet
        ["Nebraska", 1, _("Nebraska"),
         path_css('Web_Nebraska.css'), None, [], []],

        # Visually Impaired style sheet with its navigation menus
        ["Visually Impaired", 1, _("Visually Impaired"),
         path_css('Web_Visually.css'), "narrative-menus.css", [], []],

        # ancestor tree style sheet and its images
        ["ancestortree", 0, "ancestortree",
         path_css("ancestortree.css"), None,
         [path_img("Web_Gender_Female.png"),
          path_img("Web_Gender_Male.png")], []],

        # media reference regions style sheet
        ["behaviour", 0, "Behaviour",
         path_css('behaviour.css'), None, [], []],

        # NarrativeMap stylesheet/ image for NarrativeWeb place maps
        ["NarrativeMaps", 0, "",
         path_css("narrative-maps.css"), None, [], []],

        # default printer style sheet
        ["Print-Default", 0, "Print-Default",
         path_css('Web_Print-Default.css'), None, [], []],

        # Horizontal Navigation Menus Style Sheet
        ["Horizontal-Menus", 0, "Horizontal Menus",
         path_css('Web_Horizontal-Menus.css'), None, [], []],

        # Vertical Navigation Menus Style Sheet
        ["Vertical-Menus", 0, "Vertical Menus",
         path_css('Web_Vertical-Menus.css'), None, [], []],

        # WebKit/ Html5/ CSS3 Fade Navigation Menus Style Sheet
        ["Fade-Menus", 0, "Fade In/ Out Menus",
         path_css('Web_Fade-Menus.css'), None, [], []],

        # WebKit/ Html5/ CSS3 Animated Drop Down Style Sheet
        ["Animated DropDown", 0, "Animated DropDown",
         path_css("Web_Citations-Animated.css"), None, [],
         "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"],

        # Source Page Citations Referents Outline Style sheet...
        ["Outline", 0, "Outline Citations",
         path_css("Web_Citations-Outline.css"), None, [], []],

        # WebKit/ Html5/ CSS3 Drop Down Navigation Menus Style Sheet
        ["DropDown-Menus", 0, "Drop Down Menus",
         path_css("Web_DropDown-Menus.css"), None, [], []],

        # no style sheet option
        ["No style sheet", 1, _("No style sheet"), [], None, [], []],

        # Document image
        ["Document", 0, "Document",
         os.path.join(IMAGE_DIR, "document.png"), None, [], []],

        # blank
        ["Blank", 0, "Blank",
         path_img("blank.gif"), None, [], []],

        # all other images for use in NarrativeWeb
        ['All Images', 0, 'All Images', None, None,
         [path_img("blank.gif"),
          os.path.join(IMAGE_DIR, "document.png")], []],

        # Gramps Fav icon #2
        ["favicon2", 0, "FavIcon2",
         path_img("favicon2.ico"), None, [], []],

        # copyright image
        ['Copyright', 0, 'Copyright',
         path_img("somerights20.gif"), None, [], []],

        # marker icon for openstreetmap
        ['marker', 0, 'marker',
         path_img_48x48("gramps-geo-mainmap.png"), None, [], []],
        ]
    # If we add css user files, we must restart gramps to use them.
    if os.path.exists(USER_CSS):
        list_files = os.listdir(USER_CSS)
        for cssfile in list_files:
            if cssfile.endswith(".css"):
                css_f = cssfile.replace('.css', '')
                CSS_FILES.append(["UsEr_" + css_f, 1, css_f,
                                  os.path.join(USER_CSS, cssfile), None,
                                  looking_for_urls_in_user_css(cssfile),
                                  []])
    return CSS_FILES

def looking_for_urls_in_user_css(css_file):
    """
    At each time we find the tag url, we get the content and add it
    to the images list. This content must be local.
    """
    images = []
    cssfile = os.path.join(USER_CSS, css_file)
    with open(cssfile) as css:
        data = css.readlines()
        for line in data:
            if "url" in line:
                url = re.match(r".*url\((.*)\)", line)
                if url.group(1)[0:3] != "http":
                    img = url.group(1).replace("../images/", "")
                    img = os.path.join(USER_CSS, img)
                    if img not in images:
                        images.append('%s' % img)
    return images


def process_list(data):
    """
    Gather all of the web resources together, and allow override files
    if available.
    """
    retval = []
    for row in data:
        file = row[3]
        if file:
            dummy_path, filename = os.path.split(file)
            # is there a override file in the VERSION_DIR/webstuff?
            # eg, ~/.gramps/gramps34/webstuff/Web_Nebraska.css
            # if so, replace this one:
            override = os.path.join(VERSION_DIR, "webstuff", filename)
            if os.path.exists(override):
                row[3] = override
        retval.append(row)
    # {"Mainz": {"id": "Mainz", "user":1, ...}}
    retdict = {}
    for css in retval:
        if css[0] in retdict:
            retdict[css[0]]["images"].append(css[5])
        else:
            retdict[css[0]] = make_css_dict(css)
    return retdict
