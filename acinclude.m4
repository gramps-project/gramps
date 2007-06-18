dnl AM_GCONF2_REPLACEMENT
dnl Defines GCONF_SCHEMA_CONFIG_SOURCE which is where you should install schemas
dnl  (i.e. pass to $GCONFTOOL
dnl Defines GCONF_SCHEMA_FILE_DIR which is a filesystem directory where
dnl  you should install foo.schemas files
dnl
dnl This macro was copied from AM_GCONF_SOURCE_2 from the gconf2-dev package.
dnl By copying it here we remove the requirement for having it on the system.

AC_DEFUN([AM_GCONF2_REPLACEMENT],
[
  if test "x$GCONF_SCHEMA_INSTALL_SOURCE" = "x"; then
    GCONF_SCHEMA_CONFIG_SOURCE=`$GCONFTOOL --get-default-source`
  else
    GCONF_SCHEMA_CONFIG_SOURCE=$GCONF_SCHEMA_INSTALL_SOURCE
  fi

  AC_ARG_WITH(gconf-source, 
  [  --with-gconf-source=sourceaddress      Config database for installing schema files.],GCONF_SCHEMA_CONFIG_SOURCE="$withval",)

  AC_SUBST(GCONF_SCHEMA_CONFIG_SOURCE)
  AC_MSG_RESULT([Using config source $GCONF_SCHEMA_CONFIG_SOURCE for schema installation])

  if test "x$GCONF_SCHEMA_FILE_DIR" = "x"; then
    GCONF_SCHEMA_FILE_DIR='$(sysconfdir)/gconf/schemas'
  fi

  AC_ARG_WITH(gconf-schema-file-dir, 
  [  --with-gconf-schema-file-dir=dir        Directory for installing schema files.],GCONF_SCHEMA_FILE_DIR="$withval",)

  AC_SUBST(GCONF_SCHEMA_FILE_DIR)
  AC_MSG_RESULT([Using $GCONF_SCHEMA_FILE_DIR as install directory for schema files])

  AC_ARG_ENABLE(schemas-install,
     [  --disable-schemas-install	Disable the schemas installation],
     [case "${enableval}" in
       yes) schemas_install=true ;;
       no)  schemas_install=false ;;
       *) AC_MSG_ERROR(bad value ${enableval} for --disable-schemas-install) ;;
     esac],[schemas_install=true])
     AM_CONDITIONAL(GCONF_SCHEMAS_INSTALL, test x$schemas_install = xtrue)
])

dnl AM_SHARED_MIME
dnl Defines SHARED_MIME_DIR which is where mime type definitions should go.
dnl

AC_DEFUN([AM_SHARED_MIME],
[
  if test "x$SHARED_MIME_DIR" = "x"; then
    SHARED_MIME_DIR='$(prefix)/share/mime'
  fi

  AC_ARG_WITH(mime-dir,
  [  --with-mime-dir=dir	Shared mime directory.],SHARED_MIME_DIR="$withval",)

  AC_SUBST(SHARED_MIME_DIR)
  AC_MSG_RESULT([Using directory $SHARED_MIME_DIR for installation of mime type definitions])

  AC_ARG_ENABLE(mime-install,
     [  --disable-mime-install	Disable the mime types installation],
     [case "${enableval}" in
       yes) mime_install=true ;;
       no)  mime_install=false ;;
       *) AC_MSG_ERROR(bad value ${enableval} for --disable-mime-install) ;;
     esac],[mime_install=true])
  AM_CONDITIONAL(SHARED_MIME_INSTALL, test x$mime_install = xtrue)

])


dnl AM_PACKAGER
dnl Defines conditional PACKAGER_MODE to define packager mode
dnl

AC_DEFUN([AM_PACKAGER],
[
  AC_ARG_ENABLE(packager_mode,
     [  --enable-packager-mode          Enable packager mode],
     [case "${enableval}" in
       yes) packager_mode=true ;;
       no)  packager_mode=false ;;
       *) AC_MSG_ERROR(bad value ${enableval} for --enable-packager-mode) ;;
     esac],[packager_mode=false])
  AM_CONDITIONAL(PACKAGER_MODE, test x$packager_mode = xtrue)
  if test "x$packager_mode" = "xtrue"; then
     AC_MSG_RESULT([WARNING: 
     	Packager mode enabled.
        GConf schemas and shared mime types WILL NOT BE INSTALLED.
	You will need to place the contents of the
		GCONF_SCHEMAS_INSTALLATION and SHARED_MIME_INSTALLATION
	commands MANUALLY into the postinstall script of your package,
	see src/data/Makefile.am file for details.
	Otherwise you will end up with the unusable package.
	YOU HAVE BEEN WARNED!])
  fi
])
