French
=======

gramps(1)                @VERSION@               gramps(1)


**NOM**
       gramps - Gramps est une application de généalogie. Gramps est
       l'acronyme de Genealogical Research and Analysis Management Programming
       System (Systeme de Programmation pour Recherche, Analyse et Gestion de
       données généalogiques)


**SYNOPSIS**
       **gramps** [**-?** | **--help**] [**--usage**] [**--version**]
       [**-l**] [**-L**] [**-u** | **--force-unlock**] [**-O** | **--open=** *BASE_DE_DONNEES*]
       [**-f** | **--format=** *FORMAT*] [**-i** | **--import=** *FICHIER*]
       [**-e** | **--export=** *FICHIER*] [**--remove=** *FAMILY_TREE_PATTERN*]
       [**-a** | **--action=** *ACTION* [*-p* | **--options=** *CHAÎNE‐
       OPTION*]] [*FICHIER*] [**--version**]


**DESCRIPTION**
       Gramps est un programme Libre/OpenSource de généalogie. Il est écrit en
       python, et utilise une interface GTK+/GNOME. Gramps est semblable à
       d'autres programmes de généalogie tel  que  Family Tree Maker (FTM),
       Personal Ancestral Files, ou le programme GNU Geneweb. Il peut
       importer/exporter le format le plus utilisé par les autres logiciels de
       généalogie : GEDCOM.


**OPTIONS**
       **gramps** *FICHIER*
          Si *FICHIER* est désigné (sans autres commandes) comme arbre
          familial ou comme répertoire d'arbre familial, alors une session
          interactive est ouverte. Si *FICHIER* est un format de fichier
          supporté par Gramps, une base vide est créée  dont le nom est
          celui du *FICHIER* et les données y seront importées. Les autres
          options sont ignorées. Ce type de lancement permet d'utiliser
          gramps  pour manipuler des données comme dans un navigateur web.
          Les formats natifs de gramps sont acceptés, voir ci-dessous.


       **-f** , **--format=** *FORMAT*
          Le format spécifique du *FICHIER* est précédé par les arguments
          **-i** , ou **-e** . Si l'option **-f** n'est pas donnée pour le *FICHIER* ,
          alors le format sera celui de l'extension ou du type-MIME.

          Les formats de sortie disponibles sont **gramps-xml** (deviné si
          *FICHIER* se termine par **.gramps** ), et **gedcom** (deviné si *FICHIER* se
          termine  par **.ged** ), ou tout autre fichier d'exportation
          disponible dans le système de plugin Gramps.

          Les formats disponibles pour l'importation sont  **grdb** ,
          **gramps-xml** , **gedcom** , **gramps-pkg** (deviné si *FICHIER* se termine par
          **.gpkg** ), et **geneweb** (deviné si *FICHIER* se termine par **.gw** ).

          Les formats disponibles pour l'exportation sont **gramps-xml** , **ged‐
          com** , **gramps-pkg** , **wft** (deviné si *FICHIER* se termine par **.wft** ),
          **geneweb** .


       **-l**
          Imprime une liste des arbres familiaux disponibles.


       **-u** , **--force-unlock**
          Débloquer une base de données verrouillée.


       **-O** , **--open=** *BASE_DE_DONNEES*
          Ouvrir une *BASE_DE_DONNEES* qui doit être une base présente dans
          le répertoire des bases ou le nom d'un arbre familial existant.
          Si aucune action n'est définie, les options d'import ou d'export
          sont données par la ligne de commande puis une session interactive
          est ouverte, utilisant cette base de données.

          Seulement une base peut être ouverte. Si vous utilisez plusieurs
          sources, vous devez utiliser l'option d'import.


       **-i** , **--import=** *FICHIER*
          Importer des données depuis un *FICHIER* . Si vous n'avez pas
          spécifié de base de données, alors une base de données vide
          est utilisée.

          Quand plus d'un fichier doit être importé, chacun doit être
          précédé par la commande **-i** . Ces fichiers sont importés dans le
          même ordre,  **-i** *FICHIER1* **-i** *FICHIER2* et **-i** *FICHIER2* **-i**
          *FICHIER1* vont tous les deux produire différents IDs gramps.


       **-e** , **--export=** *FICHIER*
          Exporter des données dans un *FICHIER* . Pour les fichiers **gramps-xml**
          , **gedcom** , **wft** , **gramps-pkg** , et **geneweb** , le
          *FICHIER* est le nom du fichier de sortie.

          Quand plus d'un fichier doit être exporté, chacun doit être
          précédé par la commande **-e** . Ces fichiers sont importés dans le
          même ordre.


       **-a** , **--action=** *ACTION*
          Accomplir une *ACTION* sur les données importées. C'est effectué à
          la fin de l'importation. Les actions possibles sont **summary**
          (comme le rapport -> Afficher -> Statistiques sur la base),
          **check** (comme l'outil -> Réparation de la base -> Vérifier et
          réparer), **report** (produit un rapport) et **tool** (utilise un
          outil), ces derniers ont besoin de *OPTION* précédé par la commande -p.

          L' *OPTION* doit satisfaire ces conditions:
          Il ne doit pas y avoir d'espace. Si certains arguments doivent
          utiliser des espaces, la chaîne doit être encadrée par des
          guillemets. Les options vont par paire nom et valeur. Une
          paire est séparée par un signe égal. Différentes paires sont
          séparées par une virgule.

          La plupart des options sont spécifiques à chaque rapport. Même
          s'il existe des options communes.

          **name=name**
          Cette option est obligatoire, elle détermine quel rapport ou
          outil sera utilisé. Si le name saisi ne correspond à aucun
          module disponible, un message d'erreur sera ajouté.

          **show=all**
          Cette option produit une liste avec les noms des options
          disponibles pour un rapport donné.

          **show=optionname**
          Cette option affiche une description de toutes les fonctionnalités
          proposées par optionname, aussi bien les types que les valeurs pour une option.

          Utiliser les options ci-dessus pour trouver tout sur un rapport
          choisi.


       Quand plus d'une action doit être effectuée, chacune doit être précédée
       par la commande **-a** . Les actions seront réalisées une à une, dans
       l'ordre spécifié.


       **-d** , **--debug=** *NOM_LOGGER*
          Permet les logs de debug pour le développement et les tests.
          Regarder le code source pour les détails.

       **--version**
          Imprime le numéro de version pour gramps puis quitte.




**Opération**
       Si le premie argument de la ligne de commande ne commence pas par un
       tiret (i.e. pas d'instruction), gramps va essayer d'ouvrir la base de
       données avec le nom donné par le premier argument et démarrer une ses‐
       sion interactive, en ignorant le reste de la ligne de commande.


       Si la commande **-O** est notée, alors gramps va essayer le fichier défini
       et va travailler avec ses données, comme pour les autres paramètres de
       la ligne de commande.


       Avec ou sans la commande **-O** , il peut y avoir plusieurs imports,
       exports, et actions dans la ligne de commande **-i** , **-e** , et **-a** .


       L'ordre des options **-i** , **-e** , ou **-a** n'a pas de sens. L'ordre actuel est
       toujours : imports -> actions -> exports. Mais l'ouverture doit toujours
       être la première !


       Si aucune option **-O** ou **-i** n'est donnée, gramps lancera sa propre
       fenêtre et demarrera avec une base vide, puisqu'il n'y a pas données.


       Si aucune option **-e** ou **-a** n'est donnée, gramps lancera sa propre
       fenêtre et démarrera avec la base de données issue de tout les imports.
       Cette base sera **import_db.grdb** dans le répertoire **~/.gramps/import**.


       Les erreurs  rencontrées lors d'importation, d'exportation, ou d'action, seront
       mémorisées en *stdout* (si elles sont le fait de la manipulation par
       gramps) ou en *stderr* (si elles ne sont pas le fait d'une manipulation).
       Utilisez les shell de redirection de *stdout* et *stderr* pour sauver
       les messages et les erreurs dans les fichiers.


**EXEMPLES**
       Pour ouvrir un arbre familial et y importer un fichier XML, on peut
       saisir:

          **gramps -O** *'Mon Arbre Familial'* **-i** *~/db3.gramps*

       Ceci ouvre un arbre familial, pour faire la même chose, mais importer
       dans un arbre familial temporaire et démarrer une session interactive,
       on peut saisir :

          **gramps -i** *'Mon Arbre Familial'* **-i** *~/db3.gramps*

       Lecture de quatre bases de données dont les formats peuvent être
       devinés d'après les noms, puis vérification des données:

          **gramps -i** *file1.ged* **-i** *file2.tgz* **-i** *~/db3.gramps*
          **-i** *file4.wft* **-a** *check*

       Si vous voulez préciser lesformats de fichiers dans l'exemple ci-
       dessus, complétez les noms de fichiers par les options -f appropriées:

          **gramps -i** *file1.ged* **-f** *gedcom* **-i** *file2.tgz* **-f**
          *gramps-pkg* **-i** *~/db3.gramps* **-f** *gramps-xml* **-i** *file4.wft*
          **-f** *wft* **-a** *check*

       Pour enregistrer le résultat des lectures, donnez l'option **-e**
       (utiliser -f si le nom de fichier ne permet pas à gramps de deviner le
       format):

          **gramps -i** *file1.ged* **-i** *file2.tgz* **-e** *~/new-package*
          **-f** *gramps-pkg*

       Pour lire trois ensembles de données puis lancer une session
       interactive de gramps sur le tout :

          **gramps -i** *file1.ged* **-i** *file2.tgz* **-i** *~/db3.gramps*

       Pour lancer l'outil de vérification de la base de données depuis la
       ligne de commande et obtenir le résultat :

          **gramps -O** *'My Family Tree'* **-a** *tool* **-p name=** *verify*

       Enfin, pour lancer une session interactive normale, entrer :

          **gramps**


**VARIABLES D'ENVIRONMENT**
       Le programme vérifie si ces variables d'environnement sont déclarées:

       **LANG** - décrit, quelle langue est utilisée: Ex.: pour le français on
       peut définir fr_FR.UTF-8.

       **GRAMPSHOME**  - si  défini, force Gramps à utiliser un répertoire
       spécifique pour y conserver ses préférences et bases de données. Par
       défaut, cette variable n'est pas active et Gramps sait que les options
       et bases de données doivent être créées dans le répertoire par défaut
       de l'utilisateur (la variable d'environnement HOME pour Linux ou USER‐
       PROFILE pour Windows 2000/XP).


**CONCEPTS**
       Gramps est un système basé sur le support de plugin-python, permettant
       d'importer et d'exporter, la saisie, générer des rapports, des outils,
       et afficher des filtres pouvant être ajoutés sans modifier le programme.

       Par ailleurs, gramps permet la génération directe : impression, rap‐
       ports avec sortie vers d'autres formats, comme *LibreOffice.org* ,
       *HTML* , ou *LaTeX* pour permettre à l'utilisateur de choisir selon ses
       besoins


**BUGS CONNUS ET LIMITATIONS**

**FICHIERS**

       *${PREFIX}/bin/gramps*

       *${PREFIX}/lib/python3/dist-packages/gramps/*

       *${PREFIX}/share/*

       *${HOME}/.gramps*


**AUTEURS**
       Donald Allingham <don@gramps-project.org>
       http://gramps-project.org/

       Cette page man a d'abord été écrite par :
       Brandon L. Griffith <brandon@debian.org>
       pour Debian GNU/Linux système.

       Cette page man est maintenue par :
       Gramps project <xxx@gramps-project.org>

       La traduction française :
       Jérôme Rapinat <romjerome@yahoo.fr>


**DOCUMENTATION**
       La documentation-utilisateur est disponible par un navigateur
       standard sous la forme du manuel Gramps.

       La documentation pour développeur est disponible sur le site
       http://www.gramps-project.org/wiki/index.php?title=Portal:Developers .



gramps(1)                 @VERSION@               gramps(1)
