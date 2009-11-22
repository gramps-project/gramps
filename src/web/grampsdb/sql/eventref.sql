CREATE INDEX grampsdb_name_surname 
       ON grampsdb_name (surname, first_name);

CREATE INDEX grampsdb_eventref_object_id_object_type_id 
       ON grampsdb_eventref (object_id, object_type_id);
