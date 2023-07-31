# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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
from gramps.gen.plug._pluginreg import register, STABLE, GENERAL
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.2"

# ------------------------------------------------------------------------
#
# libcairo
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libcairodoc",
    name="Cairodoc lib",
    description=_("Provides a library for using Cairo to " "generate documents."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libcairodoc.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libgedcom
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libgedcom",
    name="GEDCOM library",
    description=_("Provides GEDCOM processing functionality"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libgedcom.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# librecurse
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="librecurse",
    name="Recursive lib",
    description=_("Provides recursive routines for reports"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="librecurse.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libgrampsxml
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libgrampsxml",
    name="Grampsxml lib",
    description=_("Provides common functionality for Gramps XML " "import/export."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libgrampsxml.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libholiday
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libholiday",
    name="holiday lib",
    description=_("Provides holiday information for different countries."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libholiday.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# llibhtmlbackend
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libhtmlbackend",
    name="htmlbackend lib",
    description=_("Manages a HTML file implementing DocBackend."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libhtmlbackend.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libhtmlconst
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libhtmlconst",
    name="htmlconst lib",
    description=_("Common constants for html files."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libhtmlconst.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libhtml
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libhtml",
    name="html lib",
    description=_("Manages an HTML DOM tree."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libhtml.py",
    authors=["Gerald Britton"],
    authors_email=["gerald.britton@gmail.com"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libmapservice
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libmapservice",
    name="mapservice lib",
    description=_("Provides base functionality for map services."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libmapservice.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libnarrate
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libnarrate",
    name="narration lib",
    description=_("Provides Textual Narration."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libnarrate.py",
    authors=["Brian Matherly"],
    authors_email=["brian@gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libodfbackend
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libodfbackend",
    name="odfbackend lib",
    description=_("Manages an ODF file implementing DocBackend."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libodfbackend.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libpersonview
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libpersonview",
    name="person list lib",
    description=_("Provides the Base needed for the List People views."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libpersonview.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libprogen
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libprogen",
    name="Pro-Gen lib",
    description=_("Provides common functionality for Pro-Gen import"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libprogen.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    # load_on_reg = True
)

# ------------------------------------------------------------------------
#
# libplaceview
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libplaceview",
    name="place list lib",
    description=_("Provides the Base needed for the List Place views."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libplaceview.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libsubstkeyword
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libsubstkeyword",
    name="Substitution Values",
    description=_("Provides variable substitution on display lines."),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libsubstkeyword.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

# ------------------------------------------------------------------------
#
# libtreebase
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    id="libtreebase",
    name="Graphical report lib",
    description=_(
        "Provides the base needed for the ancestor and " "descendant graphical reports."
    ),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="libtreebase.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)
