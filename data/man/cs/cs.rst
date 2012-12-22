Czech
======

gramps(1)			     3.4.0			     gramps(1)



**JMÉNO**
       gramps - programový systém pro správu genealogického výzkumu a analýzy.


**POUŽITÍ**
       gramps	[-?|--help]  [--usage]	[--version]  [-l]  [-u|--force-unlock]
       [-O|--open=  DATABÁZE  [-f|--format=  FORMÁT]]	[-i|--import=	SOUBOR
       [-f|--format=   FORMÁT]]   [-i|--import=   ...]	 [-e|--export=	SOUBOR
       [-f|--format= FORMÁT]] [-a|--action= AKCE] [-p|--options= PARAMETRY]] [
       SOUBOR ] [--version]


**POPIS**
       Gramps  je  zdarma šířený Open Source genealogický program. Je napsán v
       jazyce Python s využitím rozhraní  GTK+/GNOME.	Gramps	bude  povědomý
       komukoli,  kdo už pracoval s jinými genealogickými programy jako Family
       Tree Maker (TM),  Personal Ancestral  Files  (TM),  nebo  GNU  Geneweb.
       Podporuje import dat z populárního formátu GEDCOM, který je celosvětově
       rozšířen a je využíván téměř všemi ostatními genealogickými programy.


**MOŽNOSTI**
       **gramps** *SOUBOR*
	      Pokud je zadán SOUBOR (bez dalších parametrů) jako název	rodok‐
	      menu  nebo jako adresář databáze rodokmenu, je gramps otevřeno v
	      interaktivním  módu.  Pokud  je  SOUBOR  formátem   podporovaným
	      Gramps, je vytvořen rodokmen s názvem založeným na názvu souboru
	      a data ze vstupu jsou do něho  naimportována.  Zbytek  parametrů
	      příkazové  řádky je ignorován.  Tento způsob spouštění je vhodný
	      pro gramps použitý jako prohlížeč genealogických dat  např.  pro
	      webové  prohlížeče.   Spuštění  tímto způsobem zpracuje jakákoli
	      data ve formátu podporovaném gramps, viz dále.


       **-f** , **--format=** *FORMÁT*
	      Explicitně definuje formát  SOUBORu  předchozího	parametru  -i,
	      nebo  -e.  Pokud	není parametr -f pro SOUBOR specifikován, bude
	      automaticky použit formát  odpovídající  koncovce  souboru  nebo
	      MIME-typu.

	      Formáty dostupné pro export jsou	gramps-xml (automaticky použit
	      pokud má SOUBOR koncovku .gramps),  gedcom  (automaticky	použit
	      pokud  má SOUBOR koncovku .ged), případně jiný další formát dos‐
	      tupný prostřednictvím zásuvných modulů Gramps.

	      Formáty dostupné	pro  import  jsou  grdb,  gramps-xml,  gedcom,
	      gramps-pkg  (automaticky použit pokud má SOUBOR koncovku .gpkg),
	      nebo geneweb (automaticky použit pokud má SOUBOR koncovku .gw).

	      Formáty dostupné pro export jsou gramps-xml, gedcom, gramps-pkg,
	      wft (automaticky použit pokud má SOUBOR koncovku .wft), geneweb,
	      a iso (nikdy není použit automaticky, vždy musí být specifikován
	      parametrem -f).


       **-l**     
          Vypíše seznam známých rodokmenů.


       **-u** , **--force-unlock**
	      Odemkne zamčenou databázi.


       **-O** , **--open=** *DATABÁZE*
	      Otevření *DATABÁZE* . Hodnota  musí  být  existujícím databázovým
	      adresářem,  nebo	názvem	existujícího  rodokmenu.    Pokud   na
	      příkazové  řádce nejsou žádné parametry importu nebo exportu, je
	      nad danou databází spuštěna interaktivní relace.


       **-i** , **--import=** *SOUBOR*
	      Importuje data ze SOUBORu. Pokud není specifikována databáze, je
	      použita dočasná. Ta je po ukončení gramps smazána.

	      Pokud  je  předáván  více  než jeden vstup, musí každému souboru
	      předcházet parametr -i.  Soubory jsou zpracovávány v  pořadí,  v
	      jakém  byly zadány na příkazové řádce.  Např. -i SOUBOR1 -i SOU‐
	      BOR2 a -i SOUBOR2 -i SOUBOR1 mohou vytvořit ve výsledné databázi
	      různá gramps ID.


       **-a** , **--action=** *AKCE*
	      Provedení  AKCE  nad importovanými daty. Akce jsou spuštěny poté
	      co jsou všechny importy dat úspěšně ukončeny. V tuto chvíli jsou
	      podporovány    následující    akce:    summary	(stejné   jako
	      Zprávy->Pohled->Souhrn), check (stejné  jako  Nástroje->Database
	      Processing->Kontrola  a oprava), report (vytvoří zprávu), a tool
	      (spustí nástroj zásuvného modulu).  Akce report a tool potřebují
	      v PARAMETRY zadat parametr -p .

	      PARAMETRY by měly splňovat následující kritéria:
	      Nesmí  obsahovat žádné mezery.  Pokud některý argument potřebuje
	      mezeru, musí být řetězec uzavřen v uvozovkách (držet se  syntaxe
	      příkazové  řádky).   Řetězec  možností je seznam párů název=hod‐
	      nota.  Jednotlivé páry musí být odděleny čárkami.

	      Většina  možností  nástrojů  a  zpráv  jsou   specifickými   pro
	      konkrétní  nástroj  nebo	zprávu.   Existují ale i takové, které
	      jsou společné.

	      **name=name**
	      Povinná  předvolba  určující  který  nástroj  nebo  zpráva  bude
	      spuštěna.    Pokud   zadané   name   neodpovídá  žádné  dostupné
	      funkčnosti, vypíše se chybové hlášení následované seznamem  dos‐
	      tupných nástrojů a zpráv (záleží na AKCE).

	      **show=all**
	      Vytvoří seznam názvů všech předvoleb dostupných pro danou zprávu
	      nebo nástroj.

	      **show=optionname**
	      Vypíše popis všech  funkcionalit	poskytnutých  optionname,  ale
	      také všechny přijatelné typy a hodnoty pro tuto volbu.

	      Použijte	výše  popsané  volby  pro zjištění všech možností dané
	      zprávy.


       Pokud je zadána jedna nebo více výstupních akcí, každá musí být uvozena
       předvolbou -a. Akce jsou prováděny jedna za druhou v zadaném pořadí.


       **-d** , **--debug=** *LOGGER_NAME*
	      Zapne  ladicí  výstup  pro vývoj a testování. Detaily najdete ve
	      zdrojovém kódu.

       **--version**
	      Vytiskne číslo verze gramps a skončí




**Chování**
       Pokud první parametr  příkazové	řádky  nezačíná  pomlčkou,  pokusí  se
       gramps  otevřít	soubor	s  názvem daným prvním argumentem na příkazové
       řádce a spustit interaktivní  relaci.  Zbytek  argumentů  na  příkazové
       řádce je v tomto případě ignorován.


       Pokud  je  zadán  parametr  -O,	pak  se  gramps  snaží otevřít zadanou
       databázi a pracovat s jejími daty  podle  instrukcí  dalších  parametrů
       příkazové řádky.


       S  nebo	bez  použití  parametru  -O  může  být provedeno více importů,
       exportů, případně akcí daných argumenty příkazové řádky (-i, -e a -a).


       Na pořadí parametrů -i, -e, nebo -a nezáleží.   Aktuální  pořadí  zpra‐
       cování  je  vždy:  všechny  importy (pokud jsou nějaké) -> všechny akce
       (pokud jsou nějaké) -> všechny exporty (pokud jsou  nějaké).   Parametr
       otevření musí být ale vždy první!


       Pokud  nejsou zadány -O nebo -i, gramps otevře své hlavní okno a spustí
       se v obvyklém interaktivním módu s prázdnou databází.


       Pokud nejsou zadány -e nebo -a, gramps otevře své hlavní okno a	spustí
       se  v  ovbyklém interaktnivním módu s databází vzniklou výsledkem všech
       importů.  Tato databáze je umístěna v souboru import_db.grdb v adresáři
       ~/.gramps/import.


       Chyba  vzniklá  při  importu,  exportu nebo akci bude vypsána na stdout
       (pokud se jedná o vyjímku  ošetřenou  gramps)  nebo  na	stderr	(pokud
       problém	není  ošetřen).  Pro  uložení zpráv a chyb do souboru použijte
       obvyklá přesměrování výstupů stdout a stderr příkazové řádky.


**PŘÍKLADY**
       Otevření existujícího rodokmenu a import xml souboru do něho  může  být
       proveden takto:
       
	      gramps -O 'Můj rodokmen' -i ~/db3.gramps

       To  samé,  jen  s importem do dočasné databáze a otevřením interaktivní
       relace:
       
	      gramps -i 'My Family Tree' -i ~/db3.gramps

       Import čtyř databází (jejichž formáty jsou stanoveny podle  názvů  sou‐
       borů)  a  následná  kontrola  bezchybnosti  výsledné  databáze může být
       provedena takto:
       
	      gramps -i file1.ged -i file2.tgz -i ~/db3.gramps -i file4.wft -a
	      check

       Explicitní  specifikace	formátu databází předchozího příkladu přidáním
       příslušného parametru -f za název souboru:
       
	      gramps -i file1.ged -f gedcom  -i  file2.tgz  -f	gramps-pkg  -i
	      ~/db3.gramps -f gramps-xml -i file4.wft -f wft  -a check

       Zapsání	výsledné  databáze vytvořené ze všech importů zajistí parametr
       -e (použijte -f pokud nelze uhodnout formát z názvu souboru):
       
	      gramps -i file1.ged -i file2.tgz -e ~/nový-balíček -f gramps-pkg

       Import tří databází a start interaktivní gramps relace nad výsledkem:
       
	      gramps -i file1.ged -i file2.tgz -i ~/db3.gramps

       Spuštění nástroje kontroly z příkazové řádky s výstupem na stdout:
       
	      gramps -O 'Můj rodokmen' -a tool -p name=verify

       A konečně spuštění normální interaktivní relace aplikace:
       
	      gramps


**PROMĚNNÉ PROSTŘEDÍ**
       Program kontroluje, zda jsou nastaveny následující proměnné:

       **LANG** - popisuje, který jazyk bude použit: Příklad: pro češtinu musí mít
       proměnná hodnotu cs_CZ.utf8.

       **GRAMPSHOME**  -  pokud  je  nastavena,  Gramps  použije její hodnotu jako
       adresář v němž jsou uložena nastavení a databáze.  Ve  výchozím	stavu,
       kdy  proměnná není nastavena gramps předpokládá že adresář s databázemi
       a nastavením bude vytvořen v adresáři s	uživatelským  profile  (popsán
       proměnnou prostředí HOME v Linuxu nebo USERPROFILE ve Windows 2000/XP).


**KONCEPTY**
       gramps  podporuje  systém  zásuvných modulů založených na jazyku python
       jehož prostřednictvím umožňuje přidání	import/export  modulů,	modulů
       pro  vytváření  zpráv,  nástrojů  a  zobrazovacích  filtrů bez nutnosti
       zásahu do hlavního programu.

       Dále, krom možnosti přímého tisku,  dovoluje  směřovat  výstup  také  k
       ostatním systémům a aplikacím jako např. OpenOffice.org, AbiWord, HTML,
       nebo LaTeX. Tím dává možnost přizpůsobit formát požadavku uživatelů.


**ZNÁMÉ CHYBY A OMEZENÍ**
       nejsou


**SOUBORY**

       *${PREFIX}/bin/gramps*
       
       *${PREFIX}/lib/python/dist-packages/gramps/*
       
       *${PREFIX}/share/*
       
       *${HOME}/.gramps*


**AUTOŘI**
       Donald Allingham <don@gramps-project.org>
       http://gramps-project.org/

       Originální manuálovou stránku vytvořil:
       Brandon L. Griffith <brandon@debian.org>
       pro zařazení do systému Debian GNU/Linux.

       Tuto manuálovou stránku přeložil a v současné době spravuje:
       Zdeněk Hataš <zdenek.hatas@gmail.com>


**DOKUMENTACE**
       Uživatelská dokumentace je  k  dispozici  prostřednictvím  standardního
       prohlížeče  nápovědy  GNOME  ve formě příručky Gramps. Příručka je také
       dostupná ve formátu XML jako gramps-manual.xml v  adresáři  doc/gramps-
       manual/$LANG v oficiální distribuci zdrojového kódu.

       Dokumentace  pro  vývojáře  je  k  dispozici  na  webu
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers



Leden 2012			     3.4.0			     gramps(1)
