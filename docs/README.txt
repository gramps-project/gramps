Installation and building the docs
==================================

You need to install sphinx. Assuming you have installed the python setuptools, just do:

  sudo easy_install sphinx
or
  sudo pip install sphinx

Once installed, go to the docs directory, and do:

  make html

Which will produce the html output in docs/_build/html


Documentation Guidelines
=======================

Doc strings in python files should be written in reStructured text: http://docutils.sourceforge.net/docs/user/rst/quickref.html

The typical docstring for Gramps should look like this:

"""Brief synopsis

This is a longer explanation, which may include  *italics* or **bold**, or
a link to another method :meth:`~gen.lib.person.Person.get_handle`
Then, you need to provide optional subsection in this order (just to be
consistent and have a uniform documentation, nothing prevent you to switch
the order). 

:param arg1: the first value
:type arg1: int or float or :class:`~gen.lib.baseobj.BaseObject`
:param arg2: the second value
:type arg2: int or float 
:param arg3: the third value
         
:returns: arg1/arg2 +arg3
:rtype: float, this is the return type
            
       
:Examples:

>>> import template
>>> a = MainClass()
>>> a.function2(1,1,1)
2

:note:
    can be useful to emphasize
    important feature

:See Also:
    :class:`MainClass1`
       
:Warnings:
    arg2 must be non-zero.
            
:Todo:
   check that arg2 is non zero. 
"""

For a class, use :cvar variable: for class variable, :ivar variable: for instance class
variable, .. attribute:: attribute: for attributes, .... 
See http://sphinx-doc.org/markup/ and http://sphinx-doc.org/markup/inline.html

Tips and Tricks
===============
Change in many files something:

perl -pi -w -e "s/L{PersonRef}/:class:\`\~gen.lib.personref.PersonRef\`/g;" *.py 

here L{PersonRef} is changed in :class:`~gen.lib.personref.PersonRef
`
