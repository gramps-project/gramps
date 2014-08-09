# SetLanguage.py
#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2010 Stephen George
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
# $Id:  $
import locale
import _winreg
import sys
import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                    datefmt='%H:%M',
                    filename= 'c:/launcher.log', #path.join(out_dir,'build.log'),
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


langLookup = {
            'ar' : 'Arabic',
            'bg' : 'Bulgarian',
            'ca' : 'Catalan',
            'cs' : 'Czech',
            'da' : 'Danish ',
            'de' : 'German',
            'en' : 'English',
            'eo' : 'Esperanto',
            'es' : 'Spanish',
            'fi' : 'Finnish',
            'fr' : 'French',
            'ga' : 'Irish',
            'he' : 'Hebrew',
            'hr' : 'Croatian',
            'hu' : 'Hungarian',
            'it' : 'Italian',
            'ja' : 'Japanese',
            'lt' : 'Lithuanian',
            'mk' : 'Macedonian',
            'nb' : '',
            'nl' : 'Dutch',
            'nn' : '',
            'pl' : 'Polish',
            'pt_BR' : 'Portuguese (Brazil)',
            'ro' : 'Romanian',
            'ru' : 'Russian',
            'sk' : 'Slovak',
            'sl' : 'Slovenian',
            'sq' : 'Albanian',
            'sr' : 'Serbian',
            'sv' : 'Swedish',
            'tr' : 'Turkish',
            'uk' : 'Ukrainian',
            'vi' : 'Vietnamese',
            'zh_CN' : 'Chinese (PRC)',
            }

def GetGtkPath():
    log.debug('GetGtkPath()')
    dllPathInRegistry = None
    try:
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GTK\\2.0') as key:
            dllPathInRegistry = _winreg.QueryValueEx(key, 'DllPath')[0]
            # check a few key files exist at this location
            gtkfiles = ['libgdk-win32-2.0-0.dll', 'libglib-2.0-0.dll', 'libgobject-2.0-0.dll', 'libcairo-2.dll'] 
            for file in gtkfiles:
                if not os.path.isfile(os.path.join(dllPathInRegistry, file)):
                    dllPathInRegistry = None # one of the files not present, so assume path is wrong
                    break
    except WindowsError, e:
        dllPathInRegistry = None
    log.debug(' DLLPATH=%s'%dllPathInRegistry)
    return dllPathInRegistry

def GetGrampsPath():
    GrampsPathInRegistry = None
    try:  
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GRAMPS') as key:
            GrampsPathInRegistry = _winreg.QueryValue(key, '')
            # check a few key files exist at this location
    except WindowsError, e:
        GrampsPathInRegistry = None
        
    log.debug(' GRAMPSPATH=%s'%GrampsPathInRegistry)
    return GrampsPathInRegistry
    
def GetLanguageFromLocale():
    lang = ' '
    try:
        lang = os.environ["LANG"]
        lang = lang.split('.')[0]
    except:
        # if LANG is not set
        lang = locale.getlocale()[0]
        if not lang:
            # if lang is empty/None
            lang = locale.getdefaultlocale()[0] 
    return lang

def writeLauncher(language, langcode, runtimepath, grampspath):
    lines = []
    lines.append('''@rem Setting the working language
@rem ============================    
@rem GRAMPS looks during the start-up-phase for an environment variable (called LANG) 
@rem to switch to a special language. It's better to use a ".CMD" or ".BAT" file to 
@rem control this environment variable instead a permanent setting in the windows registry,
@rem to have the possibility to go back to the GRAMPS standard language (English) in the 
@rem case you want to report about a problem or a bug.
''')    
    lines.append('\n@rem Set GRAMPS environment settings to %s \n' % language)
    lines.append('SET LANG=$LANG$ \nSET LANGUAGE=$LANG$\n'.replace("$LANG$", langcode) )
    
    lines.append('''\n\n@rem Setting the configuration path
@rem ==============================    
@rem During the boot process of GRAMPS there is a check for an environment variable
@rem called GRAMPSHOME. Without this environment variable GRAMPS uses the default 
@rem windows path as the location to save all configuration files:
@rem <system drive>\<userpath>\<application data>\gramps 
@rem If required, uncomment GRAMPSHOME line and edit to suit your use.
 ''')
    lines.append('\n@rem set the path for GRAMPS configuration files')
    lines.append('\n@rem set GRAMPSHOME=PATH_TO_CONFIG_FILES')

    lines.append('''\n\n@rem Put GTK runtime on PATH
@rem =========================
@rem Ensure GTK runtime on path first, so right GTK DLL's used.
''')
    if runtimepath:
        lines.append('\n@rem Put your gtk runtime first on path')
        path = '\npath="%s";%%PATH%%' % runtimepath
    else:
        lines.append('\n@rem Uncommnet following line, and edit path to your GTK runtime')
        path = "\n@rem path=PATH_TO_YOUR_GTK_RUNTIME;%%PATH%%\n" 
    lines.append(path)
    lines.append('''\n\n@rem Start GRAMPS application
@rem =========================
@rem Start GRAMPS with pythonw.exe (Python interpreter that runs without a command line console) 
''')
    lines.append('\n@rem start Gramps')
    lines.append('\n"%s" "%s"\n' % (os.path.join(sys.prefix, 'pythonw.exe') , os.path.join(grampspath, 'gramps.py' ) ))
    fout = open( os.path.join(grampspath, 'gramps_locale.cmd'), 'w')
    fout.writelines(lines)
    fout.close()
    for line in lines:
        print line

gtkpath = GetGtkPath()
grampspath = GetGrampsPath()
lang = GetLanguageFromLocale()
if lang:
    try:
        lang_text = langLookup[lang.split('_', 1)[0]]
    except KeyError, e:
        try:
            lang_text = langLookup[lang]
        except KeyError, e:
            lang_text = "Unknown"
        
    writeLauncher(lang_text, "%s.utf-8"%lang, gtkpath, grampspath)    
