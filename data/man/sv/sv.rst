Swedish
=======

Gramps(1)			     3.4.0			     Gramps(1)



**NAMN**
       Gramps - Genealogical Research and Analysis Management Programming Sys‐
       tem.


**SAMMANFATTNING**
       Gramps  [-?|--help]  [--usage]  [--version]  [-l]   [-u|--force-unlock]
       [-O|--open= DATABAS [-f|--format= FORMAT]] [-i|--import= FIL [-f|--for‐
       mat= FORMAT]] [-i|--import= ...]  [-e|--export= FIL [-f|--format=  FOR‐
       MAT]]  [-a|--action=  ÅTGÄRD] [-p|--options= ALTERNATIVSTRÄNG]] [ FIL ]
       [--version]


**BESKRIVNING**
       Gramps är ett Free/OpenSource släktforskningsprogram. Det är skrivet  i
       Python, med hjälp av GTK+/GNOME gränssnittet.  Gramps bör kännas bekant
       för de flesta, som har använt  andra  släktforskningsprogram  tidigare,
       som Family Tree Maker (TM), Personal Ancestral Files (TM), DISGEN eller
       GNU Geneweb.  Det stöder import via det populära  GEDCOM-formatet,  som
       används över hela världen av nästan all släktforskningsprogramvara.


**ALTERNATIV**
       **Gramps** *FIL*
	      När *FIL* ges  (utan  några flaggor) som namn på ett familjeträd
	      eller som en mapp med familjeträd, så öppnas detta och en inter‐
	      aktiv session startas.  Om FIL är en fil, vars format förstås av
	      Gramps, skapas ett tomt famljeträd, vars namn är grundat på nam‐
	      net  FIL och vars data importeras till det.  Resterande alterna‐
	      tiv ignoreras. Detta sätt att starta passar  vid	användning  av
	      Gramps som en hanterare för släktforskningsdata i t. ex. en web-
	      läsare.  Detta startsätt accepterar alla inbyggda dataformat för
	      Gramps, se nedan.


       **-f** , **--format=** *FORMAT*
	      Uttryckligen  specificera  format  på FIL givet av föregående -i
	      eller -e-alternativ. Om -f-alternativet inte ges för någon  FIL,
	      gissas  filformat  för  den  filen utgående från dess filändelse
	      eller dess MIME-typ.

	      De format, som är tillgängliga för utmatnig, är Gramps-xml (gis‐
	      sas  om FIL slutar på .Gramps), gedcom (gissas om FIL slutar med
	      .ged) eller någon  filexport,  som  är  tillgänglig  via	Gramps
	      tilläggsprogramsystem.

	      De   format,   som   är  tillgängliga  för  inmatnig,  är  grdb,
	      Gramps-xml, gedcom, Gramps-pkg (gissas om FIL slutar med	.gpkg)
	      och geneweb (gissas om FIL slutar med .gw).

	      De format, som är tillgängliga för export är Gramps-xml, gedcom,
	      Gramps-pkg, wft (gissas om FIL slutar med .wft), geneweb och iso
	      (gissas aldrig, specificeras alltid med -f-alternativ).


       **-l**     
          Listar alla databaser/familjeträd.


       **-u** , **--force-unlock**
	      Tvingar upplåsning av databas.


       **-O** , **--open=** *DATABAS*
	      Öppnar *DATABAS* , som måste vara en befitlig databasmapp eller ett
	      befintligt familjeträd.  Om ingen åtgärd, import	eller  export-
	      alternativ  anges på kommandoraden så startas en interaktiv ses‐
	      sion med den angivna databasen.


       **-i** , **--import=** *FIL*
	      Importera data från FIL. Om du inte har specificerat en databas,
	      skapas en temporär sådan, som tas bort när Gramps avslutas.

	      Om  mer  är  en  indatafil  anges, måste varje föregås av en -i-
	      flagga.  Filerna importeras i den givna ordningen, t.ex. -i FIL1
	      -i  FIL2	och  -i FIL2 -i FIL1 kan skapa skilda Gramps IDs i den
	      resulterande databasen.


       **-e** , **--export=** *FIL*
	      Exporterar data till *FIL* . För iso-format, är *FIL* i själva verket
	      namnet  på den mapp, som Gramps databas kommer att skrivas till.
	      För Gramps-xml, gedcom, wft, Gramps-pkg och geneweb, är *FIL* nam‐
	      net på resultatfilen.

	      Om  mer  är  en  utdatafil  anges, måste varje föregås av en -e-
	      flagga.  Filerna skrivs en efter en i den givna ordningen.


       **-a** , **--action=** *ÅTGÄRD*
	      Utför ÅTGÄRD på importerade  data.  Detta  görs  efter  att  all
	      import har avslutats felfritt. F. n. är följand åtgärder möjliga
	      summary	(samma	  som	 Rapporter->Visa->Sammanfattning    av
	      databasen) ,  check  (samma  som Verktyg->Reparera databas ->Kon‐
	      trollera och reparera) samt report ( skapar report, kräver
	      en *ALTERNATIVSTRÄNG* lämnad via **-p** flaggan ) .

	      *ALTERNATIVSTRÄNG* -en måste uppfylla följand villkor:
	      Får ej innehålla några mellanslag.  Om  några  argument  behöver
	      inbegripa  mellanslag,  måste  strängen  omslutas  av  anföring‐
	      stecken.	Alternativsträngen är en lista med  par  av  namn  och
	      värden  (åtskiljda  av  likhetstecken).	Namn  och  värde måste
	      åtskiljas med komma.

	      De flesta rapportalternativ är unika  för  varje	rapport  eller
	      verktyg. Emellertid finns det gemensamm alternativ.

	      **name=rapportnamn**
	      Detta  är  obligatoriskt	och bestämmer vilken rapport som skall
	      skapas.  Om det givna namn inte motsvarar någon  möjlig  rapport
	      eller verktyg, kommer ett felmeddelande att skrivas ut, följt av
	      möjliga namn på rapporter eller verktyg.

	      **show=all**
	      Detta ger en lista med namn på alla möjliga  alternativ  för  en
	      bestämd rapport eller verktyg.

	      **show=optionname**
	      Detta  skriver  ut beskrivningen av den funktion, som optionname
	      innebär, likväl vad som är godkända typer och värden  för  detta
	      alternativ.

	      Använd  alternativen ovan för att ta reda på all om en viss rap‐
	      port.


       Om mer än en utdataåtgärd givits måste varje föregås av	en  -a-flagga.
       Åtgärderna utförs en och en i den givna turordningen.


       **-d** , **--debug=** *LOGGER_NAME*
	      Kopplar  på avlusningshjälpmedel för utveckling och tester.  För
	      detaljer hänvisas till källkoder

       **--version**
	      Skriver ur Gramps versionsnummer och avslutar


**Operation**
       Om första argumentet på kommandoraden inte inledds med ett  minustecken
       (d.  v. s. ingen flagga), kommer Gramps att försöka öppna den fil, vars
       namn givits av det första argumentet samt påbörja en interaktiv session
       utan att ta hänsyn till resten av argumenten på kommandoraden.


       Om  -O-flagga  givits,  kommer  Gramps  att  försöka öppna den omnämnda
       databasen och sedan arbeta med dess data, enligt  ytterligare  instruk‐
       tioner på kommandoraden.


       Med eller utan -Oflagga, kan det ske många importeringar, exporteringar
       och åtgärder beskrivna ytterligare på kommanodraden genom  att  använda
       -i-, -e- samt -a-flaggor.


       Ordningen  på  -i-,  -e-  eller -a-alternativen spelar ingen roll.  Den
       gällande ordningen är alltid: all import (om någon)  ->	alla  åtgärder
       (om  några)  ->	all  export  (om  någon). Men öppning måste alltid ske
       först!


       Om inget -O- eller -i-alternativ givits, kommer Gramps att starta  sitt
       huvudfönster  samt påbörja den vanliga interaktiva sessionen med en tom
       databas, då hur som helst inget data finns att bearbeta.


       Om inget -e- eller -a-alternativ givits, kommer Gramps att starta  sitt
       huvudfönster  samt  påbörja  den  vanliga interaktiva sessionen med den
       databas, som blev resultet från all import. Denna databas  återfinns  i
       import_db.grdb under ~/.Gramps/import-mappen.


       De  fel	som  inträffar	under import, export eller vid åtgärder kommer
       antingen att skrivas till stdout (om dessa avbrott hanteras av  Gramps)
       eller  till stderr (om dessa inte hanteras). Använd vanliga skalkomman‐
       don för att styra om stdout och stderr till att	spara  medelanden  och
       fel i filer.


**EXAMPEL**
       För  att öppna ett befintligt familjeträd och importera en xml-fil till
       det, kan man skriva:
       
	      Gramps -O 'Mitt familjeträd' -i ~/db3.Gramps

       Ovanstående ändrar det öppnade familjeträdet, för att göra  samma  sak,
       men  importera  bägge  till  ett tillfälligt familjeträd och påbörja en
       interaktiv session, kan man skriva:
       
	      Gramps -i 'My Family Tree' -i ~/db3.Gramps

       För att importera fyra databaser (vars  format  kan  avgöras  av  deras
       namn)  och  sedan  felkontrollera  den resulterande  databasen, kan man
       skriva:
       
	      Gramps -i FIL1.ged -i FIL2.tgz -i ~/db3.Gramps  -i  FIL4.wft  -a
	      check

       För  att  uttryckligen  specificera formaten i examplet ovan, lägg till
       filnamn med passande -f-alternativ:
       
	      Gramps -i FIL1.ged  -f  gedcom  -i  FIL2.tgz  -f	Gramps-pkg  -i
	      ~/db3.Gramps -f Gramps-xml -i FIL4.wft -f wft -a check

       För  att  spara	den  databas,  som är resultat av all import, ange -e-
       flagga (använd -f om filnamnet inte tillåter Gramps att gissa dess for‐
       mat):
       
	      Gramps -i FIL1.ged -i FIL2.tgz -e ~/new-package -f Gramps-pkg

       För  att importera tre databaser och påbörja en interaklive Gramps-ses‐
       sion med importresultatet:
       
	      Gramps -i FIL1.ged -i FIL2.tgz -i ~/db3.Gramps

       För att köra  verifieringsverktyget  från  kommandoraden  och  mata  ut
       resultatet till stdout:
       
	      Gramps -O file.grdb -a tool -p name=verify

       Slutligen, för att påbörja en normal interaktiv session skriv bara:
       
	      Gramps


**BEGREPP**
       Stöder ett python-baserat system för tilläggsprogram, som möjliggör att
       import- och export-funktioner, rapportgeneratorer,  verktyg  samt  vis‐
       ningsfilter, kan komplettera Gramps utan ändringar i huvudprogrammet.

       Förutom	att  skapa utskrift på skrivare direkt, kan rapportgeneratorer
       ha andra målsystem som OpenOffice.org, AbiWord, HTML eller LaTeX så att
       användaren kan tillåtas att ändra format för att passa behoven.


**KÄNDA FEL OCH BEGRÄNSNINGAR**
**FILER**

       *${PREFIX}/bin/gramps*
       
       *${PREFIX}/lib/python/dist-packages/gramps/*
       
       *${PREFIX}/share/*
       
       *${HOME}/.gramps*


**FÖRFATTARE**
       Donald Allingham <don@gramps-project.org>
       http://gramps-project.org/

       Denna man-sida skrevs ursprungligen av:
       Brandon L. Griffith <brandon@debian.org>
       till att ingå i Debians GNU/Linux-system.

       Denna man-sida underhålls f. n. av:
       Alex Roitman <shura@gramps-project.org>

       Denna man-sida har översatts till svenska av:
       Peter Landgren <peter.talken@telia.com>


**DOCUMENTATION**
       Användardokumentationen	är  tillgänglig  genom GNOME's standard hjälp-
       bläddrare i form av Gramps-handboken. Handboken finns även i XML-format
       som  gramps-manual.xml  under  doc/gramps-manual/$LANG i den officiella
       källdistributionen. Dock ej på svenska.

       Utvecklingsdokumentationen kan hittas på
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers 


Januari 2013			     4.0.0			     Gramps(1)
