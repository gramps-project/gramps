from gramps.gen.db.utils import open_database
from gramps.gen.db.conversion_tools import convert_21

# 1. Prepare: create a database named "Example" in version 20
#    containing the blob data

# 2. Open the database in latest Gramps to convert the database
#    to version 21

db = open_database("Example")

# This is a version 21 database

# But we tell it to use the blob data:

db.set_serializer("blob")

for table_name in db._get_table_func():
    print("Testing %s..." % table_name)
    get_array_from_handle = db._get_table_func(table_name, "raw_func")
    iter_objects = db._get_table_func(table_name, "iter_func")

    for obj in iter_objects():
        # We convert the object into the JSON dicts:
        json_data = db.serializer.object_to_data(obj)

        # We get the blob array:
        array = get_array_from_handle(obj.handle)

        # We convert the array to JSON dict using the
        # conversion code to convert array directly to
        # dict

        convert_data = convert_21(table_name, array)

        # Now we make sure they are identical in types
        # and values:
        assert convert_data == json_data

db.close()
