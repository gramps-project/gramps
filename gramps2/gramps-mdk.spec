%define ver      1.1.0
%define rel      0.CVS20040609
%define prefix   /usr
%define localstatedir /var/lib
# Ensure that internal RPM macros for configure & makeinstall 
# will expand properly
%define _prefix   %prefix
%define _localstatedir %localstatedir

Summary: Genealogical Research and Analysis Management Programming System.
Name: gramps
Version: %ver
Release: %rel
License: GPL
Group: Applications/Genealogy
Source: http://download.sourceforge.net/gramps/gramps-%{ver}.tar.gz
BuildRoot: /var/tmp/%{name}-%{version}-root

URL: http://gramps.sourceforge.net/

Requires: python >= 2.2
Requires: gnome-python >= 1.99
Requires: gnome-python-gconf >= 1.99
Requires: gnome-python-canvas >= 1.99
Requires: gnome-python-gnomevfs >= 1.99
Requires: pygtk2.0-libglade >= 1.99

BuildRequires: scrollkeeper >= 0.3.5
BuildRequires: automake >= 1.6
BuildRequires: autoconf >= 2.52
BuildRequires: rpm >= 4.1
BuildRequires: desktop-file-utils >= 0.2.92

%description
gramps (Genealogical Research and Analysis Management Programming
System) is a GNOME based genealogy program supporting a Python
based plugin system.

%prep
%setup

%build
if [ ! -f configure ]; then
  CFLAGS="$MYCFLAGS" ./autogen.sh $MYARCH_FLAGS --prefix=%prefix \
    --localstatedir=%localstatedir --bindir=%{_bindir} \
    --mandir=%{_mandir} --libdir=%{_libdir} --datadir=%{_datadir} \
    --includedir=%{_includedir} --sysconfdir=%{_sysconfdir}
else
  CFLAGS="$MYCFLAGS" %configure
fi

CFLAGS="$RPM_OPT_FLAGS" make

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall
mkdir $RPM_BUILD_ROOT%{_datadir}/applications
desktop-file-install --vendor gramps --delete-original \
	--dir $RPM_BUILD_ROOT%{_datadir}/applications  \
	--add-category Application                     \
	--add-category Utility                         \
	$RPM_BUILD_ROOT%{_datadir}/gnome/apps/Applications/gramps.desktop
%find_lang gramps
rm -rf $RPM_BUILD_ROOT/%{_localstatedir}/scrollkeeper/

%clean
rm -rf $RPM_BUILD_ROOT

%files -f gramps.lang
%defattr(-, root, root)

%doc AUTHORS COPYING COPYING-DOCS ChangeLog FAQ INSTALL NEWS README TODO 
%doc %{_mandir}/man1/*

%{prefix}/bin/gramps

%{_datadir}/applications/*
%{_datadir}/pixmaps/gramps.png

%{_libdir}/gramps
%{_datadir}/gramps
%{_datadir}/omf/gramps

%post
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update; fi

%postun
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update; fi
 
%changelog
* Tue Dec  2 2003 Tim Waugh <twaugh@redhat.com>
- More docs.
- Change Copyright: to License:.

* Fri Sep 19 2003 Tim Waugh <twaugh@redhat.com>
- Own %%{_datadir/gramps directory.
- Ship %%{_libdir}/gramps.
* Mon May 20 2003 Donald Peterson <dpeterson@sigmaxi.org>
- Override RPMs default of localstatedir to /var/lib..
  This is done in accordance with GNOME and FHS compliance guidelines 
  (http://fedora.mplug.org/docs/rpm-packaging-guidelines.html)
- Use %find_lang macro to get NLS files
- Set %doc tags on appropriate files
- Remove temporary scrollkeeper-created files from install before packaging
  to avoid rpm 4.1 complaints.  (These aren't needed in the distribution.)
- Use default scrollkeeper-update scripts
* Mon Mar 24 2003 Alex Roitman <shura@alex.neuro.umn.edu>
- update scrollkeeper dependencies and add post and postun to enable install on a machine without scrollkeeper
* Fri Jun 14 2002 Donald Peterson <dpeterso@engr.ors.edu>
- add scrollkeeper dependencies and some file cleanup
