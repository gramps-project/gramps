dnl AM_SHARED_MIME
dnl Defines SHARED_MIME_DIR which is where mime type definitions should go.
dnl

AC_DEFUN([AM_SHARED_MIME],
[
  if test "x$SHARED_MIME_DIR" = "x"; then
    SHARED_MIME_DIR='$(prefix)/share/mime'
  fi

  AC_ARG_WITH(mime-dir,
  [  --with-mime-dir=dir     Shared mime directory.],SHARED_MIME_DIR="$withval",)

  AC_SUBST(SHARED_MIME_DIR)
  AC_MSG_RESULT([Using directory $SHARED_MIME_DIR for installation of mime type definitions])
])
