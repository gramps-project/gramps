%define ver      0.1.3
%define rel      1
%define prefix   /usr

Summary: Genealogical Research and Analysis Management Programming System.
Name: gramps
Version: %ver
Release: %rel
Copyright: GPL
Group: Applications/Genealogy
Source: http://download.sourceforge.net/gramps/gramps-%{ver}.tar.gz
BuildRoot: /var/tmp/%{name}-%{version}-root

URL: http://gramps.sourceforge.net

Requires: python >= 1.5.2
Requires: pygnome >= 1.0.53
Requires: PyXML

%description
GRAMPS is an acronym for the Genealogical Research and Analysis
Management Programming System.  It was conceived under the concept
that most genealogy programs were designed to provide the
researcher the capability to input information related to a
particular family tree.

%prep
%setup

%build
if [ ! -f configure ]; then
  CFLAGS="$MYCFLAGS" ./autogen.sh $MYARCH_FLAGS --prefix=%prefix
else
  CFLAGS="$MYCFLAGS" ./configure $MYARCH_FLAGS --prefix=%prefix
fi

make

%install
rm -rf $RPM_BUILD_ROOT

make GNOME_DATADIR=$RPM_BUILD_ROOT%{prefix}/share prefix=$RPM_BUILD_ROOT%{prefix} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)

%doc README COPYING TODO
%{prefix}/bin/gramps
%{prefix}/share/gnome/apps/Applications/gramps.desktop
%{prefix}/share/pixmaps/gramps.png
# %{prefix}/share/gramps/*
%{prefix}/share/locale/*/LC_MESSAGES/gramps.mo
%{prefix}/share/gramps/*.pyo
%{prefix}/share/gramps/*.glade
%{prefix}/share/gramps/*.sxw
%{prefix}/share/gramps/*.xpm
%{prefix}/share/gramps/*.jpg
%{prefix}/share/gramps/filters/*
%{prefix}/share/gramps/plugins/*
