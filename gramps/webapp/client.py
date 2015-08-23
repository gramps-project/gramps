import urllib2
import urllib

import logging
LOG = logging.getLogger(".web")

PATH_TO_LOGIN = "login/"

def login(base_address, username=None, password=None):
    # fetch the login page in order to get the csrf token
    cookieHandler = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(urllib2.HTTPSHandler(), cookieHandler)
    urllib2.install_opener(opener)
    login_url = base_address + PATH_TO_LOGIN
    LOG.info("login_url: " + login_url)
    login_page = opener.open(login_url)
    # attempt to get the csrf token from the cookie jar
    csrf_cookie = None
    for cookie in cookieHandler.cookiejar:
        if cookie.name == 'csrftoken':
             csrf_cookie = cookie
             break
    if not cookie:
        raise IOError("No csrf cookie found")
    LOG.info( "found csrf cookie: " + str(csrf_cookie))
    LOG.info( "csrf_token = %s" % csrf_cookie.value)
    # login using the usr, pwd, and csrf token
    login_data = urllib.urlencode(dict(
        username=username, password=password,
        csrfmiddlewaretoken=csrf_cookie.value))
    LOG.info("login_data: %s" % login_data)
    LOG.info("login_url: %s" % login_url)
    req = urllib2.Request(login_url, login_data)
    req.add_header('Referer', login_url)
    response = urllib2.urlopen(req)
    # <--- 403: FORBIDDEN here
    LOG.info('response url:\n' + str(response.geturl()) + '\n')
    LOG.info('response info:\n' + str(response.info()) + '\n')
    # should redirect to the welcome page here, if back at log in - refused
    url = response.geturl()
    LOG.info("url:", url)
    LOG.info("login_url:", login_url)
    if url == login_url:
        return None
    LOG.info('\t%s is logged in' % username)
    # save the cookies/opener for further actions
    return opener
