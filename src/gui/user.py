#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Brian G. Matherly
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
#

"""
The User class provides basic interaction with the user.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.user
from gui.utils import ProgressMeter
from QuestionDialog import WarningDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# User class
#
#-------------------------------------------------------------------------
class User(gen.user.User):
    """
    This class provides a means to interact with the user via GTK.
    It implements the interface in gen.user.User()
    """
    def __init__(self):
        self.progress = None
    
    def begin_progress(self, title, message, steps):
        """
        Start showing a progress indicator to the user.
        
        @param title: the title of the progress meter
        @type title: str
        @param message: the message associated with the progress meter
        @type message: str
        @param steps: the total number of steps for the progress meter. a value 
            of 0 indicates that the ending is unknown and the meter should just 
            show activity.
        @type steps: int
        @returns: none
        """
        self.progress = ProgressMeter(title)
        if steps > 0:
            self.progress.set_pass(message, steps, ProgressMeter.MODE_FRACTION)
        else:
            self.progress.set_pass(message, mode=ProgressMeter.MODE_ACTIVITY)
    
    def step_progress(self):
        """
        Advance the progress meter.
        """
        if self.progress:
            self.progress.step()
    
    def end_progress(self):
        """
        Stop showing the progress indicator to the user.
        """
        if self.progress:
            self.progress.close()
            self.progress = None
    
    def prompt(self, title, question):
        """
        Ask the user a question. The answer must be "yes" or "no". The user will
        be forced to answer the question before proceeding.
        
        @param title: the title of the question
        @type title: str
        @param question: the question
        @type question: str
        @returns: the user's answer to the question
        @rtype: bool
        """
        return False
    
    def warn(self, title, warning):
        """
        Warn the user.
        
        @param title: the title of the warning
        @type title: str
        @param warning: the warning
        @type warning: str
        @returns: none
        """
        WarningDialog(title, warning)
    
    def notify_error(self, title, error):
        """
        Notify the user of an error.
        
        @param title: the title of the error
        @type title: str
        @param error: the error message
        @type error: str
        @returns: none
        """
        ErrorDialog(title, warning)
