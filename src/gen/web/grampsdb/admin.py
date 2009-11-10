from gen.web.grampsdb.models import *
from django.contrib import admin

for type_name in get_tables("all"):
    admin.site.register(type_name[1])

