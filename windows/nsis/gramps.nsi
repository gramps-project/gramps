#
# Filename: gramps.nsi
#
# Description: Nullsoft Installer (NSIS) file to build Windows installer:
# Updated:     2006-07-26 13:12:28-0400
# Author:      Steve Hall [ digitect dancingpaper com ]
#
# Requires:    NSIS version 2.0 or later.
# Notes:
# o WARNING: if you make changes to this script, look out for $INSTDIR
#   to be valid, because this line is very dangerous:  RMDir /r $INSTDIR
# o WARNING: Except the uninstaller. That re-paths for some reason.
#

#               Installer Attributes
# 0. Base Settings {{{1

# version numbers
!define GRAMPS_VER_MAJOR $%VERSION%
!define GRAMPS_VER_MINOR $%VERSIONSUB%
!define GRAMPS_VER_POINT $%VERSIONPT%

# adds Native Language Support
!define HAVE_NLS

# output file
Name "GRAMPS"
OutFile gramps-${GRAMPS_VER_MAJOR}.${GRAMPS_VER_MINOR}.${GRAMPS_VER_POINT}.exe

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

# don't allow installation into C:\
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
InstallDirRegKey HKCU "Software\${MUI_PRODUCT}" ""

# Remember the installer language
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\${MUI_PRODUCT}"
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

!define MUI_FINISHPAGE_RUN "python"
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
!insertmacro MUI_LANGUAGE "Danish"
#!insertmacro MUI_LANGUAGE "Default"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "English"
#!insertmacro MUI_LANGUAGE "Estonian"
#!insertmacro MUI_LANGUAGE "Farsi"
#!insertmacro MUI_LANGUAGE "Finnish"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
#!insertmacro MUI_LANGUAGE "Greek"
#!insertmacro MUI_LANGUAGE "Hebrew"
#!insertmacro MUI_LANGUAGE "Hungarian"
#!insertmacro MUI_LANGUAGE "Indonesian"
!insertmacro MUI_LANGUAGE "Italian"
#!insertmacro MUI_LANGUAGE "Japanese"
#!insertmacro MUI_LANGUAGE "Korean"
#!insertmacro MUI_LANGUAGE "Latvian"
#!insertmacro MUI_LANGUAGE "Lithuanian"
#!insertmacro MUI_LANGUAGE "Macedonian"
#!insertmacro MUI_LANGUAGE "Norwegian"
#!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "Portuguese"
!insertmacro MUI_LANGUAGE "PortugueseBR"
#!insertmacro MUI_LANGUAGE "Romanian"
#!insertmacro MUI_LANGUAGE "Russian"
#!insertmacro MUI_LANGUAGE "Serbian"
#!insertmacro MUI_LANGUAGE "SerbianLatin"
#!insertmacro MUI_LANGUAGE "SimpChinese"
#!insertmacro MUI_LANGUAGE "Slovak"
#!insertmacro MUI_LANGUAGE "Slovenian"
!insertmacro MUI_LANGUAGE "Spanish"
#!insertmacro MUI_LANGUAGE "Swedish"
#!insertmacro MUI_LANGUAGE "Thai"
#!insertmacro MUI_LANGUAGE "TradChinese"
#!insertmacro MUI_LANGUAGE "Turkish"
#!insertmacro MUI_LANGUAGE "Ukrainian"

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
	#File /r ..\nsis\gramps.ico

SectionEnd

#    Icons, menus and shortcuts {{{1

SubSection "Icons, menus and shortcuts" MenusAndIcons

Section "Add GRAMPS to the Start Menu" MenuStart
SectionIn 1 3
	# determines "Start In" location for shortcuts
	SetOutPath $INSTDIR

	CreateDirectory "$SMPROGRAMS\GRAMPS\"
	CreateShortCut "$SMPROGRAMS\GRAMPS\GRAMPS.lnk" "$3" "$\"$INSTDIR\gramps.py$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
	WriteINIStr "$SMPROGRAMS\GRAMPS\GRAMPS Website.url" "InternetShortcut" "URL" "http://www.gramps-project.org/"
	CreateShortCut "$SMPROGRAMS\GRAMPS\Uninstall GRAMPS.lnk" "$\"$INSTDIR\uninstall.exe$\"" "" "" "0" "" "" "Uninstall GRAMPS"

SectionEnd

Section "Add Desktop icon" Desktop
#SectionIn 1 3
# determines "Start In" location for shortcuts
SetOutPath $INSTDIR
CreateShortCut "$DESKTOP\GRAMPS.lnk" "$3" "$\"$INSTDIR\gramps.py$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
SectionEnd

SubSectionEnd

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

	unEnd:

SectionEnd

# 1}}}
#               7b. Functions
#    Installer {{{1
#####################################################################

Function .onInit

	; test for dependencies
	MessageBox MB_OK "Testing dependencies..."

	; look for python.exe
	; NOTE: This is set to $3 if it exists.

	; on path
	SearchPath $3 python.exe
#MessageBox MB_OK "DEBUG: Testing python.exe on path...$\n$\nFound:  $\"$3$\""
	IfFileExists $3 HavePython 0

    ; registry keys (these are confirmed possibilities)
	; reg key
	ReadRegStr $3 HKCR 'Applications\python.exe\shell\open\command' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
	ReadRegStr $3 HKLM 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\python.exe' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
	ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.4' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
	ReadRegStr $3 HKLM 'SOFTWARE\Python\PythonCore\2.4\InstallPath' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCR 'Python.File\shell\open\command' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCU 'Software\Classes\Python.File\shell\open\command' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCU 'Software\Microsoft\Windows\Current version\App Paths\Python.exe' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCU 'Software\Microsoft\Windows\ShellNoRoam\MUICache (data:python)' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.4\InstallPath' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0
	; reg key
    ReadRegStr $3 HKCU 'Software\Python\PythonCore\2.4\PythonPath' ""
	StrCpy $3 "$3python.exe"  ; append "python.exe"
	IfFileExists $3 HavePython 0


	; TODO: request path from user/browse (can NSIS do this?)
		MessageBox MB_OK "Python not found, unable to continue."
		Abort
		HavePython:

	; extract gcheck
	SetOutPath $TEMP
#MessageBox MB_OK "DEBUG: $$TEMP location found:$\n$\n  $TEMP"
	File gcheck.py
	; set INI output location ($1)
	StrCpy $1 "$TEMP\gramps-install.ini"
#MessageBox MB_OK "DEBUG: Attempting to run:$\n$\n  $\"$3$\" $TEMP\gcheck.py $1"
	; run gcheck
	Exec '"$3" $TEMP\gcheck.py $1'

    ; Note The Exec above is a fork, meaning the following file test
    ;      will fail because it happens faster than the Exec can run
    ;      to create it!
	DetailPrint "pausing..."
	Sleep 1000
	

	; verify INI created
	IfFileExists $1 YesINI 0
		MessageBox MB_OK "Dependency test INI creation failed, unable to continue."
		Abort
		YesINI:

	; verify environment test results
	; GTK+
	ReadINIStr $0 $1 tests gtk
	StrCmp $0 "yes" HaveGTK 0
		MessageBox MB_OK "GTK+ not installed, unable to continue."
		Abort
		HaveGTK:
	; pygtk
	ReadINIStr $0 $1 tests pygtk
	StrCmp $0 "yes" Havepygtk 0
		MessageBox MB_OK "pygtk not installed, unable to continue."
		Abort
		Havepygtk:
	; glade
	ReadINIStr $0 $1 tests glade
	StrCmp $0 "yes" Haveglade 0
		MessageBox MB_OK "glade not installed, unable to continue."
		Abort
		Haveglade:
	; pycairo
	ReadINIStr $0 $1 tests pycairo
	StrCmp $0 "yes" Havepycairo 0
		MessageBox MB_OK "pycairo not installed, unable to continue."
		Abort
		Havepycairo:

	#!insertmacro MUI_LANGDLL_DISPLAY

	# default install directory ($INSTDIR)
	StrCpy $INSTDIR $PROGRAMFILES\gramps

FunctionEnd

Function .onInstSuccess
	# write uninstaller
	WriteUninstaller $INSTDIR\uninstall.exe
FunctionEnd

Function .onInstFailed
	MessageBox MB_OK|MB_ICONEXCLAMATION "Installation failed."
FunctionEnd

Function WarnDirExists
	# warn if dir already exists
	IfFileExists $INSTDIR\*.* DirExists DirExistsOK
	DirExists:
	MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
		"Install over existing?" \
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

	IfFileExists "$DESKTOP\GRAMPS.lnk" 0 unNoDesktop
	Delete "$DESKTOP\GRAMPS.lnk"
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
	LangString DESC_Prog ${LANG_ENGLISH} "GRAMPS..."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN

	!insertmacro MUI_DESCRIPTION_TEXT ${Main} $(DESC_Main)
	!insertmacro MUI_DESCRIPTION_TEXT ${MenusAndIcons} $(DESC_MenusAndIcons)
	!insertmacro MUI_DESCRIPTION_TEXT ${Desktop} $(DESC_Desktop)
	!insertmacro MUI_DESCRIPTION_TEXT ${MenuStart} $(DESC_MenuStart)
	!insertmacro MUI_DESCRIPTION_TEXT ${Prog} $(DESC_Prog)

!insertmacro MUI_FUNCTION_DESCRIPTION_END

# 1}}}
# vim:foldmethod=marker:noexpandtab
