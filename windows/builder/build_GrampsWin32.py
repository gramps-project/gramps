#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2006       Brian Matherly
# Copyright (C) 2008       Stephen George
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
# $Id: $

import os, glob, sys, shutil
import string
import os.path as path
import subprocess

CONFIGURE_IN = 'configure.in'
CONST_PY_IN = 'src/const.py.in'
TRANSLATE_FOLDER = 'po'

EXTRA_FILES = [ 'COPYING', 'NEWS', 'FAQ', 'AUTHORS']

FULL_COLON_SUBST = "~"

#min required version of NSIS
MIN_NSIS_VERSION = (2,42)

#tools used during build
MAKENSIS_exe = None
SVN_exe = None
po_errs = []
po_oks = []

import gobject


#==== Set up logging system
# need to also set up a logger for when run as a module.

# change to set up a console logger in module global space.
# then add the file logger later once I know the path
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                    datefmt='%H:%M',
                    filename= 'build.log', #path.join(out_dir,'build.log'),
                    filemode='w')
#create a Handler for the console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#Set a simle format for console
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
#add the console handler to the root handler
log = logging.getLogger('BuildApp')
log.addHandler(console)


class buildbase(GObject.GObject):
    __gsignals__={
        "build_progresstext"        :  (GObject.SignalFlags.RUN_LAST, None, [GObject.TYPE_STRING]),
        "build_progressfraction"    :  (GObject.SignalFlags.RUN_LAST, None, [GObject.TYPE_FLOAT]),
    }

    def __init(self):
        GObject.GObject.__init__(self)
        self.gramps_version = 'VERSION-UNKNOWN'
        self.bTarball = bTarball
        self.build_root = '.'  # the directory were the build source is located
        self.out_dir = '.'     # the directory to output final installer to, and the expand source to
        self.repository_path = '.' #where the source comes from, either SVN root or a tarball
        self.bBuildInstaller = True
        self.tarbase3 = '.'
        
    def getbuild_src(self):
        return os.path.join(self.build_root, 'src')

    build_src = property(getbuild_src)

    def isGrampsRoot(self, root ):
        log.debug( 'isGrampsRoot: %s' % root )
        if path.isfile(path.join(root, CONFIGURE_IN)):
            if path.isfile(path.join(root, CONST_PY_IN)):
                if path.isdir(path.join(root, TRANSLATE_FOLDER)):
                    return True
        return False

    def getSVNRevision(self, dir ):
        log.debug('========== getSVNRevision(%s)' % dir)
        cmd = 'svnversion -n %s' % dir
        log.debug( "Running: %s" % cmd )
        
        proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        (out, err) = proc.communicate()
        output = string.strip(out)
        log.debug( output )
        if err:
            for line in err.split('\n'):
                log.error(line)
            if not stdout:
                output = '-UNKNOWN'
        return 'SVN' + output

    def exportSVN(self, svn_dir, destdir):
        '''
        svn export PATH1 PATH2
        exports a clean directory tree from the working copy specified by PATH1 into PATH2.
        All local changes will be preserved, but files not under version control will not be copied.

        destdir cannot exist, script will clean up dir first
        '''
        log.debug('========== exportSVN(%s, %s)' % (svn_dir, destdir) )
#        cmd = '"%s" export %s %s' % (SVN_exe ,svn_dir, destdir)
        cmd = [SVN_exe, 'export' ,svn_dir, destdir] #'"%s" export %s %s' % (SVN_exe ,svn_dir, destdir)
        
        log.info( "Running: %s" % cmd)
        
        proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        (out, err) = proc.communicate()
        output = string.strip(out)
        log.info( output )
        if err:
            log.error(err)

    def copyExtraFilesToBuildDir(self, source_path):
        '''
        A few extra files not in src directory needs to be copied to the build dir
        '''
        log.debug('========== copyExtraFilesToBuildDir(%s)' % (source_path))
        for file in EXTRA_FILES:
            outfile = file
            if file == 'NEWS':
                #Jump through hoops tomake sure the end of line charactors are windows format (wont work on linux!!)
                outfile = 'NEWS.TXT' #Lets add .TXT suffix to filename so installer knows to call notepad 
                fnews = open(os.path.join(source_path,file), 'r')
                newslines = fnews.readlines()
                newsout = open(os.path.join(self.build_src,outfile), 'w')
                newsout.writelines(newslines)
                newsout.close()
                fnews.close()
            else:
                shutil.copy(os.path.join(source_path,file), os.path.join(self.build_src,outfile) )

    def compileInstallScript(self):
        '''
        Now we got a build directory, lets create the installation program
        '''
        log.debug('========== compileInstallScript()')
        log.info('Compiling NullSoft install script .... be patient')
        # calc path to gramps2.nsi
        # need to ensure __file__ has full path, under linux it does not.
        thisfilepath = os.path.abspath(__file__)
        pth = os.path.relpath(os.path.dirname( thisfilepath ), os.getcwd())
        pth2nsis_script = os.path.join(pth, 'gramps2.nsi') 

        #should tests be more along lines of os.name which returns 'posix', 'nt', 'mac', 'os2', 'ce', 'java', 'riscos'
        if sys.platform == 'win32':
#            cmd = '"%s" /V3 %s' % (MAKENSIS_exe, pth2nsis_script)
            cmd = [MAKENSIS_exe, '/V3',pth2nsis_script]
        elif sys.platform == 'linux2':
            #assumption makensis is installed and on the path
            cmd = '%s -V3 %s' % (MAKENSIS_exe, pth2nsis_script)
        
        log.info( "Running: %s" % cmd)
        # Need to define the following enviroment variables for NSIS script
        os.environ['GRAMPS_VER'] = self.gramps_version
        os.environ['GRAMPS_BUILD_DIR'] = os.path.abspath(self.build_src)
        os.environ['GRAMPS_OUT_DIR'] = os.path.abspath(self.out_dir)
        
        proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        (out, err) = proc.communicate()
        output = string.strip(out)
        log.info( output )
        if err:
            log.error(err)

    def getVersionFromConfigureIn(self, repository_path):
        log.debug('========== read_config_in(%s)' % repository_path)
        fin = open('%s/configure.in' % repository_path, 'r')
        conf_lines = fin.readlines()
        fin.close()
        return self.getVersionFromLines(conf_lines)
        
    def getVersionFromLines(self, conf_lines):
        log.debug('========== getVersionFromLines()')
        for line in conf_lines:
            if 'AC_INIT(gramps' in line:
                junk, ver, junk2 = line.split(',')
            elif line[:7] == 'RELEASE':
                junk,release = line.split('=')
                if 'SVN$' in release:#not a release version
                    release = self.getSVNRevision( repository_path )
                elif not self.bTarball:  # This is aRelease, lets make sure svn working copy is prestine
#                elif not bTarball:  # This is aRelease, lets make sure svn working copy is prestine
                    test_num = getSVNRevision( repository_path )
                    if test_num.endswith('M'): # in test_num:   #endsWith
                        log.warning('*==========================================================')
                        log.warning('*     Building a Release from modified SVN Working Copy    ')
                        log.warning('*  ===>  Creating %s-%s from %s-%s  <==' % (ver.strip(), release.strip(),ver.strip(), test_num.strip()) )
                        log.warning('*==========================================================')
        gversion = '%s-%s' % (ver.strip(), release.strip())
        gversion = gversion.replace(":", FULL_COLON_SUBST) # if it's a mixed version, then need to replace the : with something else
        log.info( 'GrampsVersion: %s' % gversion )
        return gversion

    def processPO( self ):
        log.debug('========== processPO( )')
        po_dir = os.path.join(self.build_root, "po")
        mo_dir = os.path.join(self.build_src, "lang")
        if not os.path.exists(mo_dir):
            os.makedirs(mo_dir)
        #TODO: find a better way to handle  different platforms
        if sys.platform == 'win32':
            po_files = glob.glob(po_dir + "\*.po")
            # no longer using python msgfmt as it doesn't handle plurals (april 2010)
            # msgfmtCmd = path.normpath(path.join(sys.prefix, "Tools/i18n/msgfmt.py") )
            
            # GetText Win 32 obtained from http://gnuwin32.sourceforge.net/packages/gettext.htm
            # ....\gettext\bin\msgfmt.exe needs to be on the path
            msgfmtCmd = 'msgfmt.exe'
            #print 'msgfmtCmd = %s' % msgfmtCmd
        elif sys.platform == 'linux2':
            po_files = glob.glob(po_dir + "/*.po")
            msgfmtCmd = "%s/bin/msgfmt" % sys.prefix
        else:
            po_files = [] #empty list
            msgfmtCmd = "UNKNOWN_PLATFORM"
        log.debug( msgfmtCmd )
        #if not os.path.exists(msgfmtCmd):
        #    log.error( "msgfmt not found - unable to generate mo files")
        #    return
        log.info( "Generating mo files" )
        global po_errs, po_oks 
        po_total = len(po_files)
        po_count = 0 
        for po_file in po_files:
            po_count = po_count + 1
            #This will be interesting
            self.emit("build_progresstext", 'compiling %s' % po_file)
            self.emit("build_progressfraction", po_count/po_total)

            lan = os.path.basename(po_file).replace( ".po", "" )
            lan_path = os.path.join(mo_dir,lan,"LC_MESSAGES")
            if not os.path.exists(lan_path):
                os.makedirs(lan_path)
            mo_file = os.path.join(lan_path,"gramps.mo")
            log.info( mo_file )

            cmd = [msgfmtCmd, '--statistics','-o', mo_file, po_file]
            log.debug( cmd )

            proc = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            (out, err) = proc.communicate()
            output = string.strip(out)
            log.info( output )
            # log.debug( output ) Nothing coming out here, statistics come out stderr ??
            if err:
                log.info(err) # statistics comming out stderr
                po_errs.append(lan)
            else:
                po_oks.append(lan)

    def generateConstPy(self ):
        log.debug('========== generate_const.py()')
        fin = open(os.path.join(self.build_src,'const.py.in'), 'r')
        in_lines = fin.readlines()
        fin.close()
        fout = open(os.path.join(self.build_src,'const.py'), 'w')
        for line in in_lines:
            if '@VERSIONSTRING@' in line: #VERSION        = "@VERSIONSTRING@"
                corrline = line.replace('@VERSIONSTRING@', self.gramps_version.replace(FULL_COLON_SUBST,":") )
                fout.write(corrline)
                #fout.write('VERSION        = "%s"\n'% self.gramps_version.replace(FULL_COLON_SUBST,":"))

            #elif '@prefix@' in line: #PREFIXDIR = "@prefix@"
            #       what to do? , doesnt seem to matter on windows

            #elif '@sysconfdir@' in line: #SYSCONFDIR = "@sysconfdir@"
            #       what to do? , doesnt seem to matter on windows

            else:
                fout.write(line)
        fout.close()

    def cleanBuildDir(self):
        log.debug( '========== cleanBuildDir()' )
        log.info( 'Cleaning build and output directories' )
        if sys.platform == 'win32': #both platforms emit different exceptions for the same operation, map the exception here
            MY_EXCEPTION = WindowsError
        elif sys.platform == 'linux2':
            MY_EXCEPTION = OSError
        if os.path.exists(self.build_root):
            try:
                log.info('removing directory: %s' % self.build_root )
                shutil.rmtree(self.build_root)
            except MY_EXCEPTION, e:
                log.error( e )

        for file in ['gramps-%s.exe'%self.gramps_version ]: #, 'build.log']:
            fname = os.path.join(self.out_dir, file)
            if os.path.isfile(fname):
                try:
                    log.info('removing file:      %s' % fname )
                    os.remove(fname)
                except MY_EXCEPTION, e:
                    log.error( e )

    def getNSISVersionNumber(self):
        #Check version of NSIS, to ensure NSIS is compatible with script features 
          # >"c:\Program Files\NSIS\makensis.exe" /version
          # v2.42
        cmd = '"%s" -VERSION' % (MAKENSIS_exe)
        log.debug(cmd)
        
        proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        (out, err) = proc.communicate()
        output = string.strip(out)
        log.info( output )
        if err:
            log.error(err)
            if sys.platform == 'win32': #'not recognized' in err:
                minor =0
                major =0
                return (major, minor)
            
        #parse the output to get version number into tuple
        ver =  output[1:].split('.') 
        major = int(ver[0])
        try:
            minor = int(ver[1]) 
        except ValueError, e:
            m = ver[1]
            minor = int(m[:2])        
        return (major, minor)

    def checkForBuildTools(self):
        global MAKENSIS_exe, SVN_exe
        log.debug( '========== checkForBuildTools()' )
        if sys.platform == 'win32':
            import _winreg as winreg
            # Find NSIS on system
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\NSIS') as key:
                    nsispath = winreg.QueryValue(key, '')
                    makensisexe = path.join( nsispath, 'makensis.exe')
                    if path.isfile( makensisexe ):
                        MAKENSIS_exe = makensisexe
            except WindowsError, e:
                log.warning('NSIS not found, in registory')
                log.warning('..Testing if makensis is on the path')
                MAKENSIS_exe = 'makensis'
                #cmd = os.path.join(nsis_dir, MAKENSIS_exe)
                
                cmd = '%s /VERSION' % MAKENSIS_exe
                proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                (out, err) = proc.communicate()
                output = string.strip(out)
                log.info( output )
                if err:
                    log.error(err)
                    log.error('....makensis.exe not found on path')
                    sys.exit(0)
                #else:
                #    log.info("makensis version %s" % output)

            # Find msgfmt on system
            cmd = os.path.join(msg_dir, 'msgfmt.exe')
            
            proc = subprocess.Popen( cmd, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            (out, err) = proc.communicate()
            output = string.strip(out)
            log.info( output )
            if not err.startswith(cmd):
                #log.error(err)
                log.error('msgfmt.exe not found on path')
                log.error('    try the -m DIR , --msgdir=DIR option to specify the directory or put it on the path')
                sys.exit(0)
            
            # Find SVN on system  -  optional,  if building from tarball
            if not bTarball:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\svn.exe') as key:
                        svnpath = winreg.QueryValue(key, '')
                    if path.isfile(svnpath):
                        SVN_exe = svnpath
                except WindowsError, e:
                    log.warning('SVN not found, in registory')
                    log.warning('... Hoping svn is on the path')
                    SVN_exe = 'svn'
            
        elif sys.platform == 'linux2':
            #ASSUMPTION: these tools are on the path
            #TODO: check for svn on Linux
            log.info( 'TODO: Check for svn' )
            SVN_exe = 'svn'
            #TODO: check for nsis on Linux
            log.info( 'TODO: Check for nsis' )
            MAKENSIS_exe = 'makensis'
            
        # Check if we are running a compatible vesion of NSIS
        vers = self.getNSISVersionNumber()
        if vers < MIN_NSIS_VERSION:
            log.error( "Require NSIS version %d.%d or later  ..... found NSIS version %d.%d" % (MIN_NSIS_VERSION[0],MIN_NSIS_VERSION[1], vers[0], vers[1]) )
            log.info("Disabling NSIS compilation ... Please upgrade your NSIS version")
            self.bBuildInstaller = False
        else:
            self.bBuildInstaller = True
            log.info( "NSIS version %d.%d" % vers )
            
    def expandTarBall(self, tarball, expand_dir):
        # gramps-3.1.0.tar.gz
        log.info( 'expandTarBall(%s, %s)' % (tarball, expand_dir) )
        if tarfile.is_tarfile(self.repository_path):
            tar = tarfile.open(self.repository_path)
            tar.extractall(self.out_dir)
            tar.close()
            #base = os.path.basename(self.repository_path)
            extractDir =  os.path.join(self.out_dir, self.tarbase3  )
            try:
                os.rename( extractDir, self.build_root)
            except WindowsError, e:
                log.error("FAILED: \n\t extractDir=%s \n\t build_root=%s" % (extractDir, self.build_root))
                raise WindowsError, e
        else:
            log.error( "Sorry %s is not a tar file" % self.repository_path )

    def getVersionFromTarBall(self, tarball):
        log.debug( 'getVersionFromTarBall(%s)' % (tarball))
        
        if tarfile.is_tarfile(self.repository_path):
            tar = tarfile.open(self.repository_path)
            members = tar.getnames()
            for member in members:
                if 'configure.in' in member:
                    log.debug('Reading version from: %s' % member)
                    file = tar.extractfile(member)
                    lines = file.readlines()
                    vers = self.getVersionFromLines(lines)
                if 'TODO' in member: #need to get path this will extract too, grab it of one of the files
                    self.tarbase3, rest = member.split('/', 1)
                    print '==ExtractPath', self.tarbase3
            tar.close()
        log.debug( 'Version (%s)' % (vers) )
        return vers
        
    def copyPatchTreeToDest(self, src, dst):
        '''Patch a tarball build with alternate files as required.
        At this stage do not allow new directories to be made or
        new files to be added, just replace existing files.
        '''
        log.info('Patching: now in %s', src)
        names = os.listdir(src)
        #os.makedirs(dst) - not creating new dir
        errors = []
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.isfile(srcname) and os.path.isfile(dstname):
                    log.info('Overwriting %s -> %s' % (srcname, dstname))
                    shutil.copyfile(srcname, dstname)
                elif os.path.isdir(srcname) and os.path.isdir(dstname):
                    self.copyPatchTreeToDest(srcname, dstname)
                else:
                    log.error('UNDEFINED: %s -> %s' % (srcname, dstname))
            except (IOError, os.error), why:
                errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error, err:
                errors.extend(err.args[0])
        if errors:
            raise Error(errors)
                
def buildGRAMPS( base, out_dir, bTarball):
    bo = buildbase()

    bo.repository_path = base
    bo.out_dir = out_dir
    bo.bTarball = bTarball
    bo.bBuildInstaller = bBuildInstaller
    
    if not bo.bTarball and not bo.isGrampsRoot(bo.repository_path):
        log.error( '$$$$ BAD Gramps Root specified $$$$')
    else:
        bo.checkForBuildTools()
        if bo.bTarball:
            bo.gramps_version = bo.getVersionFromTarBall( bo.repository_path )
            bo.build_root = path.normpath(os.path.join(bo.out_dir, 'gramps-%s' % bo.gramps_version))
            if bBuildAll:
                bo.cleanBuildDir()
                bo.expandTarBall(base, bo.out_dir)
            bo.copyExtraFilesToBuildDir(bo.build_root )
        else: #SVN Build
            bo.gramps_version = bo.getVersionFromConfigureIn( base )
            bo.build_root = path.normpath(os.path.join(bo.out_dir, 'gramps-%s' % bo.gramps_version))
            if bBuildAll:
                bo.cleanBuildDir()
                os.mkdir(bo.build_root)
                bo.exportSVN(os.path.join(base, 'src'), os.path.join(bo.build_root, 'src') )
                bo.exportSVN(os.path.join(base, 'po'), os.path.join(bo.build_root, 'po') )
                bo.exportSVN(os.path.join(base, 'example'), os.path.join(bo.build_root, 'examples') )
            bo.generateConstPy( ) 
            bo.copyExtraFilesToBuildDir(base)
        
        if bPatchBuild:
            bo.copyPatchTreeToDest( patch_dir, bo.build_root )
        if bBuildAll:
            bo.processPO( )
        if bo.bBuildInstaller:
            bo.compileInstallScript()


if __name__ == '__main__':
    import getopt
    import os
    import sys
    import tarfile

    usage = '''Create Gramps Windows Installer.
Usage:
    python build_GrampsWin32.py [options] [repository_path]

Arguments:
    repository_path                   Path to the repository to build GRAMPS from, this can be either
                                        - The root path of a SVN working copy
                                        - A tarball that has been saved on local disk
                                        - Left blank to build the SVN working copy this file is part of
Options:
    -h,     --help                This help message.
    -oDIR,  --out=DIR             Directory to build files (optional)
            --nsis_only           Build NSIS only (does not Clean & Build All)
    -t      --tarball             Build release version from Tarball.
    -mDIR, --msgdir=DIR           Directory to msgfmt.exe
    -pDIR, --patch=DIR            Specify a directory to patch files into the build.
                                  only valid for a tarball build.
                                  This directory will allow you to patch the release after expanding 
                                  from tarball and before creating installer.
                                  (n.b. each file to be replaced needs to be specified with full path 
                                        to exactly mimic the paths in the expanded tarball)
    '''
# TODO: nsis_dir option - a path to nsismake (for occasions script cannot work it out)
# TODO: svn_dir  option - a path to svn (for occasions script cannot work it out)
# TODO: tortoise_dir Option - accommodate windows user who dont have svn but use tortoiseSVN

    repository_path = '.' # Repository - either SVN working copy dir or Tarball file
    out_dir = None
    bBuildAll = True
    bBuildInstaller = True
    bTarball = False
    msg_dir = ""
    bPatchBuild = False
    patch_dir = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:tm:p:",
                                  ["help", "out=", "nsis_only", "tarball", "msgdir=", "patch="])

        for o, a in opts:
            if o in ("-h", "--help"):
                print usage
                sys.exit(0)

            if o in ("-o", "--out"):
                out_dir =  a
            if o in ("--nsis_only"):
                bBuildAll = False
            if o in ('-t', "--tarball"):
                print 'This is a tarball build'
                bTarball = True
            if o in ("-m", "--msgdir"):
                if os.path.isdir( a ):
                    msg_dir =  a
                else:
                    raise getopt.GetoptError, '\nERROR: msgfmt dir does not exist'
            if o in ("-p", "--patch"):
                if os.path.isdir( a ):
                    patch_dir =  a
                    bPatchBuild = True
                else:
                    raise getopt.GetoptError, '\nERROR: Patch directory does not exist'
                
        if args: #got args use first one as base dir
            repository_path = path.normpath(args[0])
        else:   # no base dir passed in, work out one from current working dir
            repository_path = path.normpath("%s/../.." % os.getcwd() )

        if bPatchBuild and not bTarball:
            log.warning("Cannot specify patch for SVN build, resetting patch option")
            patch_dir = None
    #        raise getopt.GetoptError, '\nERROR: No base directory specified'

        if len(args) > 1:
            raise getopt.GetoptError, '\nERROR: Too many arguments'

    except getopt.GetoptError, msg:
        print msg
        print '\n %s' % usage
        sys.exit(2)

    if bTarball:
        if not tarfile.is_tarfile(repository_path):
            print "Tarball %s not a valid Tarball" % repository_path
            sys.exit(1)
            
    else:    
        if not os.path.isdir(repository_path):
            print "WC root directory not found; %s " % repository_path
            sys.exit(1)

    if out_dir == None: 
        if bTarball:
            out_dir = path.normpath(os.getcwd())
        else:
            out_dir = path.normpath(os.path.join(repository_path, 'windows'))
        log.info("Setting outdir to %s", out_dir)
        

    s_args = ''
    for value in sys.argv[1:]:
        s_args = s_args + ' %s'%value

    print "======= build_GrampsWin32.py %s ========"  % s_args
    log.debug('Using %s to find python tools' % sys.prefix)
    log.info('Platform: %s' % sys.platform)
    #==========================
    sys.exit(buildGRAMPS(repository_path,out_dir, bTarball))

GObject.type_register(buildbase)