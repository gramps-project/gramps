# Copyright (C) 2003 Jesper Zedlitz
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

"Export/Partition"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
import posixpath

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import RelLib
import GrampsCfg

from QuestionDialog import ErrorDialog
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade
from gnome.ui import *
import WriteXML

personSeen = []
familySeen = []
database_for_unlinked_persons = RelLib.GrampsDB()
prefix = "/tmp/test"

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def work_on_person( db, person ):
   global personSeen
   
   if (len(person.getFamilyList()) + len(person.getParentList())) > 0:
     database = db
   else:
     database = database_for_unlinked_persons
   
   if( database.getPersonMap().has_key( person.getId() ) ):
      return
   
   database.addPersonNoMap( person, person.getId() )
   personSeen.append(person)
   
   for source_ref in person.getPrimaryName().getSourceRefList():
      work_on_sourceref( database, source_ref)
   
   for name in person.getAlternateNames():
      for source_ref in name.getSourceRefList():
         work_on_sourceref( database, source_ref)

   work_on_event( database, person.getBirth() )
   work_on_event( database, person.getDeath() )
   for event in person.getEventList():
      work_on_event(database, event)
		    
   # recursion
   for fam in person.getFamilyList():
     work_on_family( database, fam )
	  
   for fam in person.getParentList():
     work_on_family( database, fam[0] )
       
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def work_on_family( database, family ):
   global familySeen
   if database.getFamilyMap().has_key( family.getId() ):
      return
      
   database.getFamilyMap()[family.getId()] = family 
   familySeen.append(family)
   
   work_on_event( database, family.getMarriage() )
   for event in family.getEventList():
      work_on_event(database, event)

   
   # recursion
   father = family.getFather()
   if( father != None ):
     work_on_person( database, father )
	 
   mother = family.getMother()
   if( mother != None ):
     work_on_person( database, mother )
	 
   for person in family.getChildList():
      work_on_person( database, person )

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def work_on_sourceref( database, source_ref ):
   if source_ref == None:
      return
      
   source = source_ref.getBase()
   if source == None:
      return
   
   if database.getSourceMap().has_key(source.getId()):
      return
      
   database.addSourceNoMap( source, source.getId() );


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def work_on_event( database, event ):
   if event == None:
      return
      
   for source_ref in event.getSourceRefList():
      work_on_sourceref( database, source_ref)
      
   work_on_place( database, event.getPlace() )


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def work_on_place( database, place ):
   if place == None:
      return
      
   if place in database.getPlaces():
      return
   database.addPlaceNoMap(place, place.getId())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def report(db, person):
    global personSeen
    global prefix
    global database_for_unlinked_persons
    
    text = "=== Partitions ===\n"
    count = 0
    for p in db.getPersonMap().values():
       if not p in personSeen:
          database = RelLib.GrampsDB()
          work_on_person( database, p )
	  
	  person_len = len(database.getPersonKeys())
	  if person_len > 0:
             g = WriteXML.XmlWriter(database,None,0,0)
             g.write(prefix+str(count)+".xml")
	     text += "partition "+prefix+str(count)+".xml written ( "+str(person_len)+" persons)\n"
	     count += 1

    g = WriteXML.XmlWriter(database_for_unlinked_persons,None,0,0)
    g.write(prefix+".xml")
    text += "partition "+prefix+".xml written ( "+str(len(database_for_unlinked_persons.getPersonKeys()))+" persons)\n"

    base = os.path.dirname(__file__)
    glade_file = "%s/summary.glade" % base

    topDialog = gtk.glade.XML(glade_file,"summary","gramps")
    topDialog.signal_autoconnect({
        "destroy_passed_object" : Utils.destroy_passed_object,
    })

    top = topDialog.get_widget("summary")
    textwindow = topDialog.get_widget("textwindow")
    textwindow.get_buffer().set_text(text)
    top.show()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Partitions"),
    status=(_("Alpha")),
    category=_("Export"),
    description=_("This program partitions individuals in a database into disjoint partitions.\n"+
                  "A partition is composed of people related by one or more multiple relations.\n"+
		  "There should be no known relationship between people in different partitions.")
    )

