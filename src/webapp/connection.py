import urllib
import urllib2

class Connection(object):
    """
    >>> conn = Connection()
    >>> response = conn.login("http://blankfamily.us/login/", "username", "password")
    """
    def login(self, login_url, username, password):
        cookies = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(cookies)
        urllib2.install_opener(opener)
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
        login_data = urllib.urlencode(params)
        request = urllib2.Request(login_url, login_data)
        response = urllib2.urlopen(request)
        if response.geturl() == login_url:
            raise Exception("Invalid password")
        return response

