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
        Shared mime types WILL NOT BE INSTALLED.
	You will need to place the contents of the
		SHARED_MIME_INSTALLATION
	commands MANUALLY into the postinstall script of your package,
	see data/Makefile.am file for details.
	Otherwise you will end up with the unusable package.
	YOU HAVE BEEN WARNED!])
  fi
])
