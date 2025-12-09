#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Manages the FamilySearch session.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import requests
import certifi
import threading
import socket
import time


# -------------------------------------------------------------------------
#
# GNOME python modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# Exceptions
#
# -------------------------------------------------------------------------
class FSException(Exception):
    pass


class FSPermission(Exception):
    pass


# -------------------------------------------------------------------------
#
# Listener class
#
# -------------------------------------------------------------------------
class Listener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.result = {}

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", 57938))
            s.listen(5)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                response = str(data)
                response = response[response.find("?") + 1 :]
                response = response[: response.find(" ")]
                for part in response.split("&"):
                    key, value = part.split("=")
                    self.result[key] = value.replace("+", " ")
                if "error" in self.result:
                    msg = "Access denied! User declined consent.\n"
                else:
                    msg = "Success! You can now return to Gramps.\n"

                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send("Content-Length: {:d}\n".format(len(msg)).encode("utf-8"))
                conn.send(b"Content-Type: text/plain\n\n")
                conn.send(msg.encode("utf-8"))


# -------------------------------------------------------------------------
#
# Session class
#
# -------------------------------------------------------------------------
class Session(requests.Session):
    def __init__(self, server: str, app_key: str, redirect: str):
        super().__init__()
        self.verify = certifi.where()
        self.app_key = app_key
        self.redirect = redirect
        self.listener = Listener()
        if server == 0:  # beta
            self.fs_url = "https://beta.familysearch.org/"
            self.ident_url = "https://identbeta.familysearch.org/"
            self.api_url = "https://apibeta.familysearch.org/"
        else:
            self.fs_url = "https://www.familysearch.org/"
            self.ident_url = "https://ident.familysearch.org/"
            self.api_url = "https://api.familysearch.org/"
        self.access_token = None

    def login(self, username: str, password: str) -> None:
        """
        Login to FamilySearch.
        """
        self.get(self.fs_url + "auth/familysearch/login")
        xsrf_token = self.cookies.get("XSRF-TOKEN")

        payload = {
            "_csrf": xsrf_token,
            "username": username,
            "password": password,
        }
        response = self.post(
            self.ident_url + "login",
            data=payload,
        )

        data = response.json()
        if data and data.get("loginError"):
            raise FSException(data["loginError"])

    def authorize(self, username: str) -> str:
        """
        Retrieve an authorization code.
        """
        self.listener.start()

        url = self.ident_url + "cis-web/oauth2/v3/authorization"
        payload = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect,
            "response_type": "code",
            "scope": "openid",
            "username": username,
        }
        headers = {"accept": "text/html"}
        response = self.get(url, headers=headers, params=payload)

        if "realm_permission" in response.url:
            raise FSPermission(response.url)

        auth_code = ""
        try:
            auth_code = response.url.split("=")[1]
        except IndexError:
            raise FSException("Authorization error")

        return auth_code

    def listen(self) -> str:
        """
        Listen for a response from the redirect uri after user has granted
        permission.
        """
        while self.listener.is_alive():
            time.sleep(0.1)
            while Gtk.events_pending():
                Gtk.main_iteration()

        if "error_description" in self.listener.result:
            raise FSException(self.listener.result["error_description"])

        return self.listener.result.get("code", "")

    def get_token(self, auth_code: str) -> None:
        """
        Retrieve an access code from the authorization code.
        """
        url = self.ident_url + "cis-web/oauth2/v3/token"
        payload = {
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect,
            "client_id": self.app_key,
            "code": auth_code,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }
        response = self.post(url, data=payload, headers=headers)

        data = response.json()
        if data and data.get("access_token"):
            self.access_token = data["access_token"]
        else:
            raise FSException("Authorization error")

    def get(self, url, **kwargs):
        """
        An enhanced requests `get` method for convenience.
        """
        if not url.startswith("http"):
            url = self.api_url + url
            headers = kwargs.setdefault("headers", {})
            headers.setdefault("authorization", "Bearer " + self.access_token)
            headers.setdefault("accept", "application/x-fs-v1+json")
        return super().get(url, **kwargs)

    def get_current_person(self) -> str:
        """
        Return the JSON representing the current person.
        """
        response = self.get("platform/tree/current-person")
        return response.text
