Dutch
======

gramps(1)			     3.4.0			     gramps(1)



**NAAM**
       gramps - Genealogisch Onderzoek en Analyse Beheersysteem.


**SAMENVATTING**
       gramps  [-?|--help]  [--usage]  [--version] [-O|--open= GEGEVENSBESTAND
       [-f|--format= FORMAAT]] [-i|--import= BESTAND  [-f|--format=  FORMAAT]]
       [-i|--import=   ...]   [-e|--export=  BESTAND  [-f|--format=  FORMAAT]]
       [-a|--action= ACTIE] [-p|--options= OPTIESTRING]] [ BESTAND  ]  [--ver‐
       sion]


**BESCHRIJVING**
       Gramps  is  een	Free/OpenSource  genealogisch programma dat in Python,
       geschreven is en gebruik maakt van de GTK+/GNOME interface.  Gramps zal
       voor iedereen die al gewerkt heeft met andere genealogische programma's
       zoals Family Tree Maker (TM),  Personal Ancestral  Files  (TM)  of  GNU
       Geneweb.   Importeren vanuit het gekende GEDCOM-formaat wordt onderste‐
       und. Dit formaat wordt wereldwijd gebruikt door bijna alle  genealogis‐
       che software.


**OPTIES**
       **gramps** *BESTAND*
	      Wanneer *BESTAND* opgegeven wordt (zonder vlaggen) als een famili‐
	      estamboom of als een familistamboommap, dan  wordt  dit  bestand
	      geopend en een interactieve sessie wordt gestart. Indien BESTAND
	      een bestandsformaat dat door Gramps herkent wordt, zal een  lege
	      familiestamboom	aangemaakt   worden.   De  bestandsnaam  wordt
	      gebaseerd op de *BESTAND*  naam  en  de  gegevens  worden  in  dit
	      bestand  geïmporteerd. Met resterende opties wordt geen rekening
	      gehouden. Deze wijze van opstarten is zeer bruikbaar  om	Gramps
	      te  gebruiken  voor  genealogische  gegevens via een webbrowser.
	      Deze opstartmethode kan gelijk welk  gegevensformaat  eigen  aan
	      Gramps behandelen, zie onder.


       **-f** , **--format=** *FORMAAT*
	      Expliciet  een formaat opgeven voor BESTAND door de optie -i, of
	      -e mee te geven. Indien de -f optie niet	opgegeven  wordt  voor
	      BESTAND,	wordt  het formaat gebaseerd op de bestandsextensie of
	      het MIME-type.

	      Formaten beschikbaar voor uitvoer zijn  gramps-xml  (guessed  if
	      FILE  ends  with	.gramps),  gedcom  (guessed  if FILE ends with
	      .ged), or any file export available through  the	Gramps	plugin
	      system.

	      Formats  available  for  import  are  grdb,  gramps-xml, gedcom,
	      gramps-pkg (guessed  if  FILE  ends  with  .gpkg),  and  geneweb
	      (guessed if FILE ends with .gw).

	      Formats available for export are gramps-xml, gedcom, gramps-pkg,
	      wft (guessed if FILE ends with .wft), geneweb,  and  iso	(never
	      guessed, always specify with -f option).


       **-O** , **--open=** *DATABASE*
          Open *DATABASE* which  must be an existing database directory or
          existing family tree name. If no action, import or export
          options are given on the command line then an interactive ses‐
          sion is started using that database.


       **-i** , **--import=** *FILE*
          Import data from *FILE* . If you haven't specified a database then
          a  temporary database is used; this is deleted when you exit
          gramps.

          When more than one input file is given, each has to be preceded
          by **-i** flag. The files are imported in the specified order, i.e.
          **-i** *FILE1* **-i** *FILE2* and **-i** *FILE2* **-i** *FILE1* 
          might produce different gramps IDs in the resulting database.


       **-a** , **--action=** *ACTION*
          Perform *ACTION* on the imported data. This is done after all
          imports are successfully completed. Currently available  actions
          are **summary** (same  as  Reports->View->Summary), **check** (same as
          Tools->Database Processing->Check and Repair), **report** (generates
          report),  and  tool  (runs a plugin tool).  Both **report** and **tool**
          need the *OPTIONSTRING* supplied by the **-p** flag).

          The *OPTIONSTRING* should satisfy the following conditions:
          It must not contain any  spaces. If some arguments need to
          include spaces, the string should be enclosed with quotation
          marks, i.e., follow the shell syntax. Option string is a list
          of  pairs  with name and value (separated by the equality sign).
          The name and value pairs must be separated by commas.

          Most of the report or tools options are specific for each report
          or tool. However, there are some common options.

          **name=name**
          This mandatory option determines which report or tool will be
          run. If the supplied name does not correspond to any  available
          report or tool, an error message will be printed followed by the
          list of available reports or tools (depending on the *ACTION* ).

          **show=all**
          This will produce the list of names for all options available
          for a given report or tool.

          **show=optionname**
          This will print the description of the functionality supplied by
          *optionname*, as well as what are the acceptable types and  values
          for this option.

          Use the above options to find out everything about a given
          report.


       When more than one output action is given, each has to be preceded  by
       **-a** flag. The actions are performed one by one, in the specified order.


       **-d** , **--debug=** *LOGGER_NAME*
          Enables debug logs for development and testing. Look at the
          source code for details

       **--version**
          Prints the version number of gramps and then exits




**werking**
       Indien het eerste argument in de opdrachtregel niet start met dash (dus
       geen vlag) dan zal Gramps trachten om het bestand  te  openen  met  een
       naam  die  in  het eerste argument werd opgegeven. Vervolgens wordt een
       interactieve  sessie  gestart  en  de   overige	 argumenten   van   de
       opdrachtregel worden genegeerd.

       If the  **-O** flag is given, then gramps will try opening the supplied
       database and then work with that data, as instructed by the further
       command line parameters.


       With or without the **-O** flag, there could be multiple imports, exports,
       and actions specified further on the command line by using **-i** , 
       **-e** , and **-a** flags.


       The order of **-i** , **-e** , or **-a** options does not matter. The actual order
       always is: all imports (if any) -> all actions (if any) -> all  exports
       (if any). But opening must always be first!


       If no **-O** or **-i** option is given, gramps will launch its main window and
       start the usual interactive session with the empty database, since
       there is no data to process, anyway.


       If no **-e**  or **-a** options are given, gramps will launch its main window
       and start the usual interactive session with the database resulted from
       all imports. This database resides in the **import_db.grdb** under
       **~/.gramps/import** directory.


       The error encountered during import, export, or action, will be  either
       dumped to stdout (if  these  are exceptions handled by gramps) or to
       *stderr* (if these are not handled). Use usual shell redirections of
       *stdout* and *stderr* to save messages and errors in files.


**EXAMPLES**
       To open an existing family tree and import an xml file into it, one
       may type:
          
          **gramps -O** *'My Family Tree'* **-i** *~/db3.gramps*

       The above changes the opened family tree, to do the  same, but import
       both in a temporary family tree and start an interactive session, one
       may type:
       
          **gramps -i** *'My Family Tree'* **-i** *~/db3.gramps*

       To import four databases (whose formats can be  determined from their
       names) and then check the resulting database for errors, one may type:
       
          **gramps -i** *file1.ged* **-i** *file2.tgz* **-i** *~/db3.gramps* 
          **-i** *file4.wft* **-a** *check*

       To explicitly specify the formats in the above  example,  append  file‐
       names with appropriate **-f** options:
          
          **gramps -i** *file1.ged* **-f** *gedcom* **-i** *file2.tgz* **-f** 
          *gramps-pkg* **-i** *~/db3.gramps* **-f** *gramps-xml* **-i** *file4.wft*
          **-f** *wft* **-a** *check*

       To record the database resulting from all imports, supply **-e** flag  (use
       **-f** if the filename does not allow gramps to guess the format):
       
          **gramps -i** *file1.ged* **-i** *file2.tgz* **-e** *~/new-package*
          **-f** *gramps-pkg*

       To import three databases and start interactive gramps session with the
       result:
          
          **gramps -i** *file1.ged* **-i** *file2.tgz* **-i** *~/db3.gramps*

       To run the Verify tool from the commandline and output the result to
       stdout:
       
          **gramps -O** *'My Family Tree'* **-a** *tool* **-p name=** *verify*

       Finally, to start normal interactive session type:
       
          **gramps**


**CONCEPTEN**
       Ondersteuning van een op python-gebaseerd plugin systeem. Dit laat  toe
       om verslagen, hulpgereedschappen en vensterfilters toe te voegen zonder
       dat het hoofdprogramma dient aangepast.

       De klassieke uitdrukken zijn mogelijk, maar daar  bovenover  kunnen  de
       meeste  verslagen  ook gebruik maken van OpenOffice.org, AbiWord, HTML,
       of LaTeX. Zo kunnen gebruikers het formaat wijzigen naar eigen wens.


**GEKENDE BUGS EN BEPERKINGEN**

**BESTANDEN**

       *${PREFIX}/bin/gramps*
       
       *${PREFIX}/lib/python/dist-packages/gramps/*
       
       *${PREFIX}/share/*
       
       *${HOME}/.gramps*


**AUTEURS**
       Donald Allingham <don@gramps-project.org>
       http://gramps-project.org/

       Deze man pagina werd oorspronkelijk geschreven door:
       Brandon L. Griffith <brandon@debian.org>
       voor het Debian GNU/Linux systeem.

       Deze man pagina wordt momenteel onderhouden door:
       Alex Roitman <shura@gramps-project.org>

       Deze nederlandstalige man pagina wordt momenteel onderhouden door:
       Erik De Richter <frederik.de.richter@pandora.be>


**DOCUMENTATIE**
       De gebruikersdocumentatie is beschikbaar via browser in de webstek.

       De  ontwikkelingsdocumentatie kan gevonden worden op de 
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers 
       webstek.



August 2005			     4.0.0			     gramps(1)
