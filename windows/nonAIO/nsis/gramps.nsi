#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2006-2008 Steve Hall <digitect dancingpaper com>
# Copyright (C) 2008 Stephen George
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
#
# Description: Nullsoft Installer (NSIS) file to build Windows installer:
#
# Requires:    NSIS version 2.0 or later.
# Notes:
# o WARNING: if you make changes to this script, look out for $INSTDIR
#   to be valid, because this line is very dangerous:  RMDir /r $INSTDIR
# o WARNING: Except the uninstaller. That re-paths for some reason.
#

# ToDo {{{1
#
# o More refined dependency checking (versioning)
# o Add .gramps and .gpkg as extensions
#   * => Need separate icons for them?
#
# 1}}}
#               Installer Attributes
# 0. Base Settings {{{1

# version numbers
!define GRAMPS_VER_MAJOR $%VERSION%
!define GRAMPS_VER_MINOR $%VERSIONSUB%
!define GRAMPS_VER_POINT $%VERSIONPT%
!define GRAMPS_VER_BUILD $%VERSIONBUILD%

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "GRAMPS"
!define PRODUCT_VERSION ${GRAMPS_VER_MAJOR}.${GRAMPS_VER_MINOR}.${GRAMPS_VER_POINT}-${GRAMPS_VER_BUILD}
!define PRODUCT_PUBLISHER "The GRAMPS project"
!define PRODUCT_WEB_SITE "http://gramps-project.org"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define DESKTOP_LINK "$DESKTOP\${PRODUCT_NAME} ${PRODUCT_VERSION}.lnk"

# adds Native Language Support
!define HAVE_NLS

# output file
Name ${PRODUCT_NAME}
OutFile gramps-${PRODUCT_VERSION}.exe

# self ensure we don't have a corrupted file
CRCCheck on

# compression
SetCompress auto
# zlib good, bzip2 better, lzma best (and slowest, whew.)
SetCompressor lzma
# reference existing store if possible
SetDatablockOptimize on
# UPX
# comment next line if you don't have UPX (http://upx.sourceforge.net)
!packhdr temp.dat "upx --best --compress-icons=0 temp.dat"

SetOverwrite try

# don't allow installation into C:\ directory
AllowRootDirInstall false

# install details color scheme
InstallColors /windows
# background
BGGradient off

# adds an XP manifest
XPStyle on

# default install path
InstallDir $PROGRAMFILES\gramps

# Remember install folder
InstallDirRegKey HKCU "Software\${PRODUCT_NAME}" ""

# Remember the installer language
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\${PRODUCT_NAME}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

# types of installs we can perform
InstType Typical
InstType Minimal
InstType Full

SilentInstall normal

# 1. Header file (Begin Modern User Interface)  {{{1
!include "MUI.nsh"

# 2. Interface Configuration {{{1

# installer/uninstaller icons (these must match in size!)
#!define MUI_ICON "classic-install.ico"
#!define MUI_UNICON "classic-uninstall.ico"

# splash, header graphics (same for both!)
!define MUI_HEADERIMAGE
#!define MUI_HEADERIMAGE_BITMAP "win.bmp"
#!define MUI_WELCOMEFINISHPAGE_BITMAP "nsis-splash.bmp"

!define MUI_LICENSEPAGE_BUTTON $(^AgreeBtn)
!define MUI_LICENSEPAGE_RADIOBUTTONS
!define MUI_LICENSEPAGE_RADIOBUTTONS_TEXT_ACCEPT $(^AcceptBtn)
!define MUI_LICENSEPAGE_RADIOBUTTONS_TEXT_DECLINE $(^DontAcceptBtn)

#!define MUI_COMPONENTSPAGE_CHECKBITMAP "nsis-checkboxes.bmp"
# use small description box below components (not adjacent)
!define MUI_COMPONENTSPAGE_SMALLDESC

!define MUI_DIRECTORYPAGE_TEXT_TOP $(^DirText)
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION $(^DirBrowseText)
!define MUI_DIRECTORYPAGE_VERIFYONLEAVE

!define MUI_FINISHPAGE_RUN "$3"
!define MUI_FINISHPAGE_RUN_PARAMETERS "$\"$INSTDIR\gramps.py$\""

!define MUI_ABORTWARNING

# 3. Pages {{{1

!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_LICENSE "..\COPYING"

!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH


# Uninstaller

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# 4. Custom functions {{{1

# 5. Language files {{{1
# Languages
# TODO: These are pretty badly broken at the moment.
# Note: This appears to be due to building on Win95 which does not
#       support Unicode:
#       (http://nsis.sf.net/archive/nsisweb.php?page=247&instances=0,235)
#
#   So what happens if we use only ASCII?
#
#!insertmacro MUI_LANGUAGE "Arabic"
#!insertmacro MUI_LANGUAGE "Bulgarian"
#!insertmacro MUI_LANGUAGE "Catalan"
#!insertmacro MUI_LANGUAGE "Croatian"
#!insertmacro MUI_LANGUAGE "Czech"
#!insertmacro MUI_LANGUAGE "Default"
#!insertmacro MUI_LANGUAGE "Estonian"
#!insertmacro MUI_LANGUAGE "Farsi"
#!insertmacro MUI_LANGUAGE "Finnish"
#!insertmacro MUI_LANGUAGE "Greek"
#!insertmacro MUI_LANGUAGE "Hebrew"
#!insertmacro MUI_LANGUAGE "Hungarian"
#!insertmacro MUI_LANGUAGE "Indonesian"
#!insertmacro MUI_LANGUAGE "Japanese"
#!insertmacro MUI_LANGUAGE "Korean"
#!insertmacro MUI_LANGUAGE "Latvian"
#!insertmacro MUI_LANGUAGE "Lithuanian"
#!insertmacro MUI_LANGUAGE "Macedonian"
#!insertmacro MUI_LANGUAGE "Norwegian"
#!insertmacro MUI_LANGUAGE "Polish"
#!insertmacro MUI_LANGUAGE "Romanian"
#!insertmacro MUI_LANGUAGE "Russian"
#!insertmacro MUI_LANGUAGE "Serbian"
#!insertmacro MUI_LANGUAGE "SerbianLatin"
#!insertmacro MUI_LANGUAGE "SimpChinese"
#!insertmacro MUI_LANGUAGE "Slovak"
#!insertmacro MUI_LANGUAGE "Slovenian"
#!insertmacro MUI_LANGUAGE "Swedish"
#!insertmacro MUI_LANGUAGE "Thai"
#!insertmacro MUI_LANGUAGE "TradChinese"
#!insertmacro MUI_LANGUAGE "Turkish"
#!insertmacro MUI_LANGUAGE "Ukrainian"

!insertmacro MUI_LANGUAGE "Danish"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "Portuguese"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Spanish"

# 6. Reserve Files  {{{1

# 1}}}
#               7a. Sections
#    Program Files {{{1
######################################################################

Section "Program files (required)" Main
SectionIn 1 2 3 RO

    Call WarnDirExists

    SetOutPath $INSTDIR
    File /r ..\src\*.*
    File ..\COPYING
    File ..\NEWS
    File ..\FAQ
    File ..\AUTHORS
    #File /r ..\nsis\gramps.ico
    WriteRegStr HKLM "SOFTWARE\${PRODUCT_NAME}" "" "$INSTDIR"
    WriteRegStr HKLM "SOFTWARE\${PRODUCT_NAME}" "version" ${PRODUCT_VERSION}

SectionEnd

#    Menus and shortcuts {{{1

SubSection "Menus and shortcuts" MenusAndIcons

Section "Add GRAMPS to the Start Menu" MenuStart
SectionIn 1 3
    # determines "Start In" location for shortcuts
    SetOutPath $INSTDIR

    StrCpy $0 "GRAMPS"

    IfFileExists "$SMPROGRAMS\$0" 0 skipStartMenuRemove
    RMDir /r "$SMPROGRAMS\$0\"
    skipStartMenuRemove:

    CreateDirectory "$SMPROGRAMS\$0\"
    CreateShortCut "$SMPROGRAMS\$0\GRAMPS ${PRODUCT_VERSION}.lnk" "$3" "$\"$INSTDIR\gramps.py$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
    WriteINIStr "$SMPROGRAMS\$0\GRAMPS Website.url" "InternetShortcut" "URL" "http://www.gramps-project.org/"
    CreateShortCut "$SMPROGRAMS\$0\Uninstall GRAMPS.lnk" "$\"$INSTDIR\uninstall.exe$\"" "" "" "0" "" "" "Uninstall GRAMPS"

SectionEnd

Section "Add Desktop icon" Desktop
#SectionIn 1 3
# determines "Start In" location for shortcuts
SetOutPath $INSTDIR
CreateShortCut "${DESKTOP_LINK}" "$3" "$\"$INSTDIR\gramps.py$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
SectionEnd

SubSectionEnd

#    Language Files {{{1

Section "Language Files" LangFiles
# off by default
#SectionIn 1 3

    #CreateDirectory $INSTDIR\lang
    SetOutPath $INSTDIR
    File /r ..\po\*.mo

    #MessageBox MB_OK "Setting up languages..."
    # setup
    ; switches:
    ; -c
    ; -t :: setup the language files
    ; -r
    ;
    ; pythonw grampsSetup.py -c -t
    #Exec '"$3" $\"$INSTDIR\grampsSetup.py -c -t -r$\"'

SectionEnd

#    File Association {{{1

#    FileAssoc.nsh macro {{{2
;
; FileAssoc.nsh (http://nsis.sourceforge.net/FileAssoc)
; File association helper macros
; Written by Saivert
;
; Features automatic backup system and UPDATEFILEASSOC macro for
; shell change notification.
;
; |> How to use <|
; To associate a file with an application so you can double-click it in explorer, use
; the APP_ASSOCIATE macro like this:
;
;   Example:
;   !insertmacro APP_ASSOCIATE \
;      "txt" \
;      "myapp.textfile" \
;      "myapp tiny description" \
;     "$INSTDIR\myapp.exe,0" \
;     "Open with myapp" \
;     "$INSTDIR\myapp.exe $\"%1$\""
;
; Never insert the APP_ASSOCIATE macro multiple times, it is only ment
; to associate an application with a single file and using the
; the "open" verb as default. To add more verbs (actions) to a file
; use the APP_ASSOCIATE_ADDVERB macro.
;
;   Example:
;   !insertmacro APP_ASSOCIATE_ADDVERB "myapp.textfile" "edit" "Edit with myapp" \
;     "$INSTDIR\myapp.exe /edit $\"%1$\""
;
; To have access to more options when registering the file association use the
; APP_ASSOCIATE_EX macro. Here you can specify the verb and what verb is to be the
; standard action (default verb).
;
; And finally: To remove the association from the registry use the APP_UNASSOCIATE
; macro. Here is another example just to wrap it up:
;   !insertmacro APP_UNASSOCIATE "txt" "myapp.textfile"
;
; |> Note <|
; When defining your file class string always use the short form of your application title
; then a period (dot) and the type of file. This keeps the file class sort of unique.
;   Examples:
;   Winamp.Playlist
;   NSIS.Script
;   Photoshop.JPEGFile
;
; |> Tech info <|
; The registry key layout for a file association is:
; HKEY_CLASSES_ROOT
;     <applicationID> = <"description">
;         shell
;             <verb> = <"menu-item text">
;                 command = <"command string">
;

!macro APP_ASSOCIATE EXT FILECLASS DESCRIPTION ICON COMMANDTEXT COMMAND
    ; Backup the previously associated file class
    ReadRegStr $R0 HKCR ".${EXT}" ""
    WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"

    WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"
    WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
    WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
    WriteRegStr HKCR "${FILECLASS}\shell" "" "open"
    WriteRegStr HKCR "${FILECLASS}\shell\open" "" `${COMMANDTEXT}`
    WriteRegStr HKCR "${FILECLASS}\shell\open\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_EX EXT FILECLASS DESCRIPTION ICON VERB DEFAULTVERB SHELLNEW COMMANDTEXT COMMAND
    ; Backup the previously associated file class
    ReadRegStr $R0 HKCR ".${EXT}" ""
    WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"

    WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"
    StrCmp "${SHELLNEW}" "0" +2
    WriteRegStr HKCR ".${EXT}\ShellNew" "NullFile" ""

    WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
    WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
    WriteRegStr HKCR "${FILECLASS}\shell" "" `${DEFAULTVERB}`
    WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
    WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_ADDVERB FILECLASS VERB COMMANDTEXT COMMAND
    WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
    WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_REMOVEVERB FILECLASS VERB
    DeleteRegKey HKCR `${FILECLASS}\shell\${VERB}`
!macroend


!macro APP_UNASSOCIATE EXT FILECLASS
    ; Backup the previously associated file class
    ReadRegStr $R0 HKCR ".${EXT}" `${FILECLASS}_backup`
    WriteRegStr HKCR ".${EXT}" "" "$R0"

    DeleteRegKey HKCR `${FILECLASS}`
!macroend

!macro APP_ASSOCIATE_GETFILECLASS OUTPUT EXT
    ReadRegStr ${OUTPUT} HKCR ".${EXT}" ""
!macroend


; !defines for use with SHChangeNotify
!ifdef SHCNE_ASSOCCHANGED
!undef SHCNE_ASSOCCHANGED
!endif
!define SHCNE_ASSOCCHANGED 0x08000000
!ifdef SHCNF_FLUSH
!undef SHCNF_FLUSH
!endif
!define SHCNF_FLUSH        0x1000

!macro UPDATEFILEASSOC
; Using the system.dll plugin to call the SHChangeNotify Win32 API function so we
; can update the shell.
    System::Call "shell32::SHChangeNotify(i,i,i,i) (${SHCNE_ASSOCCHANGED}, ${SHCNF_FLUSH}, 0, 0)"
!macroend

;EOF

# 2}}}

Section "File Association" FileAssoc
SectionIn 1 3
# depends on FileAssoc.nsh, by Saivert (http://nsis.sourceforge.net/FileAssoc)

    # .grdb
    !insertmacro APP_ASSOCIATE \
      "grdb" \
      "application/x-gramps-database" \
      "GRAMPS database file" \
     "$INSTDIR\images\ped24.ico" \
     "Open with GRAMPS" \
     "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .gramps
    !insertmacro APP_ASSOCIATE \
      "gramps" \
      "application/x-gramps-file" \
      "GRAMPS application file" \
     "$INSTDIR\images\ped24.ico" \
     "Open with GRAMPS" \
     "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .gpkg
    !insertmacro APP_ASSOCIATE \
      "gpkg" \
      "application/x-gramps-package" \
      "GRAMPS package file" \
     "$INSTDIR\images\ped24.ico" \
     "Open with GRAMPS" \
     "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .ged
    !insertmacro APP_ASSOCIATE \
      "ged" \
      "application/x-gramps-gedcom" \
      "GEnealogical Data COMmunication (GEDCOM) file" \
     "$INSTDIR\images\ped24.ico" \
     "Open with GRAMPS" \
     "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

SectionEnd

#    Uninstall {{{1
######################################################################

Section Uninstall

    # ask first
    MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "Completely remove installation? $\n\
        (Delete folder $INSTDIR ) " \
        IDNO unQuit IDYES unContinue

    unQuit:
    Abort

    unContinue:
    ClearErrors
    RMDir /r $INSTDIR
    Call un.StartMenu
    Call un.Desktop
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
   
    DeleteRegKey HKLM "SOFTWARE\${PRODUCT_NAME}"   

    unEnd:

SectionEnd

# 1}}}
#               7b. Functions
#    Installer {{{1
#####################################################################

Function .onInit

#MessageBox MB_OK "Testing dependencies..."

    ; look for pythonw.exe
    ; NOTE: This is set to $3 if it exists.

    ; on path
    SearchPath $3 pythonw.exe
#MessageBox MB_OK "DEBUG: Testing pythonw.exe on path...$\n$\nFound:  $\"$3$\""
    IfFileExists $3 HavePython 0

    ; registry keys (these are confirmed possibilities)
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\python.exe' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key (updated on 2.5 upgrade)
    ReadRegStr $3 HKCR 'Python.File\shell\open\command' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key (updated on 2.5 upgrade)
    ReadRegStr $3 HKCU 'Software\Classes\Python.File\shell\open\command' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKCU 'Software\Microsoft\Windows\Current version\App Paths\Python.exe' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKCU 'Software\Microsoft\Windows\ShellNoRoam\MUICache (data:python)' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key (Python version 2.5)
    ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.5\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key (Python version 2.4)
    ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.4\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    # these hold compound paths
    #; reg key (Python version 2.5)
    #ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.5\PythonPath' ""
    #StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    #IfFileExists $3 HavePython 0
    #; reg key (Python version 2.4)
    #ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.4\PythonPath' ""
    #StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    #IfFileExists $3 HavePython 0

    ; Keys not prone to be properly updated on upgrades
    ; reg key
    ReadRegStr $3 HKCR 'Applications\python.exe\shell\open\command' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key (not updated on 2.5 upgrade)
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.5\PythonPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.4\PythonPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.5' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.4' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.5\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    ; reg key
    ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.4\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0


    ; TODO: request path from user/browse (can NSIS do this?)
        #MessageBox MB_OK "GRAMPS requires Python to be installed, please see:$\n \
        #  $\n \
        #  http://gramps-project.org/windows/ $\n \
        #  $\n \
        #  for installation help. Unable to continue installation."
        #Abort
        MessageBox MB_OK "Python not found."
        StrCpy $4 "flag"
        HavePython:


    ; extract gcheck
    SetOutPath $TEMP

    File gcheck.py
    ; set INI output location ($1)
    StrCpy $1 "$TEMP\gramps-install.ini"

    ; run gcheck
    ExecWait '"$3" $TEMP\gcheck.py $1'

    ; verify INI created
    IfFileExists $1 YesINI 0
        #MessageBox MB_OK "Dependency test INI creation failed, unable to continue."
        #Abort
        MessageBox MB_OK "Dependency test INI creation failed."
        StrCpy $4 "flag"
        YesINI:

    ; verify environment test results
    ; GTK+ and pygtk
    ReadINIStr $0 $1 tests gtk
    StrCmp $0 "yes" HaveGTK 0

        ; TODO: if no, perhaps just have GTK+ installed, check registry
        ; reg key
        ReadRegStr $3 HKCU 'Environment\GTK_BASEPATH' ""
        IfFileExists $3\*.* NoHavePyGTK 0
        ; reg key
        ReadRegStr $3 HKCU 'Software\GTK\2.0\Path' ""
        IfFileExists $3\*.* NoHavePyGTK 0
        ; reg key
        ReadRegStr $3 HKLM 'Software\GTK\2.0\Path' ""
        IfFileExists $3\*.* NoHavePyGTK 0
        ; reg key
        ReadRegStr $3 HKLM 'Software\GTK\2.0\DllPath' ""
        IfFileExists $3\*.* NoHavePyGTK 0

        ; if we make it this far, we don't have GTK+
        #MessageBox MB_OK "GRAMPS requires GTK+ and PyGTK to be installed, please see:$\n \
        #  $\n \
        #  http://gramps-project.org/windows/ $\n \
        #  $\n \
        #  for installation help. Unable to continue installation."
        #Abort
        MessageBox MB_OK "GTK+ and PyGTK not found."
        StrCpy $4 "flag"

        NoHavePyGTK:
        #MessageBox MB_OK "PyGTK import failed (GTK+ found on system), please see:$\n \
        #  $\n \
        #  http://gramps-project.org/windows/ $\n \
        #  $\n \
        #  for installation help. Unable to continue installation."
        #Abort
        MessageBox MB_OK "PyGTK not found."
        StrCpy $4 "flag"

        HaveGTK:

    # NOTE: we can not detect just pygtk via gcheck.py

    ; glade
    ReadINIStr $0 $1 tests glade
    StrCmp $0 "yes" Haveglade 0
        #MessageBox MB_OK "glade not installed, unable to continue."
        #Abort
        MessageBox MB_OK "Glade not found."
        StrCpy $4 "flag"
        Haveglade:
    ; pycairo
    ReadINIStr $0 $1 tests pycairo
    StrCmp $0 "yes" Havepycairo 0
        #MessageBox MB_OK "pycairo not installed, unable to continue."
        #Abort
        MessageBox MB_OK "pycairo not found."
        StrCpy $4 "flag"
        Havepycairo:

    #!insertmacro MUI_LANGDLL_DISPLAY

    StrCmp $4 "flag" +1 DependantsOK
    MessageBox MB_OK "At least one dependency was not found, unable to continue."
    Abort

    DependantsOK:

    Call RemovePrevious
   
    # default install directory ($INSTDIR)
    StrCpy $INSTDIR $PROGRAMFILES\gramps

FunctionEnd

Function .onInstSuccess

    # write uninstaller
    WriteUninstaller $INSTDIR\uninstall.exe
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
#Does not display icon on win2000?    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\images\ped24.ico"
FunctionEnd

Function .onInstFailed
    MessageBox MB_OK|MB_ICONEXCLAMATION "Installation failed."
FunctionEnd

Function RemovePrevious
    #check if gramps exists in registry
    ClearErrors
    Var /GLOBAL PreviousPath
    ReadRegStr $PreviousPath HKLM "SOFTWARE\${PRODUCT_NAME}" ""
    # do some tests to find an installed version
    ifErrors NoPreviousVersion
        IfFileExists $PreviousPath\uninstall.exe 0 NoPreviousVersion #Check uninstall.exe from previous version exists on HD
        Var /GLOBAL PreviousVersion
        ReadRegStr $PreviousVersion HKLM "SOFTWARE\${PRODUCT_NAME}" "Version"
        #  query OK to delete old version
        MessageBox MB_OKCANCEL|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "${PRODUCT_NAME} $PreviousVersion is already installed$\n$\nClick 'OK' to uninstall previous version or 'Cancel' to continue anyway" \
        IDCANCEL NoPreviousVersion
        #  uninstall old version
        CopyFiles $PreviousPath\uninstall.exe $TEMP
        ExecWait '"$TEMP\uninstall.exe" _?=$PreviousPath' $0
        StrCpy $INSTDIR $PreviousPath #set the previous path as the default install path <= worth while or not?
        ;DetailPrint "uninstaller set error level $0"
    NoPreviousVersion:
FunctionEnd

Function WarnDirExists
    # warn if dir already exists
    IfFileExists $INSTDIR\*.* DirExists DirExistsOK
    DirExists:
    MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "Install over existing installation?" \
        IDYES DirExistsOK
    Quit
    DirExistsOK:
FunctionEnd

#    Uninstaller {{{1
#####################################################################

Function un.onUnInstSuccess

FunctionEnd

Function un.StartMenu

    IfFileExists "$SMPROGRAMS\GRAMPS" 0 unStartMenuFine
    RMDir /r "$SMPROGRAMS\GRAMPS\"
    unStartMenuFine:

FunctionEnd

Function un.Desktop

    IfFileExists "${DESKTOP_LINK}" 0 unNoDesktop
    Delete "${DESKTOP_LINK}"
    unNoDesktop:

FunctionEnd

# 1}}}
# 8. Section Descriptions {{{1
######################################################################
# (must be last)

    LangString DESC_Main ${LANG_ENGLISH} "Main program files (required)."
    LangString DESC_MenusAndIcons ${LANG_ENGLISH} "General Desktop and Start Menu shortcut options."
    LangString DESC_Desktop ${LANG_ENGLISH} "Add icon to the Desktop."
    LangString DESC_MenuStart ${LANG_ENGLISH} "Add icons to the Start Menu."
    LangString DESC_LangFiles ${LANG_ENGLISH} "Set up non-English languages."
    LangString DESC_FileAssoc ${LANG_ENGLISH} "Associate GRAMPS with .grdb, .gramps, .gpkg, and .ged files."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN

    !insertmacro MUI_DESCRIPTION_TEXT ${Main} $(DESC_Main)
    !insertmacro MUI_DESCRIPTION_TEXT ${MenusAndIcons} $(DESC_MenusAndIcons)
    !insertmacro MUI_DESCRIPTION_TEXT ${Desktop} $(DESC_Desktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${MenuStart} $(DESC_MenuStart)
    !insertmacro MUI_DESCRIPTION_TEXT ${LangFiles} $(DESC_LangFiles)
    !insertmacro MUI_DESCRIPTION_TEXT ${FileAssoc} $(DESC_FileAssoc)

!insertmacro MUI_FUNCTION_DESCRIPTION_END

# 1}}}
# vim:foldmethod=marker:noexpandtab
