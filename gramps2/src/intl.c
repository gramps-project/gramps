/***********************************************************
Copyright (C) 1997 Martin von Löwis

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies.

This software comes with no warranty. Use at your own risk.
******************************************************************/
#include <stdio.h>
#include <errno.h>
#include <libintl.h>
#include <locale.h>
#include "Python.h"

static PyObject*
PyIntl_gettext(PyObject* self,PyObject *args)
{
  char *in;
  if (!PyArg_ParseTuple(args,"z",&in))
    return 0;

  if (*in == '\0')
    return PyString_FromString("");
  return PyString_FromString(gettext(in));
}

static PyObject*
PyIntl_dgettext(PyObject* self,PyObject *args)
{
  char *domain,*in;
  if(!PyArg_ParseTuple(args,"zz",&domain,&in))return 0;
  return PyString_FromString(dgettext(domain,in));
}

static PyObject*
PyIntl_dcgettext(PyObject *self,PyObject *args)
{
  char *domain,*msgid;
  int category;
  if(!PyArg_ParseTuple(args,"zzi",&domain,&msgid,&category))
    return 0;
  return PyString_FromString(dcgettext(domain,msgid,category));
}

static PyObject*
PyIntl_textdomain(PyObject* self,PyObject* args)
{
  char *domain;
  if(!PyArg_ParseTuple(args,"z",&domain))return 0;
  return PyString_FromString(textdomain(domain));
}

static PyObject*
PyIntl_bindtextdomain(PyObject* self,PyObject*args)
{
  char *domain,*dirname;
  if(!PyArg_ParseTuple(args,"zz",&domain,&dirname))return 0;
  return PyString_FromString(bindtextdomain(domain,dirname));
}

static PyObject*
PyIntl_setlocale(PyObject* self,PyObject* args)
{
  int category;
  char *locale=0;
  if(!PyArg_ParseTuple(args,"i|z",&category,&locale))return 0;
  return Py_BuildValue("z",setlocale(category,locale));
}

static PyObject*
PyIntl_localeconv(PyObject* self,PyObject* args)
{
  PyObject* result;
  struct lconv *l;
  if(!PyArg_NoArgs(args))return 0;
  result = PyDict_New();
  if(!result)return 0;
  l=localeconv();
#define RESULT_STRING(s) \
  PyDict_SetItemString(result,#s,PyString_FromString(l->s))
#define RESULT_INT(i) \
  PyDict_SetItemString(result,#i,PyInt_FromLong(l->i))

#define RESULT_CHAR(c) {\
    char tmp[2]; \
    tmp[0]=l->c;tmp[1]='\0';\
    PyDict_SetItemString(result,#c,PyString_FromString(tmp)); \
  }  

    /* Numeric information */
  RESULT_STRING(decimal_point);
  RESULT_STRING(thousands_sep);
  RESULT_STRING(grouping);

  /* Monetary information */
  RESULT_STRING(int_curr_symbol);
  RESULT_STRING(currency_symbol);
  RESULT_STRING(mon_decimal_point);
  RESULT_STRING(mon_thousands_sep);
  RESULT_STRING(mon_grouping);
  RESULT_STRING(positive_sign);
  RESULT_STRING(negative_sign);
  RESULT_INT(int_frac_digits);
  RESULT_INT(frac_digits);
  RESULT_INT(p_cs_precedes);
  RESULT_INT(p_sep_by_space);
  RESULT_INT(n_cs_precedes);
  RESULT_INT(n_sep_by_space);
  RESULT_INT(p_sign_posn);
  RESULT_INT(n_sign_posn);

  return result;
}


static struct PyMethodDef PyIntl_Methods[] = {
  {"gettext",(PyCFunction)PyIntl_gettext,1},
  {"dgettext",(PyCFunction)PyIntl_dgettext,1},
  {"dcgettext",(PyCFunction)PyIntl_dcgettext,1},
  {"textdomain",(PyCFunction)PyIntl_textdomain,1},
  {"bindtextdomain",(PyCFunction)PyIntl_bindtextdomain,1},
  {"setlocale",(PyCFunction)PyIntl_setlocale,1},
  {"localeconv",(PyCFunction)PyIntl_localeconv,0},
  {NULL, NULL}
};

void
#ifdef VER15
initintl15()
#elif VER20
initintl20()
#elif VER21
initintl21()
#elif VER22
initintl22()
#endif
{
  PyObject *m,*d;
#ifdef VER15
  m=Py_InitModule("intl15",PyIntl_Methods);
#elif VER20
  m=Py_InitModule("intl20",PyIntl_Methods);
#elif VER21
  m=Py_InitModule("intl21",PyIntl_Methods);
#elif VER22
  m=Py_InitModule("intl22",PyIntl_Methods);
#endif
  d = PyModule_GetDict(m);
  PyDict_SetItemString(d,"LC_CTYPE",PyInt_FromLong(LC_CTYPE));
  PyDict_SetItemString(d,"LC_NUMERIC",PyInt_FromLong(LC_NUMERIC));
  PyDict_SetItemString(d,"LC_TIME",PyInt_FromLong(LC_TIME));
  PyDict_SetItemString(d,"LC_COLLATE",PyInt_FromLong(LC_COLLATE));
  PyDict_SetItemString(d,"LC_MONETARY",PyInt_FromLong(LC_MONETARY));
  PyDict_SetItemString(d,"LC_MESSAGES",PyInt_FromLong(LC_MESSAGES));
  PyDict_SetItemString(d,"LC_ALL",PyInt_FromLong(LC_ALL));
  if(PyErr_Occurred())
    Py_FatalError("Can't initialize module intl");
}
