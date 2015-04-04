**UNSTABLE** package for testing.

This webapp, is a web-based application that runs in your browser, and requires a server.

Many Gramps users would like to collaborate or share their genealogy data on the web. 
The main focus of this Gramps-based webapp is collaboration, allow users to easily move their genealogy data to the web to be seen, and edited with proper login and permissions, in a live, collaborative environment. 

A prototype is on-line at http://gramps-connect.org/

**Requires**
Django   (version 1.7 supported until October 2015) (version 1.8 LTS supported until April 2018) ( https://www.djangoproject.com/ )

**Webapp**

- 'gramps-webapp' packages are in progress...

For **Testing only**.

See https://www.gramps-project.org/wiki/index.php?title=Gramps-Connect for more details.

**Some commands**

$ cd /usr/lib/python3.4/dist-packages/gramps/webapp
$ python manage.py help
$ sudo make

# Initialize Gramps Django site

PYTHON=GRAMPS_RESOURCES=../.. PYTHONPATH=../.. python3.4


- update: grampsdb/fixtures/initial_data.json
 $(PYTHON) manage.py syncdb --noinput
 $(PYTHON) manage.py createsuperuser --username=admin --email=bugs@gramps-project.org
 $(PYTHON) manage.py createsuperuser --username=admin1 --email=bugs@gramps-project.org


- grampsdb/fixtures/initial_data.json: init.py
 mkdir -p grampsdb/fixtures
 $(PYTHON) init.py > grampsdb/fixtures/initial_data.json


- init_gramps:
 $(PYTHON) init_gramps.py # clear primary and secondary tables


- run:
 $(PYTHON) manage.py runserver


- sql:
 $(PYTHON) manage.py sqlall > gramps-sql.sql

- dump:
 echo ".dump" | sqlite3 sqlite.db > gramps-data.sql


- load:
 sqlite3 sqlite.db < gramps-data.sql


- superusers:
 $(PYTHON) manage.py createsuperuser --username=admin --email=bugs@gramps-project.org
 $(PYTHON) manage.py createsuperuser --username=admin1 --email=bugs@gramps-project.org


- backup:
 $(PYTHON) manage.py dumpdata > backup.json


- restore: empty
 $(PYTHON) manage.py loaddata backup.json


- initial_data: 
 $(PYTHON) manage.py loaddata grampsdb/fixtures/initial_data.json


- docs:
 mkdir -p docs
 $(PYTHON) graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note -o docs/primary-tables.png
 $(PYTHON) graph_models grampsdb -i Note -o docs/note-table.png
 $(PYTHON) graph_models grampsdb -i Media -o docs/media-table.png
 $(PYTHON) graph_models grampsdb -i Place -o docs/place-table.png
 $(PYTHON) graph_models grampsdb -i Repository -o docs/repository-table.png
 $(PYTHON) graph_models grampsdb -i Event -o docs/event-table.png
 $(PYTHON) graph_models grampsdb -i Source -o docs/source-table.png
 $(PYTHON) graph_models grampsdb -i Family -o docs/family-table.png
 $(PYTHON) graph_models grampsdb -i Person -o docs/person-table.png
 $(PYTHON) graph_models grampsdb -o docs/all-tables.png
 $(PYTHON) graph_models grampsdb -i Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/secondary-tables.png
 $(PYTHON) graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/prim-sec-tables.png
 $(PYTHON) graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/prim-sec-tables.png
 $(PYTHON) graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url,NoteRef,SourceRef,EventRef,RepositoryRef,PersonRef,ChildRef,MediaRef -o docs/prim-sec-ref-tables.png


- make-empty:
 echo ".dump" | sqlite3 sqlite.db > empty.sql


- empty:
 rm -f sqlite.db
 sqlite3 sqlite.db < empty.sql


- example:
 rm -f sqlite.db
 sqlite3 sqlite.db < example.sql


- clean:
 rm -f sqlite.db
 rm -f *~ *.pyc *.pyo
 rm -f grampsdb/fixtures/initial_data.json
