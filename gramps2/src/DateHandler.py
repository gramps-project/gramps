import DateParser
import DateDisplay
import os

try:
    import gconf
except ImportError:
    import gnome.gconf
    gconf = gnome.gconf

client = gconf.client_get_default()
client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)

_lang = os.environ.get('LANG','C')
    

_lang_to_parser = {
    'C'       : DateParser.DateParser,
    'en.US'   : DateParser.DateParser,
    }

_lang_to_display = {
    'C'       : DateDisplay.DateDisplay,
    'en.US'   : DateDisplay.DateDisplay,
    }

def create_parser():
    try:
        return _lang_to_parser[_lang]()
    except:
        return DateParser.DateParser()

def create_display():
    val = client.get_int("/apps/gramps/preferences/date-format")
    try:
        return _lang_to_display[_lang](val)
    except:
        return DateDisplay.DateDisplay(3)

def get_date_formats():
    try:
        return _lang_to_display[_lang].formats
    except:
        print "not found"
        return DateDisplay.DateDisplay.formats

def set_format(val):
    try:
        _lang_to_display[_lang].display_format = val
    except:
        print "not found"
        pass

def get_format():
    try:
        return _lang_to_display[_lang].display_format
    except:
        print "not found"
        return 0
