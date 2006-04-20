#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------
import RelLib

#-------------------------------------------------------------------------
#
# Collection of standard types for various kinds of objects
#
#-------------------------------------------------------------------------
# events = (
#     # Family events
#     (RelLib.Event.UNKNOWN    , "Unknown"),
#     (RelLib.Event.MARRIAGE   , "Marriage"),
#     (RelLib.Event.MARR_SETTL , "Marriage Settlement"),
#     (RelLib.Event.MARR_LIC   , "Marriage License"),
#     (RelLib.Event.MARR_CONTR , "Marriage Contract"),
#     (RelLib.Event.MARR_BANNS , "Marriage Banns"),
#     (RelLib.Event.ENGAGEMENT , "Engagement"),
#     (RelLib.Event.DIVORCE    , "Divorce"),
#     (RelLib.Event.DIV_FILING , "Divorce Filing"),
#     (RelLib.Event.ANNULMENT  , "Annulment"),
#     (RelLib.Event.MARR_ALT   , "Alternate Marriage"),
#     # Personal events
#     (RelLib.Event.UNKNOWN         , "Unknown"),
#     (RelLib.Event.ADOPT           , "Adopted"),
#     (RelLib.Event.BIRTH           , "Birth"),
#     (RelLib.Event.DEATH           , "Death"),
#     (RelLib.Event.ADULT_CHRISTEN  , "Adult Christening"),
#     (RelLib.Event.BAPTISM         , "Baptism"),
#     (RelLib.Event.BAR_MITZVAH     , "Bar Mitzvah"),
#     (RelLib.Event.BAS_MITZVAH     , "Bas Mitzvah"),
#     (RelLib.Event.BLESS           , "Blessing"),
#     (RelLib.Event.BURIAL          , "Burial"),
#     (RelLib.Event.CAUSE_DEATH     , "Cause Of Death"),
#     (RelLib.Event.CENSUS          , "Census"),
#     (RelLib.Event.CHRISTEN        , "Christening"),
#     (RelLib.Event.CONFIRMATION    , "Confirmation"),
#     (RelLib.Event.CREMATION       , "Cremation"),
#     (RelLib.Event.DEGREE          , "Degree"),
#     (RelLib.Event.DIV_FILING      , "Divorce Filing"),
#     (RelLib.Event.EDUCATION       , "Education"),
#     (RelLib.Event.ELECTED         , "Elected"),
#     (RelLib.Event.EMIGRATION      , "Emigration"),
#     (RelLib.Event.FIRST_COMMUN    , "First Communion"),
#     (RelLib.Event.IMMIGRATION     , "Immigration"),
#     (RelLib.Event.GRADUATION      , "Graduation"),
#     (RelLib.Event.MED_INFO        , "Medical Information"),
#     (RelLib.Event.MILITARY_SERV   , "Military Service"), 
#     (RelLib.Event.NATURALIZATION  , "Naturalization"),
#     (RelLib.Event.NOB_TITLE       , "Nobility Title"),
#     (RelLib.Event.NUM_MARRIAGES   , "Number of Marriages"),
#     (RelLib.Event.OCCUPATION      , "Occupation"),
#     (RelLib.Event.ORDINATION      , "Ordination"),
#     (RelLib.Event.PROBATE         , "Probate"),
#     (RelLib.Event.PROPERTY        , "Property"),
#     (RelLib.Event.RELIGION        , "Religion"),
#     (RelLib.Event.RESIDENCE       , "Residence"),
#     (RelLib.Event.RETIREMENT      , "Retirement"),
#     (RelLib.Event.WILL            , "Will"),
#     )

attributes = (
    (RelLib.Attribute.UNKNOWN     , "Unknown"),
    (RelLib.Attribute.CASTE       , "Caste"),
    (RelLib.Attribute.DESCRIPTION , "Description"),
    (RelLib.Attribute.ID          , "Identification Number"),
    (RelLib.Attribute.NATIONAL    , "National Origin"),
    (RelLib.Attribute.NUM_CHILD   , "Number of Children"),
    (RelLib.Attribute.SSN         , "Social Security Number"),
    )

## family_relations = (
##     (RelLib.Family.MARRIED     , "Married"),
##     (RelLib.Family.UNMARRIED   , "Unmarried"),
##     (RelLib.Family.CIVIL_UNION , "Civil Union"),
##     (RelLib.Family.UNKNOWN     , "Unknown"),
##     )

# name_types = (
#     (RelLib.NameType.UNKNOWN , "Unknown"),
#     (RelLib.NameType.AKA     , "Also Known As"),
#     (RelLib.NameType.BIRTH   , "Birth Name"),
#     (RelLib.NameType.MARRIED , "Married Name"),
#     )

## source_media_types = (
##     (RelLib.RepoRef.UNKNOWN    , "Unknown"),
##     (RelLib.RepoRef.AUDIO      , "Audio"),
##     (RelLib.RepoRef.BOOK       , "Book"),
##     (RelLib.RepoRef.CARD       , "Card"),
##     (RelLib.RepoRef.ELECTRONIC , "Electronic"),
##     (RelLib.RepoRef.FICHE      , "Fiche"),
##     (RelLib.RepoRef.FILM       , "Film"),
##     (RelLib.RepoRef.MAGAZINE   , "Magazine"),
##     (RelLib.RepoRef.MANUSCRIPT , "Manuscript"),
##     (RelLib.RepoRef.MAP        , "Map"),
##     (RelLib.RepoRef.NEWSPAPER  , "Newspaper"),
##     (RelLib.RepoRef.PHOTO      , "Photo"),
##     (RelLib.RepoRef.TOMBSTONE  , "Tombstone"),
##     (RelLib.RepoRef.VIDEO      , "Video"),
##     )

## event_roles = (
##     (RelLib.EventRef.UNKNOWN   , "Unknown"),
##     (RelLib.EventRef.PRIMARY   , "Primary"),
##     (RelLib.EventRef.CLERGY    , "Clergy"),
##     (RelLib.EventRef.CELEBRANT , "Celebrant"),
##     (RelLib.EventRef.AIDE      , "Aide"),
##     (RelLib.EventRef.BRIDE     , "Bride"),
##     (RelLib.EventRef.GROOM     , "Groom"),
##     (RelLib.EventRef.WITNESS   , "Witness"),
##     (RelLib.EventRef.FAMILY    , "Family"),
##     )

# repository_types = (
#     (RelLib.Repository.UNKNOWN    , "Unknown"),
#     (RelLib.Repository.LIBRARY    , "Library"),
#     (RelLib.Repository.CEMETERY   , "Cemetery"),
#     (RelLib.Repository.CHURCH     , "Church"),
#     (RelLib.Repository.ARCHIVE    , "Archive"),
#     (RelLib.Repository.ALBUM      , "Album"),
#     (RelLib.Repository.WEBSITE    , "Web site"),
#     (RelLib.Repository.BOOKSTORE  , "Bookstore"),
#     (RelLib.Repository.COLLECTION , "Collection"),
#     (RelLib.Repository.SAFE       , "Safe"),
#     )

## marker_types = (
##     (RelLib.PrimaryObject.MARKER_NONE     , ""),
##     (RelLib.PrimaryObject.MARKER_COMPLETE , "complete"),
##     (RelLib.PrimaryObject.MARKER_TODO     , "todo"),
##     )

# url_types = (
#     (RelLib.Url.UNKNOWN    , "Unknown"),
#     (RelLib.Url.EMAIL      , "Email"),
#     (RelLib.Url.WEB_HOME   , "Home"),
#     (RelLib.Url.WEB_SEARCH , "Search"),
#     (RelLib.Url.WEB_FTP    , "FTP"),
#     )

# mapping from the tuple collection to the appropriate CUSTOM integer
custom_types = {
#    events             : RelLib.Event.CUSTOM,
    attributes         : RelLib.Attribute.CUSTOM,
#    family_relations   : RelLib.Family.CUSTOM,
#    name_types         : RelLib.NameType.CUSTOM,
#    source_media_types : RelLib.RepoRef.CUSTOM,
#    event_roles        : RelLib.EventRef.CUSTOM,
#    repository_types   : RelLib.Repository.CUSTOM,
#    marker_types       : RelLib.PrimaryObject.MARKER_CUSTOM,
#    url_types          : RelLib.Url.CUSTOM,
    }

def str_for_xml(tuples,the_tuple):
    """
    This function checks the_tuple against the collection of tuples
    and returns the string to store in the XML file.
    """

    # use list comprehension to quickly find a match, if any
    match_list = [ item for item in tuples if item[0] == the_tuple[0] ]

    # If match_list is not empty, then we have got a match,
    # so we simply return the string of that standard item
    if match_list:
        return match_list[0][1]

    # empty match_list means there's nothing with that integer,
    # so we simply return the string from the_tuple
    else:
        return the_tuple[1]

def tuple_from_xml(tuples,the_str):
    """
    This function checks the_str against the collection of tuples
    and returns the tuple to use for the type internally.
    """

    # use list comprehension to quickly find a match, if any
    match_list = [ item for item in tuples if item[1] == the_str ]
    
    # If match_list is not empty, then we have got a match,
    # so we return the tuple made from the only item in the list.
    if match_list:
        return (match_list[0][0],'')

    # empty match_list means there's nothing with that string,
    # so we return the tuple of custom type and the original string
    else:
        return (custom_types[tuples],the_str)
