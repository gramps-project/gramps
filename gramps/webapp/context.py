# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012         Douglas S. Blank <doug.blank@gmail.com>
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
# $Id: $
#

def messages(request):
    messages = {}
    if 'message' in request.session:
        message_type = request.session.get('message_type', 'error')
        messages = {'message': request.session['message'],
                    'message_type': message_type}
        del request.session['message']
        if 'message_type' in request.session:
            del request.session['message_type']
    return messages
