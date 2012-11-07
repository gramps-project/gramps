import sys
if sys.version_info[0] < 3:
    from urllib2 import (urlopen, Request, HTTPCookieProcessor,
                build_opener, install_opener)
    from urllib import urlencode
else:
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

