# Initialize GRAMPS Django site

update: grampsdb/fixtures/initial_data.json
	PYTHONPATH=../../../src python manage.py syncdb

grampsdb/fixtures/initial_data.json: 
	PYTHONPATH=../../../src python init.py > grampsdb/fixtures/initial_data.json

init_gramps:
	PYTHONPATH=../../../src python init_gramps.py # clear primary and secondary tables

run:
	PYTHONPATH=../../../src python manage.py runserver

sql:
	PYTHONPATH=../../../src python manage.py sqlall > gramps_sql.txt

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
	python manage.py graph_models grampsdb -i Attribute,Datamap,Name,Lds,Markup,Address,Location,Url -o docs/secondary-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Markup,Address,Location,Url -o docs/prim-sec-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Markup,Address,Location,Url -o docs/prim-sec-tables.png
	python manage.py graph_models grampsdb -i Person,Family,Source,Event,Repository,Place,Media,Note,Attribute,Datamap,Name,Lds,Markup,Address,Location,Url,NoteRef,SourceRef,EventRef,RepositoryRef,PersonRef,ChildRef,MediaRef -o docs/prim-sec-ref-tables.png


clean:
	rm -f sqlite.db
	rm -f *~ *.pyc *.pyo
	rm -f grampsdb/fixtures/initial_data.json
