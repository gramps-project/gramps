# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012      Douglas S. Blank <doug.blank@gmail.com>
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

from urllib.request import (Request, urlopen, HTTPCookieProcessor,
                            build_opener, install_opener)
from urllib.parse import urlencode

class Connection(object):
    """
    >>> conn = Connection()
    >>> response = conn.login("http://blankfamily.us/login/", "username", "password")
    """
    def login(self, login_url, username, password):
        cookies = HTTPCookieProcessor()
        opener = build_opener(cookies)
        install_opener(opener)
        opener.open(login_url)
        try:
            self.token = [x.value for x in cookies.cookiejar if x.name == 'csrftoken'][0]
        except IndexError:
            return Exception("no csrftoken")
        params = dict(username=username,
                      password=password,
                      next="/",
                      csrfmiddlewaretoken=self.token,
                      )
        login_data = urlencode(params)
        request = Request(login_url, login_data)
        response = urlopen(request)
        if response.geturl() == login_url:
            raise Exception("Invalid password")
        return response

