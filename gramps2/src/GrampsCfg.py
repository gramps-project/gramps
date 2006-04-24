#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sets
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Config
import RelLib
import const
import DateHandler
import GrampsDisplay
import QuestionDialog

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------
INDEX         = "i"
OBJECT        = "o"
DATA          = "d"

_surname_styles = [
    _("Father's surname"),
    _("None"),
    _("Combination of mother's and father's surname"),
    _("Icelandic style"),
    ]

panellist = [
    (_("Display"),
     [( _("General"), 3),
      ( _("Dates"), 4),
      ( _("Toolbar and Statusbar"), 2)]),
    (_("Database"),
     [( _("General"), 1),
      ( _("GRAMPS IDs"), 6),
      ( _("Researcher Information"), 5)]),
    ]


# Not exactly gconf keys, but the functions directly dependent on them

def set_calendar_date_format():
    format_list = DateHandler.get_date_formats()
    DateHandler.set_format(Config.get_date_format(format_list))

def _update_calendar_date_format(active,dlist):
    Config.save_date_format(active,dlist)
    DateHandler.set_format(active)

#-------------------------------------------------------------------------
#
# make_path - 
#   Creates a directory if it does not already exist. Assumes that the
#   parent directory already exits
#
#-------------------------------------------------------------------------
def make_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def loadConfig():
    """
    Load preferences on startup. Not much to do, since all the prefs
    are in gconf and can be retrieved any time. 
    """
    make_path(const.home_dir)
    make_path(os.path.join(const.home_dir,"filters"))
    make_path(os.path.join(const.home_dir,"plugins"))
    make_path(os.path.join(const.home_dir,"templates"))
    make_path(os.path.join(const.home_dir,"thumb"))
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_researcher():
    n  = Config.get(Config.RESEARCHER_NAME)
    a  = Config.get(Config.RESEARCHER_ADDR)
    c  = Config.get(Config.RESEARCHER_CITY)
    s  = Config.get(Config.RESEARCHER_STATE)
    ct = Config.get(Config.RESEARCHER_COUNTRY)
    p  = Config.get(Config.RESEARCHER_POSTAL)
    ph = Config.get(Config.RESEARCHER_PHONE)
    e  = Config.get(Config.RESEARCHER_EMAIL)

    owner = RelLib.Researcher()
    owner.set(n,a,c,s,ct,p,ph,e)
    return owner
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GrampsPreferences:
    def __init__(self,db):
        self.built = 0
        self.db = db
        self.top = gtk.glade.XML(const.gladeFile,"preferences","gramps")

        self.top.get_widget('button6').connect('clicked',self.on_close_clicked)
        self.top.get_widget('button7').connect('clicked',self.help_clicked)
        
        self.window = self.top.get_widget("preferences")
        self.window.connect('delete_event',self.on_close_clicked)
        self.tree = self.top.get_widget("tree")
        self.image = self.top.get_widget('image')
        self.image.set_from_file(os.path.join(const.image_dir,'splash.jpg'))
        
        self.store = gtk.TreeStore(gobject.TYPE_STRING)
        self.selection = self.tree.get_selection()
        self.selection.connect('changed',self.select)
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.tree.set_model(self.store)
        self.panel = self.top.get_widget("panel")

        self.imap = {}
        self.build_tree()
        self.build()
        self.built = 1
        self.window.show()

    def build_tree(self):
        prev = None
        ilist = []
        for (name,lst) in panellist:
            node = self.store.insert_after(None, prev)
            self.store.set(node,0,name)
            next = None
            for (subname,tab) in lst:
                next = self.store.insert_after(node,next)
                ilist.append((next,tab))
                self.store.set(next,0,subname)
        for next,tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab
        
    def build(self):

        auto = self.top.get_widget("autoload")
        auto.set_active(Config.get(Config.AUTOLOAD))
        auto.connect('toggled',
                lambda obj: Config.set(Config.AUTOLOAD,obj.get_active()))

        spell = self.top.get_widget("spellcheck")
        spell.set_active(Config.get(Config.SPELLCHECK))
        spell.connect('toggled',
                lambda obj: Config.set(Config.SPELLCHECK))

        lds = self.top.get_widget("uselds")
        lds.set_active(Config.get(Config.USE_LDS))
        lds.connect('toggled',
                lambda obj: Config.set(Config.USE_LDS,obj.get_active()))

        self.ipr = self.top.get_widget("iprefix")
        self.ipr.set_text(Config.get(Config.IPREFIX))
        self.opr = self.top.get_widget("oprefix")
        self.opr.set_text(Config.get(Config.OPREFIX))
        self.fpr = self.top.get_widget("fprefix")
        self.fpr.set_text(Config.get(Config.FPREFIX))
        self.spr = self.top.get_widget("sprefix")
        self.spr.set_text(Config.get(Config.SPREFIX))
        self.ppr = self.top.get_widget("pprefix")
        self.ppr.set_text(Config.get(Config.PPREFIX))

        sb2 = self.top.get_widget("stat2")
        sb3 = self.top.get_widget("stat3")
        if Config.get(Config.STATUSBAR) == 0 or Config.get(Config.STATUSBAR) == 1:
            sb2.set_active(1)
        else:
            sb3.set_active(1)
        sb2.connect('toggled',
                lambda obj: Config.set(Config.STATUSBAR,(2-obj.get_active())))

        toolbarmenu = self.top.get_widget("tooloptmenu")
        toolbarmenu.set_active(Config.get(Config.TOOLBAR)+1)
        toolbarmenu.connect('changed',
                lambda obj: Config.set(Config.TOOLBAR,obj.get_active()-1))

        pvbutton = self.top.get_widget('pvbutton')
        fvbutton = self.top.get_widget('fvbutton')
        if Config.get(Config.DEFAULT_VIEW) == 0:
            pvbutton.set_active(1)
        else:
            fvbutton.set_active(1)
        fvbutton.connect('toggled',
                lambda obj: Config.set(Config.DEFAULT_VIEW,(obj.get_active())))

        usetips = self.top.get_widget('usetips')
        usetips.set_active(Config.get(Config.USE_TIPS))
        usetips.connect('toggled',
                lambda obj: Config.set(Config.USE_TIPS,obj.get_active()))

        lastnamegen_obj = self.top.get_widget("lastnamegen")
        cell = gtk.CellRendererText()
        lastnamegen_obj.pack_start(cell,True)
        lastnamegen_obj.add_attribute(cell,'text',0)

        store = gtk.ListStore(str)
        for name in _surname_styles:
            store.append(row=[name])
        lastnamegen_obj.set_model(store)
        guess = Config.get(Config.SURNAME_GUESSING)
        if guess not in _surname_styles:
            guess = Config.default_value[Config.SURNAME_GUESSING]
            
        lastnamegen_obj.set_active(guess)
        lastnamegen_obj.connect("changed", 
                lambda obj: 
                Config.set(Config.SURNAME_GUESSING,obj.get_active())
                )

        date_option = self.top.get_widget("date_format")
        dlist = DateHandler.get_date_formats()
        date_option.pack_start(cell,True)
        date_option.add_attribute(cell,'text',0)

        store = gtk.ListStore(str)
        for item in dlist:
            store.append(row=[item])

        date_option.set_model(store)
        try:
            # Technically, a selected format might be out of range
            # for this locale's format list.
            date_option.set_active(Config.get_date_format(dlist))
        except:
            date_option.set_active(0)

        date_option.connect("changed",
                lambda obj: 
                _update_calendar_date_format(obj.get_active(),dlist)
                )

        resname = self.top.get_widget("resname")
        resname.set_text(Config.get(Config.RESEARCHER_NAME))
        resname.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_NAME,obj.get_text()))
        resaddr = self.top.get_widget("resaddr")
        resaddr.set_text(Config.get(Config.RESEARCHER_ADDR))
        resaddr.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_ADDR,obj.get_text()))
        rescity = self.top.get_widget("rescity")
        rescity.set_text(Config.get(Config.RESEARCHER_CITY))
        rescity.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_CITY,obj.get_text()))
        resstate = self.top.get_widget("resstate")
        resstate.set_text(Config.get(Config.RESEARCHER_STATE))
        resstate.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_STATE,obj.get_text()))
        rescountry = self.top.get_widget("rescountry")
        rescountry.set_text(Config.get(Config.RESEARCHER_COUNTRY))
        rescountry.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_COUNTRY,obj.get_text()))
        respostal = self.top.get_widget("respostal")
        respostal.set_text(Config.get(Config.RESEARCHER_POSTAL))
        respostal.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_POSTAL,obj.get_text()))
        resphone = self.top.get_widget("resphone")
        resphone.set_text(Config.get(Config.RESEARCHER_PHONE))
        resphone.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_PHONE,obj.get_text()))
        resemail = self.top.get_widget("resemail")
        resemail.set_text(Config.get(Config.RESEARCHER_EMAIL))
        resemail.connect('changed',
                    lambda obj: Config.set(Config.RESEARCHER_EMAIL,obj.get_text()))
                    
    def save_prefix(self):
        """ Validate the GRAMPS ID definitions to be usable"""
        ip = self.ipr.get_text()
        op = self.opr.get_text()
        fp = self.fpr.get_text()
        sp = self.spr.get_text()
        pp = self.ppr.get_text()
        
        # Do validation to the GRAMPS-ID format strings
        invalid_chars = sets.Set("# \t\n\r")
        prefixes = [ip,op,fp,sp,pp]
        testnums = [1,234,567890]
        testresult = {} # used to test that IDs for different objects will be different
        formaterror = False # true if formatstring is invalid
        incompatible = False    # true if ID string is possibly not GEDCOM compatible
        for p in prefixes:
            if invalid_chars & sets.Set(p):
                incompatible = True
            for n in testnums:
                try:
                    testresult[p % n] = 1
                except:
                    formaterror = True
        
        idexampletext = _('Example for valid IDs are:\n'+
                        'I%d which will be displayed as I123 or\n'+
                        'S%06d which will be displayed as S000123.')
        if formaterror:
            QuestionDialog.ErrorDialog( _("Invalid GRAMPS ID prefix"),
                _("The GRAMPS ID prefix is invalid.\n")+
                idexampletext,
                self.window)
            return False
        elif incompatible:
            QuestionDialog.OkDialog( _("Incompatible GRAMPS ID prefix"),
                _("The GRAMPS ID prefix is in an unusual format and may"+
                " cause problems when exporting the database to GEDCOM format.\n")+
                idexampletext,
                self.window)
        elif len(testresult) != len(prefixes)*len(testnums):
            QuestionDialog.ErrorDialog( _("Unsuited GRAMPS ID prefix"),
                _("The GRAMPS ID prefix is unsuited because it does not"+
                " distinguish between different objects.\n")+
                idexampletext,
                self.window)
            return False

        Config.set(Config.IPREFIX,ip)
        Config.set(Config.OPREFIX,op)
        Config.set(Config.FPREFIX,fp)
        Config.set(Config.SPREFIX,sp)
        Config.set(Config.PPREFIX,pp)
        return True
        
    def select(self,obj):
        store,node = self.selection.get_selected()
        if node:
            path = store.get_path(node)
        if node and self.imap.has_key(path):
            self.panel.set_current_page(self.imap[path])
        
    def help_clicked(self,obj):
        GrampsDisplay.help('gramps-prefs')

    def on_close_clicked(self,obj=None,dummy=None):
        if not self.save_prefix():
            return False
        self.window.destroy()
    
#-------------------------------------------------------------------------
#
# Create the property box, and set the elements off the current values
#
#-------------------------------------------------------------------------
def display_preferences_box(db):
    GrampsPreferences(db)
