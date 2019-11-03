"""
Web Relations Tree.

This plugin generates HTML page using HTML, JavaScript and CSS templates
from https://github.com/tuxofil/family-tree

Generates HTML page with interactive SVG picture, showing all
ancestors and all descendants of selected person with their families.

Clicking on any person on the picture will redraw SVG, using selected
person as the new base.

Each depicted person has context menus with:
 * optional link to the personal page;
 * fast goto actions for parents, siblings, spouses, children, cousins,
   uncles, nephews.
"""

import json
import os
import os.path
import shutil

from gramps.gen.const import DATA_DIR, GRAMPS_LOCALE
from gramps.gen.config import config
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report.stdoptions import add_private_data_option
from gramps.gen.plug.menu import StringOption, PersonOption, DestinationOption
from gramps.gen.lib import Person
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_path

_ = GRAMPS_LOCALE.translation.sgettext


# ------------------------------------------------------------------------
# WebRelTreeReport
# ------------------------------------------------------------------------
class WebRelTreeReport(Report):
    """
    Create WebRelTreeReport object that produces the report.
    """
    def __init__(self, database, options, user):
        """
        Web Report Constructor.

        :param database: link to Gramps database.
        :type database: gramps.gen.db.DbReadBase

        :param options: plugin configuration.
        :type options: gramps.gen.plug.MenuOptions

        :param user: interface for user interaction.
        :type user: gramps.gen.User
        """
        Report.__init__(self, database, options, user)
        self.options = options
        self.user = user
        self.dirname = None
        self.thumb_dirname = None
        self.gender_map = {
            Person.MALE: 'm',
            Person.FEMALE: 'f',
        }

    def write_report(self):
        """
        Web Report main callback (entry point).

        :returns: none
        """
        # read template for target page
        template_dir = os.path.join(DATA_DIR, 'templates', 'webreltree')
        template_data = ''
        try:
            with open(os.path.join(template_dir, 'index.html')) as fdescr:
                template_data = fdescr.read()
        except IOError as exc:
            self._notify_error('Could not open file: %s', exc)
            return
        # create target directories
        self.dirname = self._get_option_by_name('target')
        if not os.path.isdir(self.dirname):
            try:
                os.mkdir(self.dirname)
            except IOError as exc:
                self._notify_error('Could not create the directory: %s', exc)
                return
        self.thumb_dirname = os.path.join(self.dirname, 'thumbs')
        if not os.path.isdir(self.thumb_dirname):
            try:
                os.mkdir(self.thumb_dirname)
            except IOError as exc:
                self._notify_error('Could not create the directory: %s', exc)
                return
        # copy icons
        for basename in ['female.png', 'male.png', 'unknown.png']:
            try:
                shutil.copy(os.path.join(template_dir, basename),
                            self.thumb_dirname)
            except IOError as exc:
                self._notify_error('Error encountered: %s', exc)
                return
        persons = []
        # read data from database
        incl_private = self._get_option_by_name('incl_private')
        person_handles = self.database.get_person_handles()
        with self.user.progress(
            _('Web Relations Tree Report'), _('Creating individual pages'),
            len(person_handles)) as step:
            for handle in person_handles:
                person = self.database.get_person_from_handle(handle)
                if not incl_private and person.get_privacy():
                    continue
                persons.append({
                    'id': person.gramps_id,
                    'name': _person_short_name(person),
                    'fullname': _person_full_name(person),
                    'url': self._gen_url(person),
                    'icon': self._gen_icon(person, incl_private),
                    'bdate': self._fmt_event(person.get_birth_ref()),
                    'ddate': self._fmt_event(person.get_death_ref()),
                    'gender': self.gender_map.get(person.get_gender()),
                    'childOf': self._get_families(
                        person.get_parent_family_handle_list(), incl_private),
                    'parentOf': self._get_families(
                        person.get_family_handle_list(), incl_private),
                })
                step()
        # substitute placeholders and write result to a target file
        template_data = template_data.replace(
            '@@TITLE@@', self._get_option_by_name('title'))
        template_data = template_data.replace(
            '@@DATAMODEL@@',
            ('var personsSource = %s;\nvar startPersonId = %s;\n' %
             (json.dumps(persons, indent=2),
              json.dumps(self._get_option_by_name('person_id')))))
        target_path = os.path.join(self.dirname, 'webreltree.html')
        try:
            with open(target_path, 'w') as fdescr:
                fdescr.write(template_data)
        except IOError as exc:
            self._notify_error('Error encountered: %s', exc)
            return

    def _get_option_by_name(self, name):
        """
        Return named configuration value.

        :param name: name of the setting.
        :type name: str

        :returns: str
        """
        return self.options.menu.get_option_by_name(name).get_value()

    def _notify_error(self, message, *args):
        """
        Notify the user of an error.

        :param title: the title of the error.
        :type title: str

        :param error: the error message.
        :type error: str

        :returns: none
        """
        self.user.notify_error(_(message) % args)

    def _get_families(self, handles, incl_private):
        """
        Return list of families IDs.

        :param handles: List of handles corresponding to the family
                        records with which the person is associated.
        :type handles: list of str or bytes

        :param incl_private: include private records into result or not.
        :type incl_private: bool

        :returns: list of
        """
        result = []
        for handle in handles:
            family = self.database.get_family_from_handle(handle)
            if incl_private or not family.get_privacy():
                result.append(family.gramps_id)
        return result

    def _gen_url(self, person):
        """
        Generate URL to personal page in Narrative Web Site.

        :param person: person object.
        :type person: gramps.gen.lib.Person

        :returns: str or none
        """
        narweb_url = self._get_option_by_name('narweb_prefix')
        if narweb_url:
            fname = person.get_handle()
            path = [narweb_url, 'ppl', fname[-1].lower(),
                    fname[-2].lower(), fname + '.html']
            return '/'.join([e.strip('/') for e in path])
        return None

    def _gen_icon(self, person, incl_private=True):
        """
        Return link to the main photo of the given person.

        :param person: person object.
        :type person: gramps.gen.lib.Person

        :param incl_private: use media marked as private or not.
        :type incl_private: bool

        :returns: str or none
        """
        media_refs = person.get_media_list()
        if not media_refs:
            return None
        photo = None
        for media_ref in media_refs:
            region = media_ref.get_rectangle()
            photo_handle = media_ref.get_reference_handle()
            photo = self.database.get_media_from_handle(photo_handle)
            if not incl_private and photo.get_privacy():
                continue
            break
        if photo is None:
            return None
        mimetype = photo.get_mime_type()
        if mimetype:
            full_path = media_path_full(self.database, photo.get_path())
            src_path = get_thumbnail_path(full_path, mimetype, region)
            dst_path = os.path.join(
                self.thumb_dirname, photo_handle +
                (('%d,%d-%d,%d.png' % region) if region else '.png'))
            shutil.copyfile(src_path, dst_path)
            return os.path.join('thumbs', os.path.basename(dst_path))
        return None

    def _fmt_event(self, event_ref):
        """
        Format birth/death dates of the person as string.

        :param event_ref: person event object
        :type event_ref: gramps.gen.lib.EventRef or none

        :returns: str
        """
        if event_ref is None:
            return None
        handle = event_ref.get_reference_handle()
        if handle is None:
            return None
        event = self.database.get_event_from_handle(handle)
        if event is None:
            return None
        date = event.get_date_object()
        if date is None:
            return None
        year = date.get_year()
        if year == 0:
            return None
        month = date.get_month()
        day = date.get_day()
        return '%0.4d-%0.2d-%0.2d' % (year, month, day)


# -----------------------------------------------------------------------------
# WebRelTreeOptions; Creates the Menu
# -----------------------------------------------------------------------------
class WebRelTreeOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, database):
        """
        Constructor for plugins configuration options.

        :param name: report plugin name.
        :type name: str

        :param database: link to Gramps database.
        :type database: gramps.gen.db.DbReadBase
        """
        self.__dbname = database.get_dbname()
        MenuReportOptions.__init__(self, name, database)

    def add_menu_options(self, menu):
        """
        Add options to the menu for this report.

        :param menu: the menu for which we add options.
        :type menu: gramps.gen.plug.menu.Menu

        :returns: none
        """
        category_name = _('Report Options')

        target = DestinationOption(
            _('Destination'),
            os.path.join(config.get('paths.website-directory'),
                         self.__dbname + '_WEBRELTREE'))
        target.set_help(_('The destination directory for the web files'))
        target.set_directory_entry(True)
        menu.add_option(category_name, 'target', target)

        title = StringOption(_('Title text'), 'Web Relations Tree')
        title.set_help(_('The title of the web site'))
        menu.add_option(category_name, 'title', title)

        add_private_data_option(menu, category_name)

        person_id = PersonOption(_('Filter Person'))
        person_id.set_help(_('The center person for the filter'))
        menu.add_option(category_name, 'person_id', person_id)

        narweb_prefix = StringOption(
            _('Link prefix'), '../../' + self.__dbname + '_NARWEB/')
        narweb_prefix.set_help(
            _('A Prefix on the links to take you to Narrated Web Report'))
        menu.add_option(category_name, 'narweb_prefix', narweb_prefix)


def _person_short_name(person):
    """
    Create short name for the person.

    :param person: person object.
    :type person: gramps.gen.lib.Person

    :returns: str
    """
    pname = person.get_primary_name()
    short_name = [pname.first_name]
    for surname in pname.surname_list:
        if not surname.surname:
            continue
        if surname.primary:
            short_name.insert(0, surname.surname)
            break
    return ' '.join(short_name)


def _person_full_name(person):
    """
    Create full name for the person.

    :param person: person object.
    :type person: gramps.gen.lib.Person

    :returns: str
    """
    pname = person.get_primary_name()
    full_name = [pname.first_name]
    for surname in pname.surname_list:
        if not surname.surname:
            continue
        if surname.primary:
            full_name.insert(0, surname.surname)
        else:
            full_name.append(surname.surname)
    return ' '.join(full_name)
