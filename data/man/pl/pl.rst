Polish
=======

gramps(1)			     3.4.0			     gramps(1)



**NAME**
       gramps - Genealogical Research and Analysis Management Programming Sys‐
       tem.
       (w wolnym tłumaczeniu: System Wspomagania Badań Genealogicznych i  Pro‐
       gramowego Zarządzania Tą Informacją)


**SYNOPSIS**
       gramps	[-?|--help]  [--usage]	[--version]  [-l]  [-u|--force-unlock]
       [-O|--open=  BAZA_DANYCH  [-f|--format=	FORMAT]]  [-i|--import=   PLIK
       [-f|--format=   FORMAT]]   [-i|--import=   ...]	  [-e|--export=   PLIK
       [-f|--format= FORMAT]] [-a|--action= AKCJA] [-p|--options= CIĄG_OPCJI]]
       [ PLIK ] [--version]


**OPIS**
       Gramps  jest wolnym, darmowym programem genealogicznym OpenSource. Jest
       napisany w Python, przy użyciu interfejsu GTK+/GNOME.  Dla każdego, kto
       wcześniej  używał  innego  programu  genealogicznego  (np.  Family Tree
       Maker (TM),  Personal Ancestral Files (TM), lub	GNU  Geneweb),	zapoz‐
       nanie  się  z  interfejsem  Gramps'a  będzie  natychmiastowe.   Program
       obsługuje także import i eksport w popularnym  formacie	GEDCOM,  który
       jest używany przez większość programów genealogicznych na świecie.


**OPCJE**
       **gramps** *PLIK*
	      Kiedy *PLIK* jest  podany  (bez  żadnych flag) jako nazwa drzewa
	      rodzinnego albo nazwa katalogu z drzewem, to wybrane drzewo jest
	      otwierane  i  rozpoczynana  jest	sesja interaktywna. Jeśli PLIK
	      jest formatem rozpoznawanym przez Gramps, to tworzone jest puste
	      drzewo,  którego nazwa bazuje na nazwie PLIKU i dane są do niego
	      importowane. Pozostałe  opcje  są  wtedy	ignorowane.   Jest  to
	      sposób  na  używanie  programu  jako  uchwytu obsługującego dane
	      genealogiczne, np. w przeglądarce internetowej. Takie  wywołanie
	      akceptuje każdy format natywny dla grampsa, zobacz poniżej.


       **-f** , **--format=** *FORMAT*
	      Jawne  określenie formatu PLIKU przez poprzedzenie opcji -i, lub
	      -e.  Jeśli opcja -f nie jest podana dla żadnego PLIKU, to format
	      pliku jest określany na podstawie rozszerzenia albo typu MIME.

	      Dostępne formaty wyjściowe to:
	      gramps-xml (używany jeśli PLIK kończy się na .gramps),
	      gedcom (przyjmowany jeśli PLIK kończy się na .ged),
	      lub  dowolny  plik  eksportu  obsługiwany  przez	system wtyczek
	      Gramps.

	      Formaty dostępne dla importu to: grdb, gramps-xml, gedcom,
	      gramps-pkg (przyjmowany jeśli PLIK kończy się na .gpkg),
	      oraz geneweb (przyjmowany jeśli PLIK ma rozszerzenie .gw).

	      Formats  dostępne   dla	eksportu   to:	 gramps-xml,   gedcom,
	      gramps-pkg,  wft	(jeśli rozszerzenie PLIKU to .wft), geneweb, i
	      iso (używany tylko, jeśli jawnie określony przez parametr -f ).


       **-l**     
          Wyświetla listę dosŧępnych drzew genealogicznych.


       **-u** , **--force-unlock**
	      Wymusza odblokowanie bazy danych.


       **-O** , **--open=** *BAZA_DANYCH*
	      Otwiera *BAZĘ_DANYCH* , która musi istnieć w katalogu baz  lub  być
	      nazwą istniejącego drzewa rodzinnego. Jeśli nie podano akcji, to
	      opcje eksportu albo importu  są  wykonywane,  a  następnie  jest
	      uruchamiana sesja interaktywna z otwarciem wybranej bazy.


       **-i** , **--import=** *PLIK*
	      Importuje  dane  z *PLIKU* . Jeśli  nie określono bazy danych, to
	      tworzona jest tymczasowa baza kasowana po zamknięciu programu.

	      Kiedy podany jest więcej niż jeden plik do importu, to  każdy  z
	      nich musi być poprzedzony flagą -i. Pliki są importowane w kole‐
	      jności podanej w linii poleceń, np.:  -i PLIK1 -i PLIK2 oraz  -i
	      PLIK2  -i  PLIK1 mogą utworzyć inne identyfikatory (gramps ID) w
	      bazie wynikowej.


       **-e** , **--export=** *PLIK*
	      Eksportuje dane do *PLIKU* . Dla formatu iso, PLIK natomiast  nazwą
	      katalogu,  do którego baza danych gramps zostanie zapisana.  Dla
	      gramps-xml, gedcom, wft, gramps-pkg,  oraz  geneweb,  PLIK  jest
	      nazwą pliku wynikowego.

	      Kiedy  więcej  niż  jeden plik wyjściowy jest podany, każdy musi
	      być poprzedzony flagą  -e.  Pliki  będą  zapisywane  kolejno,  w
	      podanej przez parametry kolejności.


       **-a** , **--action=** *AKCJA*
	      Wykonuje	AKCJĘ  na  zaimportowanych  danych.  Działanie to jest
	      wykonywane dopiero, gdy wszystkie określone importy zakończą się
	      powodzeniem. Aktualnie dostępne akcje to:
	      summary  (taka  sama  jak  Raporty->Wyświetl->Podsumowanie  bazy
	      danych),
	      check  (tożsama  z  Narzędzia->Naprawa  bazy  danych->Sprawdź  i
	      napraw bazę),
	      report (generuje raport), oraz
	      tool  (uruchamia	narzędzie/wtyczkę).  Zarówno report jak i tool
	      wymagają podania CIĄGU_OPCJI poprzedzonego flagą -p ).

	      CIĄG_OPCJI powinien spełniać następujące warunki:
	      Nie może zawierać spacji.   Jeśli  niektóre  argumenty  wymagają
	      spacji,  ciąg  powinien  być enkapsulowany w znakach cudzysłowu,
	      (zobacz składnię powłoki). Ciąg opcji jest  listą  parametrów  z
	      nazwą i wartością oddzielonymi znakiem równości. Kolejne parame‐
	      try muszą być oddzielone od siebie znakiem przecinka.

	      Większość opcji dla raportów czy narzędzi jest  specyficzna  dla
	      konkretnej opcji, jednak część z opcji jest wspólna, szczególnie
	      dla raportów.

	      **name=nazwa**
	      Opcja wymagana, określający który raport	czy  narzędzie	będzie
	      uruchamiane.   Jeśli  podana wartość nazwy nie pasuje do żadnego
	      dostępnego raportu czy narzędzia, zostanie wyświetlony komunikat
	      o   błędzie   oraz  lista  dostępnych  raportów  albo  opcji  (w
	      zależności od wartości parametru AKCJA).

	      **show=all**
	      Wyświetla listę wszystkich nazw dostępnych opcji wraz z  krótkim
	      opisem dla danego raportu albo narzędzia.

	      **show=nazwa_opcji**
	      Wyświetla opis funkcji udostępnianej przez daną nazwę_opcji, jak
	      również listę parametrów, które akceptuje dana opcja.

	      Używając powyższych opcji  jesteś  w  stanie  dowiedzieć	się  o
	      wszystkich możliwościach danego raportu.


       Kiedy  więcej  niż  jeden  akcja  wyjściowa jest podana, każda musi być
       poprzedzona flagą -a. Akcje są wykonywane jedna	po  drugiej,  w  kole‐
       jności w jakiej występują w linii poleceń.


       **-d** , **--debug=** *NAZWA_LOGGERA*
	      Włącza   logi   debuggowania   dla   celów  programistycznych  i
	      testowych. Zobacz do kodu źródłowego po szczegóły.


       **--version**
	      Wyświetla wersję programu i kończy działanie.


**Działanie**
       Jeśli  pierwszy	argument nie rozpoczyna się znakiem myślnik, (nie jest
       flagą), to gramps będzie próbował otworzyć plik podany  przez  pierwszy
       argument, a następnie sesję interaktywną a pozostałą część parametrów w
       linii poleceń zignoruje.


       Jeśli podana jest flaga -O, będzie próbował otworzyć podaną bazę i pra‐
       cować  na danych w niej zawartych realizując podane później polecenia z
       linii komend.


       Z flagą -O czy bez, może  występować  wiele  importów,  eksportów  oraz
       akcji określonych za pomocą flag -i, -e, oraz -a .


       Kolejność  podawania opcji -i, -e, czy -a nie ma znaczenia.  Wykonywane
       są one zawsze w kolejności: wszystkie importy (jeśli podane) ->	wszys‐
       tkie  akcje  (jeśli  podane)  ->  wszystkie eksporty (jeśli podane) Ale
       otwarcie bazy zawsze musi być na pierwszym parametrem !


       Jeśli nie podano opcji -O lub -i, gramps uruchomi swoje główne  okno  i
       rozpocznie  normalną  sesję  interaktywną z pustą bazą danych (ponieważ
       nie zdołał przetworzyć do niej żadnych danych).


       Jeśli nie podano opcji-e albo -a gramps uruchomi swoje  głowne  okno  i
       rozpocznie  normalną  sesję interaktywną z bazą będącą wynikiem wszyst‐
       kich importów. Ta baza będzie znajdować się w  pliku  import_db.grdb  w
       katalogu ~/.gramps/import.


       Błąd podczas importu, eksportu albo dowolnej akcji będzie przekierowany
       na stdout (jeśli wyjątek  zostanie  obsłużony  przez  gramps)  albo  na
       stderr  (jeśli  nie  jest  obsłużony).  Użyj standardowych przekierowań
       strumieni stdout oraz stderr jeśli chcesz zapisać wyświetlane  informa‐
       cje i błędy do pliku.


**PRZYKŁADY**
       Aby  otworzyć  istniejące drzewo rodzinne i zaimportować dane do niego,
       można wpisać:
       
	      gramps -O 'Moje drzewo' -i ~/db3.gramps

       Powyższa opcja otwiera istniejące drzewo, ale gdy chcesz zrobić wykonać
       taką samą  akcję  tworząc tymczasowe drzewo: wystarczy wpisać: 
          
          gramps -i 'Moje drzewo' -i ~/db3.gramps

       Aby zaimportować cztery bazy (których formaty zostaną określone na pod‐
       stawie ich  nazw)  i następnie sprawdić powstałą bazę pod kątem błędów,
       należy wpisać: 
          
          gramps -i plik1.ged -i plik2.tgz -i  ~/db3.gramps
	      -i plik4.wft -a check

       Aby jawnie określić formaty w powyższym przykładzie, należy dodać nazwy
       plików z odpowiednimi opcjami -f options: 
       
       gramps -i plik1.ged -f gedcom -i  plik2.tgz  -f  gramps-pkg  -i  
       ~/db3.gramps -f gramps-xml -i plik4.wft -f wft -a check

       Aby zachować bazę z wynikami wszystkich importów, należy dodać flagę -e
       (należy użyć -f jeśli nazwa pliku nie pozwala gramps'owi na odgadnięcie
       formatu wyjściowego):
       
	      gramps -i plik1.ged -i plik2.tgz -e ~/nowy-pakiet -f gramps-pkg

       W celu zaimportwania trzech baz i  rozpoczęcia  sesji  interaktywnej  z
       wynikiem importu należy użyć polecenia podobnego do poniższego: 
       
          gramps -i plik1.ged -i plik22.tgz -i ~/db3.gramps

       Aby uruchomić narzędzie weryfikacji z linii poleceń i wyświetlić wyniki
       na stdout: 
       
          gramps -O 'Moje drzewo' -a tool -p name=verify

       Zawsze można też po prostu uruchomić sesję interaktywną wpisująć:
       
	      gramps


**ZMIENNE ŚRODOWISKOWE**

       Program	sprawdza  w systemie istnienie i wartości następujących zmien‐
       nych:

       **LANG** - określa ustawienia, jaki język zostanie wybrany.	Np.: polski to
       pl_PL.UTF-8.

       **GRAMPSHOME**  -  określa  folder, w którym będzie zapisywane ustawienia i
       bazy programu. Domyślnie jest on nieustawiony, a program przyjmuje,  że
       katalog z danymi zostanie utworzony w profilu użytkownika (zmienna HOME
       pod Linuxem albo USERPROFILE pod Windows 2000/XP).



**KONCEPCJA**
       Obsługa systemu rozszerzeń bazującego  na  pythonie,  pozwalającego  na
       dodawanie  formatów  importu  i eksportu zapisów, generatorów raportów,
       narzędzi i filtrów wyświetlania bez modyfikowania głównego programu

       Dodatkowo oprócz generowania standardowego wyjścia na drukarkę, raporty
       mogą  także  być  generowane  dla  innch systemów i do innych formatów,
       takich jak: OpenOffice.org, AbiWord,  HTML,  lub  LaTeX	aby  umożliwić
       użytkownikm wybór formatu wyjściowego w zależności od ich potrzeb.


**ZNANE BŁĘDY I OGRANICZENIA**
       Prawdopodobne. Lista błędów i propozycji znajduje się na: 
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers .


**PLIKI**
       
       *${PREFIX}/bin/gramps*
       
       *${PREFIX}/lib/python/dist-packages/gramps/*
       
       *${PREFIX}/share/*
       
       *${HOME}/.gramps (jeśli nie użyta została  zmienna  środowiskowa	GRAMP‐
       SHOME)*


**AUTORZY**
       Donald Allingham <don@gramps-project.org>
       http://gramps-project.org/

       Ta strona man jest tłumaczeniem strony man napisanej przez:
       Brandon L. Griffith <brandon@debian.org>
       dla systemu Debian GNU/Linux.

       Ta strona aktualnie jest pod opeką:
       Projekt Gramps<xxx@gramps-project.org>
       Tłumaczenie na polski: Łukasz Rymarczyk <yenidai@poczta.onet.pl>


**DOCUMENTATION**
       Dokumentacja użytkownika jest dostępna poprzez standardową przeglądarkę.

       Dokumentacja  dla  programistów	jest  dostępna	na  stronie  projektu:
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers 



January 2008			     4.0.0			     gramps(1)
