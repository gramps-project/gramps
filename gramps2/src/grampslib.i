%module grampslib
%{
#include <libgnomevfs/gnome-vfs-application-registry.h>
%}

extern const char* gnome_vfs_mime_get_icon(const char *);
extern const char* gnome_vfs_mime_type_from_name(const char* );
extern const char* gnome_vfs_mime_get_description(const char*);
extern const char* gnome_vfs_mime_get_value(const char*,const char*);

%inline %{
const char* default_application_name(const char* type) {
	GnomeVFSMimeApplication *a = gnome_vfs_mime_get_default_application(type);
	if (a) {
		return a->name;
	} else {
		return (char*) NULL;
	}
}

const char* default_application_command(const char* type) {
	GnomeVFSMimeApplication *a = gnome_vfs_mime_get_default_application(type);
	if (a) {
		return a->command;
	} else {
		return (char*) NULL;
	}	
}

%}
