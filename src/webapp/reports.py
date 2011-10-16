# imports for import/export:

import DbState
from cli.grampscli import CLIManager
from gen.plug import BasePluginManager
import os

# Example for running a report:
# ------------------------------
# from cli.plug import run_report
# from django.conf import settings
# import webapp.settings as default_settings
# try:
#     settings.configure(default_settings)
# except:
#     pass
# import dbdjango
# db = dbdjango.DbDjango()
# run_report(db, "ancestor_report", off="txt", of="ar.txt", pid="I0363")

def import_file(db, filename, callback):
    """
    Import a file (such as a GEDCOM file) into the given db.

    >>> import_file(DbDjango(), "/home/user/Untitled_1.ged", lambda a: a)
    """
    dbstate = DbState.DbState()
    climanager = CLIManager(dbstate, False) # do not load db_loader
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    # (filename, (exception-type, exception, traceback), pdata)
                    etype, exception, traceback = error_tuple
                    print "ERROR:", name, exception
                return False
            import_function = getattr(mod, pdata.import_function)
            db.prepare_import()
            import_function(db, filename, callback)
            db.commit_import()
            return True
    return False

def download(url, filename=None):
    import urllib2
    import shutil
    import urlparse
    def getFilename(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info().split(';')))
            if 'filename' in cd:
                fname = cd['filename'].strip("\"'")
                if fname: return fname
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])
    r = urllib2.urlopen(urllib2.Request(url))
    success = None
    try:
        filename = filename or "/tmp/%s" % getFilename(url,r)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r,f)
        success = filename
    finally:
        r.close()
    return success

def export_file(db, filename, callback):
    """
    Export the db to a file (such as a GEDCOM file).

    >>> export_file(DbDjango(), "/home/user/Untitled_1.ged", lambda a: a)
    """
    dbstate = DbState.DbState()
    climanager = CLIManager(dbstate, False) # do not load db_loader
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    export_list = pmgr.get_reg_exporters()
    for pdata in export_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    etype, exception, traceback = error_tuple
                    print "ERROR:", name, exception
                return False
            export_function = getattr(mod, pdata.export_function)
            export_function(db, filename, callback)
            return True
    return False

