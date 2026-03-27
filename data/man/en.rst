gramps
======

-----------------------------------------------------------------
Genealogical Research and Analysis Management Programming System.
-----------------------------------------------------------------

:Manual section: 1
:Manual group: @VERSION@

########
SYNOPSIS
########

**gramps**
\ [\ **-?** | **--help**]
\ [\ **--usage**]
\ [\ **--version**]
\ [\ **-l**]
\ [\ **-L**]
\ [\ **-u** | **--force-unlock**]
\ [\ **-O** | **--open**\ =\ *DATABASE* [\ **-f** | **--format**\ =\ *FORMAT*]]
\ [\ **-i** | **--import**\ =\ *FILE* [\ **-f** | **--format**\ =\ *FORMAT*]]
\ [\ **--remove**\ =\ *FAMILY_TREE_PATTERN*]
\ [\ **-e** | **--export**\ =\ *FILE* [**-f** | **--format**\ =\ *FORMAT*]]
\ [\ **-a** | **--action**\ =\ *ACTION*]
\ [\ **-p** | **--options**\ =\ *OPTION-STRING*]]
\ [\ *FILE*]
\ [\ **--version**]

###########
DESCRIPTION
###########

Gramps is a Free, Open Source genealogy program.
It is written in Python, using the GTK+/GNOME interface.
Gramps should seem familiar to anyone who has used other genealogy programs
before such as Family Tree Maker™, Personal Ancestral Files™,
or the GNU Geneweb.
It supports importing of the ever-popular GEDCOM format which is used worldwide
by almost all other genealogy software.

#######
OPTIONS
#######

**gramps** *FILE*
    When *FILE* is given (without any flags) as a family tree name or as a
    family tree database directory, then it is opened and an interactive
    session is started.
    If *FILE* is a file format understood by Gramps, an empty family tree is
    created whose name is based on the *FILE* name, and the data is imported
    into it.
    Any other options are ignored.
    This way of launching is suitable for using gramps as a handler for
    genealogical data in e.g. web browsers.
    This invocation can accept any data format native to gramps; see below.

**-f**, **--format**\ =\ *FORMAT*
    Explicitly specify format of *FILE* given by preceding **-i** or **-e**
    option.
    If the **-f** option is not given for any *FILE*, the format of that file
    is guessed according to its extension or MIME type.

    Formats available for export are **gramps-xml** (guessed if *FILE* ends
    with `.gramps`), **gedcom** (guessed if *FILE* ends with `.ged`), or any
    file export available through the Gramps plugin system.

    Formats available for import are **gramps-xml**, **gedcom**, **gramps-pkg**
    (guessed if *FILE* ends with `.gpkg`), and **geneweb** (guessed if *FILE*
    ends with `.gw`).

    Formats available for export are **gramps-xml**, **gedcom**,
    **gramps-pkg**, **wft** (guessed if *FILE* ends with `.wft`),
    **geneweb**.

**-l**
    Print a list of known family trees.

**-L**
    Print a detailed list of known family trees.

**-u**, **--force-unlock**
    Unlock a locked database.

**-O**, **--open**\ =\ *DATABASE*
    Open *DATABASE* which must be an existing database directory or existing
    family tree name.
    If no action, import, or export options are given on the command line, then
    an interactive session is started using that database.

**-i**, **--import**\ =\ *FILE*
    Import data from *FILE*.
    If no database was specified, then an empty database is created
    called Family Tree *x* (where *x* is an incrementing number).

    When more than one input file is given,
    each has to be preceded by a **-i** flag.
    The files are imported in the specified order, e.g.,
    **-i** *FILE1* **-i** *FILE2*
    and
    **-i** *FILE2* **-i** *FILE1*
    might produce different gramps IDs in the resulting database.

**-e**, **--export**\ =\ *FILE*
    Export data into *FILE*.
    For **gramps-xml**, **gedcom**, **wft**, **gramps-pkg**, and **geneweb**,
    the *FILE* is the name of the resulting file.

    When more than one output file is given,
    each has to be preceded by a **-e** flag.
    The files are written one by one, in the specified order.

**-a**, **--action**\ =\ *ACTION*
    Perform *ACTION* on the imported data.
    This is done after all imports are successfully completed.
    Currently available actions are **summary** (same as
    Reports→View→Summary), **check** (same as Tools→Database
    Processing→Check and Repair), **report** (generates report), and tool
    (runs a plugin tool).
    Both **report** and **tool** need the *OPTION-STRING* supplied by the
    **-p** flag).

    The *OPTION-STRING* should satisfy the following conditions:

    - It should not contain any spaces.
    - If some arguments need to include spaces, the string should be enclosed
      with quotation marks, following shell syntax.
    - The option string is a list of pairs with name and value (separated by an
      equals sign).
    - The name and value pairs must be separated by commas.

    Most of the report or tools options are specific for each report or tool.
    However, there are some common options.

    **name**\ =\ *name*
        This mandatory option determines which report or tool will be run.
        If the supplied *name* does not correspond to any available report or
        tool, an error message will be printed followed by the list of
        available reports or tools (depending on the *ACTION*).

    **show**\ =\ **all**
        This will produce the list of names for all options available for a
        given report or tool.

    **show**\ =\ *optionname*
        This will print the description of the functionality supplied by
        *optionname*, as well as what are the acceptable types and values for
        this option.

    Use the above options to find out everything about a given report.

    When more than one output action is given, each has to be preceded by a
    **-a** flag.
    The actions are performed one by one, in the specified order.

**-d**, **--debug**\ =\ *LOGGER_NAME*
    Enable debug logs for development and testing.
    Look at the source code for details.

**--version**
    Print the version number of gramps and then exits.

#########
OPERATION
#########

If the first argument on the command line does not start with dash (i.e., no
flag), gramps will attempt to open the file with the name given by the first
argument and start an interactive session, ignoring the rest of the command line
arguments.

If the **-O** flag is given, then gramps will try opening the supplied database
and then work with that data, as instructed by the further command line
parameters.

With or without the **-O** flag, further imports, exports, and actions may be
specified on the command line by using **-i**, **-e**, and
**-a** flags.

The order of **-i**, **-e**, or **-a** options does not matter.
The actual order they are processed always is:
all imports (if any) → all actions (if any) → all exports (if any).
But opening must always be first!

If no **-O** or **-i** option is given,
gramps will launch its main window and start the usual interactive session with
an empty database, since there is no data to process anyway.

If no **-e** or **-a** options are given,
gramps will launch its main window and start the usual interactive session with
the database resulting from all imports.
This database resides in the *import_db.grdb* under the *~/.gramps/import*
directory.

Any errors encountered during import, export, or action
will be dumped either to *stdout* (if these are exceptions handled by gramps)
or to *stderr* (if these are not handled).
Use usual shell redirections of *stdout* and *stderr* to save messages and
errors to files.

########
EXAMPLES
########

To open an existing family tree and import an xml file into it, one may type::

    gramps -O 'My Family Tree' -i ~/db3.gramps

The above changes the opened family tree. To do the same, but import both in a
temporary family tree and start an interactive session, one may type::

    gramps -i 'My Family Tree' -i ~/db3.gramps

To import four databases (whose formats can be determined from their names) and
then check the resulting database for errors, one may type::

    gramps -i file1.ged -i file2.tgz -i ~/db3.gramps -i file4.wft -a check

To explicitly specify the formats in the above example, append filenames with
appropriate **-f** options::

    gramps -i file1.ged -f gedcom -i file2.tgz -f gramps-pkg \
    -i ~/db3.gramps -f gramps -i file4.wft -f wft -a check

To record the database resulting from all imports, supply a **-e** flag (use
**-f** if the filename does not allow gramps to guess the format)::

    gramps -i file1.ged -i file2.tgz -e ~/new-package -f gramps-pkg

To import three databases and start an interactive gramps session with the
result::

    gramps -i file1.ged -i file2.tgz -i ~/db3.gramps

To run the Verify tool from the commandline and output the result to
*stdout*::

    gramps -O 'My Family Tree' -a tool -p name= verify

Finally, to start a normal interactive session type::

    gramps

#####################
ENVIRONMENT VARIABLES
#####################

The program checks whether these environment variables are set:

``LANG``
    Describe which language to use.
    E.g., for the Polish language this variable has to be set to `pl_PL.UTF-8`.

``GRAMPSHOME``
    Force Gramps to use the specified directory to keep program
    settings and databases in.
    By default, this variable is not set and gramps assumes that the folder
    with all databases and profile settings should be created within the user
    profile folder (described by environment variable *HOME* for Linux or
    *USERPROFILE* for Windows 2000/XP).

``CONCEPTS``
    Supports a python-based plugin system, allowing import and export writers,
    report generators, tools, and display filters to be added without
    modification of the main program.

    In addition to generating direct printer output, report generators also
    target other output formats, such as *LibreOffice*, *AbiWord*, *HTML*, or
    *LaTeX* to allow the users to modify the format to suit their needs.

#####
FILES
#####

    *${PREFIX}/bin/gramps*

    *${PREFIX}/lib/python3/dist-packages/gramps/*

    *${PREFIX}/share/*

    *${HOME}/.gramps*

#######
AUTHORS
#######

Donald Allingham <don@gramps-project.org>
https://www.gramps-project.org/

This man page was originally written by:
Brandon L. Griffith <brandon@debian.org>
for inclusion in the Debian GNU/Linux system.

This man page is currently maintained by:
Gramps project <xxx@gramps-project.org>

#############
DOCUMENTATION
#############

The user documentation is available through a web browser in the form of the
Gramps Manual.

The developer documentation can be found on the
https://www.gramps-project.org/wiki/index.php/Portal:Developers
portal.
