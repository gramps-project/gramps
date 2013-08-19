# Initialize GRAMPS Django site

update: grampsdb/fixtures/initial_data.json
	PYTHONPATH=../.. python manage.py syncdb --noinput
	PYTHONPATH=../.. python manage.py createsuperuser --username=admin --email=bugs@gramps-project.org
	PYTHONPATH=../.. python manage.py createsuperuser --username=admin1 --email=bugs@gramps-project.org

grampsdb/fixtures/initial_data.json: init.py
	mkdir -p grampsdb/fixtures
	PYTHONPATH=../.. python init.py > grampsdb/fixtures/initial_data.json

init_gramps:
	PYTHONPATH=../.. python init_gramps.py # clear primary and secondary tables

run:
	PYTHONPATH=../.. python manage.py runserver

sql:
	PYTHONPATH=../.. python manage.py sqlall > gramps-sql.sql

dump:
	echo ".dump" | sqlite3 sqlite.db > gramps-data.sql

load:
	sqlite3 sqlite.db < gramps-data.sql

superusers:
	PYTHONPATH=../.. python manage.py createsuperuser --username=admin --email=bugs@gramps-project.org
	PYTHONPATH=../.. python manage.py createsuperuser --username=admin1 --email=bugs@gramps-project.org

backup:
	PYTHONPATH=../.. python manage.py dumpdata > backup.json

restore: empty
	PYTHONPATH=../.. python manage.py loaddata backup.json

initial_data: 
	PYTHONPATH=../.. python manage.py loaddata grampsdb/fixtures/initial_data.json

docs:
	mkdir -p docs
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note -o docs/primary-tables.png
	python manage.py graph_models grampsdb -i Note -o docs/note-table.png
	python manage.py graph_models grampsdb -i Media -o docs/media-table.png
	python manage.py graph_models grampsdb -i Place -o docs/place-table.png
	python manage.py graph_models grampsdb -i Repository -o docs/repository-table.png
	python manage.py graph_models grampsdb -i Event -o docs/event-table.png
	python manage.py graph_models grampsdb -i Source -o docs/source-table.png
	python manage.py graph_models grampsdb -i Family -o docs/family-table.png
	python manage.py graph_models grampsdb -i Person -o docs/person-table.png
	python manage.py graph_models grampsdb -o docs/all-tables.png
	python manage.py graph_models grampsdb -i Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/secondary-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/prim-sec-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url -o docs/prim-sec-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Tag,Address,Location,Url,NoteRef,SourceRef,EventRef,RepositoryRef,PersonRef,ChildRef,MediaRef -o docs/prim-sec-ref-tables.png

make-empty:
	echo ".dump" | sqlite3 sqlite.db > empty.sql

empty:
	rm -f sqlite.db
	sqlite3 sqlite.db < empty.sql

example:
	rm -f sqlite.db
	sqlite3 sqlite.db < example.sql

clean:
	rm -f sqlite.db
	rm -f *~ *.pyc *.pyo
	rm -f grampsdb/fixtures/initial_data.json
