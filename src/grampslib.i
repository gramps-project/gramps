%module grampslib
%{
#include <stdio.h>
#include <stdlib.h>
#include <libgnomevfs/gnome-vfs-application-registry.h>
GList *gnome_vfs_get_registered_mime_types(void);
void gnome_vfs_mime_registered_mime_type_list_free(GList*);
%}

extern const char* gnome_vfs_mime_get_icon(const char *);
extern const char* gnome_vfs_mime_type_from_name(const char* );
extern const char* gnome_vfs_mime_get_description(const char*);
extern const char* gnome_vfs_mime_get_value(const char*,const char*);

%inline %{
const char* default_application_name(const char* type) {

	GList *node;
	char* value;
	char* retval = NULL;

	GList *s = gnome_vfs_get_registered_mime_types();

	for (node = g_list_first(s); node != NULL; node = g_list_next(node)) {
		if (!strcmp((char*)node->data,type)) {
			GnomeVFSMimeApplication *a = gnome_vfs_mime_get_default_application(type);
			if (a) {
				retval = a->name;
				break;
			}
		}	
	}
	gnome_vfs_mime_registered_mime_type_list_free(s);
	return retval;
}

const char* default_application_command(const char* type) {

	GList *node;
	char* value;
	char* retval = NULL;

	GList *s = gnome_vfs_get_registered_mime_types();

	for (node = g_list_first(s); node != NULL; node = g_list_next(node)) {
		if (!strcmp((char*)node->data,type)) {
			GnomeVFSMimeApplication *a = gnome_vfs_mime_get_default_application(type);
			if (a) {
				retval = a->command;
				break;
			}
		}	
	}
	gnome_vfs_mime_registered_mime_type_list_free(s);
	return retval;
}

%}
