import sys
import os
import _winreg
from ctypes.util import find_library
import getopt
import string


#==== Set up logging system
# need to also set up a logger for when run as a module.

# change to set up a console logger in module global space.
# then add the file logger later once I know the path


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    datefmt='%H:%M',
                    filename= 'gtkcheck.log',
                    filemode='w')
#create a Handler for the console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#Set a simple format for console
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
#add the console handler to the root handler
log = logging.getLogger('CheckGtkApp')
log.addHandler(console)


NOT_FOUND_STR ='Not Found'
#small selection of DLL's to test
testdlls = ['libgdk-win32-2.0-0.dll', 'libglib-2.0-0.dll', 'libgobject-2.0-0.dll', 'libcairo-2.dll', ]

explain_exposed = '''    ***********************************************************
    * It seems that other installations are exposing GTK DLL's
    * to the operating system as they are in the environment
    * path variable BEFORE the runtime directory.
    * You should reorder the path variable to put your GTK
    * runtime path before these other installations on the path'''

explain_safe = '''    ***************************************************************
    * While there are other installations of GTK DLL's on the path,
    * it should be safe as they are on the path AFTER the runtime
    * directory. '''

def RunExeCommand( app, args ):
    cmd = app + ' ' + args
    #print("Running: ", cmd)
    stdin, stdout, stderr = os.popen3( cmd )
    output = string.strip(stdout.read())
    #print(output)
    err = stderr.read()
    if err:
        print(err)
    return output

def CheckGtkInReg():
    global gtkPathInRegistry, gtkVersionInRegistry, dllPathInRegistry, dllPathShort
    log.info( '\n==== Checking Registry for GTK =====' )
    try:
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GTK\\2.0') as key:
            gtkVersionInRegistry = _winreg.QueryValueEx(key, 'Version')[0]
            gtkPathInRegistry = _winreg.QueryValueEx(key, 'Path')[0]
            dllPathInRegistry = _winreg.QueryValueEx(key, 'DllPath')[0]
            log.info( '  Version   : %s'% gtkVersionInRegistry )
            log.info( '  Path      : %s'% gtkPathInRegistry )
            log.info( '  DllPath   : %s'% dllPathInRegistry )

    except WindowsError as e:
        log.info( '\n  GTK registry key not found in registry' )
        log.info( '''    ********************************************************************
    * This might not be an error, but means I don't know the directory to
    * your preferred GTK installation.
    *  - try passing in your GTK installation path.\n''' )
        log.info( '-' * 60 )
        log.info( usage )
        sys.exit(0)

def WorkOutShortDosPath():
    global dllPathShort
    log.info( '\n==== Use win32Api to query short path name for GTK =====' )
    try:
        import win32api
        dllPathShort =  win32api.GetShortPathName(dllPathInRegistry)
        log.info( '  DllPath8.3: %s' % dllPathShort )
    except ImportError:
        log.info( '  **Cant query short path name, Win32Api not installed' )
        log.info( '    install from http://python.net/crew/mhammond/win32/' )
        log.info( '    if you want this function to work' )

def FindLibsWithCtypes():    
    # use ctypes to check where windows finds it's DLL's
    log.info( '\n==== Use ctypes to find dlls ====' )
    other_paths = []
    for dll in testdlls:
        dllpathvalid = False
        cpath = find_library(dll)
        if cpath:
        #print(cpath)
            if cpath == os.path.join(dllPathInRegistry, dll) \
            or cpath == os.path.join(dllPathShort, dll):
                dllpathvalid = True

            if not dllpathvalid:
                pp = os.path.dirname(cpath)
                if pp not in other_paths:
                    other_paths.append(pp)
        else:
            log.info( "  ERROR:... ctypes failed to find %s" % dll)
    if other_paths:
        for pth in other_paths:
            log.info( "  ERROR: ctypes loaded some gtk dll's from %s" % pth )
    else:
        log.info( "  OK ... ctypes found dll's in %s" % os.path.dirname(cpath) )
        
def ScanDependencyFileForErrors(fname):
    fin = open(fname, 'r')
    lines = fin.readlines()
    fin.close()
    sysroot = os.environ["SystemRoot"]
    capture = False
    runtimedlls = {}
    for line in lines:
        if line.startswith("       Module"): # work out were paths end
            pthend_idx = line.find("File Time Stamp")
        acceptablePaths = [ dllPathShort.lower(), 
                            dllPathInRegistry.lower(),
                            os.path.join(sysroot, 'system32').lower()
                          ]
        if line.startswith('-----  ------------'):
            capture = True
        if capture and line.startswith('['):
            filename = line[5:pthend_idx].strip()
            dirname = os.path.dirname(filename).strip()
            parts = line[pthend_idx:].split()
            OK = False
            if dirname.startswith(os.path.join(sysroot, 'winsxs').lower()) \
            or dirname.startswith(os.path.join(sys.prefix, 'lib\site-packages\gtk-2.0').lower()):
                OK = True

            for pth in acceptablePaths:
                if dirname == pth.lower():
                    OK = True

            if 'MSVCR90.DLL' in filename:
                if parts[0] == 'Error':
                    runtimedlls[filename] = "Error dll not found"
                else:
                    runtimedlls[filename] = parts[16]

            if OK == False:
                if parts[0] == 'Error':
                    log.info( "    %s \tError dll not found" %( filename))
                else:
                    log.info( "    ERROR: %s \tVersion %s" %( filename, parts[16]))
    for rtdll in runtimedlls:
        if runtimedlls[rtdll].startswith("Error"):
            log.info( '\n    ERROR: MS runtime %s not found'%rtdll )
        else:
            log.info( '\n    MS runtime Version %s loaded from' % runtimedlls[rtdll] )
            log.info( "    %s" %rtdll )
    log.info( '') 

def CheckWithDependencyWalker():
    log.info( '\n==== Checking with Dependency Walker ====' )
    log.info( '      Please be patient takes some time' )
    exe = os.path.join(scriptpath, 'depends.exe')
    fout = os.path.join(scriptpath, 'depres.txt')
    f2check = [ 
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/gtk/_Gtk.pyd' ),
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/gobject/_GObject.pyd' ),
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/pangocairo.pyd' ),
                ]
    if os.path.isfile( exe ):
        for ftest in f2check:
            if os.path.isfile( ftest ):
                #delete the output file before running command
                try:
                    os.remove(fout)
                except WindowsError as e:
                    pass
                log.info( '  Testing file %s' % ftest )
                out = RunExeCommand(exe, '/c /f1 /ot "%s" "%s"' % (fout, ftest) )
                if os.path.isfile(fout):
                    ScanDependencyFileForErrors(fout)
            else:
                log.info( "  ERROR: file %d does not exist", ftest )
    else:
        log.info( '  Cannot check with dependency walker, not installed in local directory' )
        log.info( '  get dependency walker from http://www.dependencywalker.com/' )
        log.info( '  and unzip into this directory for it to work.' )

def CheckPathForOtherGtkInstalls():
    log.info( '\n====Checking environment path for other gtk installations====' )
    ePath = os.environ['path']
    dirs = ePath.split(';')
    gtkpth_idx = 9999
    other_paths = []
    explain_level = 0
    for i, d in enumerate(dirs):
        #print('==%s==' %d)
        if d == gtkPathInRegistry or d == dllPathInRegistry\
        or d == dllPathShort:
            gtkpth_idx = i
            continue
        for fname in testdlls:
            f = os.path.join(d, fname)
            if os.path.isfile( f ):
                #print('   Found Erronous gtk DLL %s' % f)
                if d not in other_paths:
                    other_paths.append(d)
                    if i < gtkpth_idx: # path appears BEFORE runtime path
                        log.info( '  ERROR: %s should not appear before runtime path' % d )
                        explain_level = 2
                    else:
                        log.info( '  FOUND: %s, Probably OK as appears AFTER runtime path' % d )
                        if explain_level <= 1:
                            explain_level = 1
    if gtkpth_idx == 9999:
        log.info( '\n  ERROR: Runtime directory not on enviroment path' )
        log.info( "         ** Runtime needs to be on path to load DLL's from\n" )
    if explain_level == 2:
        log.info( explain_exposed )
    elif explain_level == 1:
        log.info( explain_safe )
    if len(other_paths) == 0:
        log.info( '  No other gtk installatons found\n' )

# ==== report what python thinks it's using =====
MIN_PYTHON_VER   = (2,5,1)
UNTESTED_PYTHON_VER = (3,0,0)

MIN_GTK_VER      = (2,10,11)
UNTESTED_GTK_VER = (2,16,7)

MIN_PYGTK_VER    = (2,10,6)
UNTESTED_PYGTK_VER    = (2,12,2)

MIN_GOBJECT_VER  = (2,12,3)
UNTESTED_GOBJECT_VER  = (2,14,3)

MIN_CAIRO_VER    = (1,2,6)
UNTESTED_CAIRO_VER    = (1,4,13)

def PrintFailedImport(appl, minVersion, result):
    log.info( '--%s version %d.%d.%d or above.....\t %s' % (appl, minVersion ,result) )

def PrintVersionResult(appl, minVersion, actualVersion, untestedVersion):
    minStr = '%d.%d.%d' % minVersion
    actStr = '%d.%d.%d' % actualVersion
    if minVersion <= actualVersion < untestedVersion: 
        result =  '...OK'
    elif  actualVersion >= untestedVersion:
        result = '...UNTESTED VERSION'
    else:
        result = '...FAILED'
    log.info( '%s version %s or above.....\tfound %s %s' % (appl, minStr , actStr, result) )

def Import_pyGtkIntoPython():
    log.info( '\n==== Test import into python ====' )
    #py_str = 'found %d.%d.%d' %  sys.version_info[:3]
    PrintVersionResult('  Python ', MIN_PYTHON_VER, sys.version_info[:3], UNTESTED_PYTHON_VER)

    # Test the GTK version
    try:
        import gtk

        PrintVersionResult('  GTK+   ', MIN_GTK_VER, Gtk.gtk_version, UNTESTED_GTK_VER )

        #test the pyGTK version (which is in the gtk namespace)
        PrintVersionResult('  pyGTK  ', MIN_PYGTK_VER, Gtk.pygtk_version, UNTESTED_PYGTK_VER )

    except ImportError:
        PrintFailedImport('  GTK+   ', MIN_GTK_VER, NOT_FOUND_STR)
        PrintFailedImport('  pyGTK  ', MIN_PYGTK_VER, 'Cannot test, ...GTK+ missing')


    #test the gobject version
    try:
        import gobject
        PrintVersionResult('  gobject', MIN_GOBJECT_VER, GObject.pygobject_version, UNTESTED_GOBJECT_VER)

    except ImportError:
        PrintFailedImport('  gobject', MIN_GOBJECT_VER, NOT_FOUND_STR)


    #test the cairo version
    try:
        import cairo
        PrintVersionResult('  cairo  ', MIN_CAIRO_VER, cairo.version_info, UNTESTED_CAIRO_VER )

    except ImportError:
        PrintFailedImport('  cairo  ', MIN_CAIRO_VER, NOT_FOUND_STR)

    #test for glade
    log.info( '\n==== See if libglade installed ====')

    try:
        import Gtk.glade
        log.info( '  Glade   tesing import of libglade .......\tOK\n' )
    except ImportError as e:
        log.info( '  Glade   importError: %s\n' % e )

if __name__ == '__main__':
    usage = '''Check for common problems in GTK/pyGTK installation.
Usage:
    python %s [options] [gtkPath]

Arguments:
    gtkPath                    Path to your GTK installation directory (not the bin dir)

Options:
    None
    ''' %(os.path.basename(__file__) )

    gtkPath = None
    gtkPathInRegistry = NOT_FOUND_STR
    gtkVersionInRegistry = NOT_FOUND_STR
    dllPathInRegistry = NOT_FOUND_STR
    dllPathShort = 'NoShortPath'
    scriptpath = os.path.dirname(sys.argv[0])
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                  [])

        for o, a in opts:
            if o in ("-h", "--help"):
                log.info( usage )
                sys.exit(0)

        if len(args) > 1:
            raise getopt.GetoptError('\nERROR: Too many arguments')
        for arg in args:
            if os.path.isdir(arg):
                gtkPath = arg
            else:
                raise  getopt.GetoptError('\nERROR: Not a valid GTK path %s' % arg)

    except getopt.GetoptError as msg:
        log.info( msg )
        log.info( '\n %s' % usage )
        sys.exit(2)

    import platform
    winver = platform.win32_ver()
    if len(winver) == 4:
        log.info(   '''\n==== platform.win32_ver() reports ====
  Operating System: %s
  Version         : %s
  Service Pack    : %s
  OS type         : %s''' %  winver)
    else:
        os.info( winver )

    if gtkPath:
        gtkPathInRegistry = gtkPath
        dllPathInRegistry = os.path.join(gtkPath, 'bin')
        os.info( '  Using %s as GTK install path' % gtkPathInRegistry )
        os.info( '  Using %s as GTK dll path' % dllPathInRegistry )
    else:
        CheckGtkInReg()

    WorkOutShortDosPath()
    FindLibsWithCtypes()
    CheckPathForOtherGtkInstalls()
    Import_pyGtkIntoPython()

    CheckWithDependencyWalker()

