#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
# Copyright (C) 2003  Tim Waugh
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import gtk

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import const
import Report
import BaseDoc
import RelLib
import Errors
import Plugins
from QuestionDialog import ErrorDialog
from gettext import gettext as _

#------------------------------------------------------------------------
#
# ComprehensiveAncestorsReport
#
#------------------------------------------------------------------------
class ComprehensiveAncestorsReport (Report.Report):

    def __init__(self,database,person,max,pgbrk,cite,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.opt_cite = cite
        self.doc = doc
        self.sources = []
        self.sourcerefs = []
        self.newpage = newpage
        self.RelClass = Plugins.relationship_class
        self.relationship = self.RelClass(database)

        table = BaseDoc.TableStyle ()
        table.set_column_widths ([15, 85])
        table.set_width (100)
        doc.add_table_style ("AR-PersonNoSpouse", table)

        table = BaseDoc.TableStyle ()
        table.set_column_widths ([10, 15, 75])
        table.set_width (100)
        doc.add_table_style ("AR-ChildNoSpouse", table)

        for nspouse in range (1, 3):
            table = BaseDoc.TableStyle ()
            table.set_width (100)
            widths = [15, 100 - 15 * (nspouse + 1)]
            widths.extend ([15] * nspouse)
            table.set_column_widths (widths)
            doc.add_table_style ("AR-PersonWithSpouse%d" % nspouse, table)

            table = BaseDoc.TableStyle ()
            table.set_width (100)
            widths = [10, 15, 90 - 15 * (nspouse + 1)]
            widths.extend ([15] * nspouse)
            table.set_column_widths (widths)
            doc.add_table_style ("AR-ChildWithSpouse%d"% nspouse, table)

        cell = BaseDoc.TableCellStyle ()
        cell.set_padding (1) # each side makes 2cm, the size of the photo
        doc.add_cell_style ("AR-PaddedCell", cell)

        cell = BaseDoc.TableCellStyle ()
        cell.set_padding (0.1)
        cell.set_left_border (1)
        cell.set_top_border (1)
        cell.set_right_border (1)
        cell.set_bottom_border (1)
        doc.add_cell_style ("AR-NoPhoto", cell)

        cell = BaseDoc.TableCellStyle ()
        cell.set_padding (0.1)
        doc.add_cell_style ("AR-Photo", cell)

        cell = BaseDoc.TableCellStyle ()
        cell.set_padding (0.1)
        doc.add_cell_style ("AR-Entry", cell)

        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0

    def write_report(self):
        if self.newpage:
            self.doc.page_break()

        self.sources = []
        name = self.person_name (self.start.get_id())
        self.doc.start_paragraph("AR-Title")
        title = _("Ancestors of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()

        self.doc.start_paragraph ("AR-Heading")
        self.doc.write_text (_("Generation 1"))
        self.doc.end_paragraph ()

        self.write_paragraphs (self.person (self.start.get_id(), suppress_children = 1,
                                            needs_name = 1))
        family_ids = [self.start.get_main_parents_family_id ()]
        if len (family_ids) > 0:
            self.generation (self.max_generations, family_ids, [], [self.start.get_id()])

        if len (self.sources) > 0:
            self.doc.start_paragraph ("AR-Heading")
            self.doc.write_text (_("Sources"))
            self.doc.end_paragraph ()

            i = 1
            for source_id in self.sources:
                source = self.database.find_source_from_id(source_id)
                self.doc.start_paragraph ("AR-Entry")
                self.doc.write_text ("[%d] %s" % (i, source.get_title ()))
                author = source.get_author ()
                pubinfo = source.get_publication_info ()
                extra = author
                if pubinfo:
                    if extra:
                        extra += ', '
                    extra += pubinfo
                if extra:
                    self.doc.write_text ('; %s' % extra)
                self.doc.end_paragraph ()

                note = source.get_note ()
                format = source.get_note_format ()
                if note:
                    self.doc.write_note (note, format, "AR-Details")

                i += 1

        if self.standalone:
            self.doc.close()
        return

    def write_paragraphs (self, paragraphs):
        for (fn, params) in paragraphs:
            if len (params) == 0:
                fn ()
            elif len (params) == 1:
                fn (params[0])
            elif len (params) == 2:
                fn (params[0], params[1])
            elif len (params) == 3:
                fn (params[0], params[1], params[2])
            elif len (params) == 4:
                fn (params[0], params[1], params[2], params[3])
            else:
                self.doc.write_text ("Call to %s with params %s" %
                                     (str (fn), str (params)))

    def family (self, family_id, already_described):
        ret = []
        family = self.database.find_family_from_id(family_id)
        if not family:
            return ret
        father_id = family.get_father_id ()
        mother_id = family.get_mother_id ()
        father = self.database.find_person_from_id(father_id)
        mother = self.database.find_person_from_id(mother_id)
        if father:
            ret.extend (self.person (father_id,
                                     short_form = father_id in already_described,
                                     already_described = already_described,
                                     needs_name = not mother,
                                     from_family = family))

        if mother:
            ret.extend (self.person (mother_id,
                                     short_form = mother_id in already_described,
                                     already_described = already_described,
                                     needs_name = not father,
                                     from_family = family))

        children_ids = family.get_child_id_list ()
        if len (children_ids):
            ret.append ((self.doc.start_paragraph, ['AR-ChildTitle']))
            ret.append ((self.doc.write_text, [_('Their children:')]))
            ret.append ((self.doc.end_paragraph, []))

            for child_id in children_ids:
                child = self.database.find_person_from_id(child_id)
                ret.extend (self.person (child_id, suppress_children = 1,
                                         short_form=child_id in already_described,
                                         already_described = already_described,
                                         needs_name = 1,
                                         from_family = family))

        return ret

    def generation (self, generations, pfamily_ids, mfamily_ids,
                    already_described, thisgen = 2):
        if generations > 1 and (len (pfamily_ids) + len (mfamily_ids)):
            people = []
            for family_id in pfamily_ids:
                people.extend (self.family (family_id, already_described))

            if thisgen > 2 and len (mfamily_ids):
                for self.gp in [self.database.find_family_from_id(mfamily_ids[0]).get_father_id (),
                                self.database.find_family_from_id(mfamily_ids[0]).get_mother_id ()]:
                    if self.gp:
                        break

                relstring = self.relationship.get_grandparents_string (self.start,
                               self.database.find_person_from_id(self.gp))[0]
                heading = _("%(name)s's maternal %(grandparents)s") % \
                          { 'name': self.first_name_or_nick (self.start),
                            'grandparents': relstring }
                people.append ((self.doc.start_paragraph, ['AR-Heading']))
                people.append ((self.doc.write_text, [heading]))
                people.append ((self.doc.end_paragraph, []))

            for family_id in mfamily_ids:
                people.extend (self.family (family_id, already_described))

            if len (people):
                if self.pgbrk:
                    self.doc.page_break()
                self.doc.start_paragraph ("AR-Heading")
                family_ids = pfamily_ids
                family_ids.extend (mfamily_ids)
                for self.gp in [self.database.find_family_from_id(family_ids[0]).get_father_id (),
                                self.database.find_family_from_id(family_ids[0]).get_mother_id ()]:
                    if self.gp:
                        break

                relstring = self.relationship.get_grandparents_string (self.start,
                                                                  self.database.find_person_from_id(self.gp))[0]
                if thisgen == 2:
                    heading = _("%(name)s's %(parents)s") % \
                              { 'name': self.first_name_or_nick (self.start),
                                'parents': relstring }
                else:
                    heading = _("%(name)s's paternal %(grandparents)s") % \
                              { 'name': self.first_name_or_nick (self.start),
                                'grandparents': relstring }

                self.doc.write_text (heading)
                self.doc.end_paragraph ()
                self.write_paragraphs (people)

                next_pfamily_ids = []
                next_mfamily_ids = []
                for family_id in family_ids:
                    family = self.database.find_family_from_id(family_id)
                    father_id = family.get_father_id ()
                    father = self.database.find_person_from_id(father_id)
                    if father:
                        already_described.append (father_id)
                        father_family_id = father.get_main_parents_family_id ()
                        father_family = self.database.find_family_from_id(father_family_id)
                        if father_family:
                            next_pfamily_ids.append (father_family_id)

                    mother_id = family.get_mother_id ()
                    mother = self.database.find_person_from_id(mother_id)
                    if mother:
                        already_described.append (mother_id)
                        mother_family_id = mother.get_main_parents_family_id ()
                        mother_family = self.database.find_family_from_id(mother_family_id)
                        if mother_family:
                            next_mfamily_ids.append (mother_family_id)

                self.generation (generations - 1, next_pfamily_ids,
                                 next_mfamily_ids, already_described,
                                 thisgen + 1)

    def person (self, person_id,
                suppress_children = 0,
                short_form = 0,
                already_described = [],
                needs_name = 0,
                from_family = None):
        ret = []
        person = self.database.find_person_from_id(person_id)
        name = self.person_name (person_id)
        if name:
            photos = person.get_media_list ()

            bits = ''
            bits += self.short_occupation (person)
            bits += self.long_born_died (person)
            if not suppress_children:
                bits += self.parents_of (person)
            else:
                bits += '.'
            bits += self.married_whom (person, from_family, suppress_children)
            bits += self.inline_notes (person)

            longnotes = self.long_notes (person, suppress_children,
                                         already_described)

            if (bits != '.' or longnotes or photos or
                suppress_children or needs_name):
                # We have something to say about this person.

                spouse = []
                if from_family:
                    from_family_father = from_family.get_father_id ()
                    from_family_mother = from_family.get_mother_id ()
                else:
                    from_family_father = from_family_mother = None

                for family_id in person.get_family_id_list ():
                    family = self.database.find_family_from_id(family_id)
                    for partner_id in [family.get_father_id (),
                                    family.get_mother_id ()]:
                        partner = self.database.find_person_from_id(partner_id)
                        if partner_id == person_id or not partner:
                            continue

                        if (suppress_children or
                            (partner != from_family_father and
                             partner != from_family_mother)):
                            for media_ref in partner.get_media_list ()[:1]:
                                object_id = media_ref.get_reference_id()
                                mobject = self.database.find_object_from_id(object_id)
                                if mobject.get_mime_type()[0:5] == "image":
                                    spouse.append ((self.doc.add_media_object,
                                                    [mobject.get_path (),
                                                     'right', 2, 2]))

                if suppress_children and len (already_described):
                    style = "AR-Child"
                else:
                    style = "AR-Person"
                if len (spouse):
                    style += "WithSpouse%d" % len (spouse)
                else:
                    style += "NoSpouse"

                ret.append ((self.doc.start_table, [style, style]))
                ret.append ((self.doc.start_row, []))

                if suppress_children and len (already_described):
                    # Can't do proper formatting with BaseDoc, so cheat.
                    ret.append ((self.doc.start_cell, ["AR-PaddedCell"]))
                    ret.append ((self.doc.end_cell, []))

                if len (photos) == 0:
                    ret.append ((self.doc.start_cell, ["AR-NoPhoto"]))
                    ret.append ((self.doc.start_paragraph, ["AR-NoPhotoText"]))
                    ret.append ((self.doc.write_text, [_("(no photo)")]))
                    ret.append ((self.doc.end_paragraph, []))
                    ret.append ((self.doc.end_cell, []))
                else:
                    ret.append ((self.doc.start_cell, ["AR-Photo"]))
                    for media_ref in photos[:1]:
                        object_id = media_ref.get_reference_id()
                        mobject = self.database.find_object_from_id(object_id)
                        if mobject.get_mime_type()[0:5] == "image":
                            ret.append ((self.doc.add_media_object,
                                         [mobject.get_path (), 'left', 2, 2]))
                        ret.append ((self.doc.end_cell, []))

                ret.append ((self.doc.start_cell, ["AR-Entry"]))
                ret.append ((self.doc.start_paragraph, ["AR-Entry"]))
                ret.append ((self.doc.write_text, [name]))
                if short_form:
                    ret.append ((self.doc.write_text,
                                 [_(" (mentioned above).")]))
                else:
                    ret.append ((self.doc.write_text, [bits]))

                ret.append ((self.doc.end_paragraph, []))
                ret.append ((self.doc.end_cell, []))

                for s in spouse:
                    ret.append ((self.doc.start_cell, ["AR-Photo"]))
                    ret.append (s)
                    ret.append ((self.doc.end_cell, []))

                ret.append ((self.doc.end_row, []))
                ret.append ((self.doc.end_table, []))

                if not short_form:
                    ret.extend (longnotes)

        return ret

    def short_occupation (self, person):
        occupation = ''
        for event_id in person.get_event_list ():
            if not event_id:
                continue
            event = self.database.find_event_from_id(event_id)
            if event.get_name () == 'Occupation':
                if occupation:
                    return ''

                occupation = event.get_description ()

        if occupation:
            return ' (%s)' % occupation

        return ''

    def event_info (self, event):
        info = ''
        name = event.get_name ()
        description = event.get_description ()
        if name != 'Birth' and name != 'Death' and name != 'Marriage':
            info += const.display_pevent (name)
            if description:
                info += ': ' + description
                description = None

        dateobj = event.get_date_object ()
        if dateobj:
            text = dateobj.get_text()
            if text:
                info += ' ' + text[0].lower() + text[1:]
            elif dateobj.get_valid ():
                if dateobj.is_range ():
                    info += ' ' + dateobj.get_date ()
                elif (dateobj.get_day_valid () and
                    dateobj.get_month_valid () and
                    dateobj.get_year_valid ()):
                    info += _(' on %(specific_date)s') % \
                            {'specific_date': dateobj.get_date ()}
                else:
                    info += _(' in %(month_or_year)s') % \
                            {'month_or_year': dateobj.get_date ()}

        placename = self.database.find_place_from_id(event.get_place_id()).get_title()
        if placename:
            info += _(' in %(place)s') % {'place': placename}
        note = event.get_note ()
        note_format = event.get_note_format ()
        inline_note = note and (note_format == 0)
        if inline_note or description:
            info += ' ('
            if description:
                info += description
            if note:
                if description:
                    info += '; '
                info += note
            info += ')'

        info += self.cite_sources (event.get_source_references ())
        return info

    def address_info (self, address):
        info = _('Address:') + ' %s %s %s %s' % (address.get_street (),
                                                 address.get_city (),
                                                 address.get_state (),
                                                 address.get_country ())

        info = info.rstrip ()
        date = address.get_date ()
        if date:
            info += ', ' + date

        info += self.cite_sources (address.get_source_references ())
        return info

    def abbrev_born_died (self, person):
        ret = ''

        birth_id = person.get_birth_id ()
        if birth_id:
            birth = self.database.find_event_from_id(birth_id)
            date = birth.get_date ()
            if date:
                ret += _(" b. %(date)s") % {'date': date}
                ret += self.cite_sources (birth.get_source_references ())

        death_id = person.get_death_id ()
        if death_id:
            death = self.database.find_event_from_id(death_id)
            date = death.get_date ()
            if date:
                ret += _(" d. %(date)s)") % {'date': date}
                ret += self.cite_sources (death.get_source_references ())

        return ret

    def long_born_died (self, person):
        ret = ''
        birth_id = person.get_birth_id ()
        if birth_id:
            birth = self.database.find_event_from_id(birth_id)
            born_info = self.event_info (birth)
            if born_info:
                ret = ", " + _("born") + born_info

        death_id = person.get_death_id()
        if death_id:
            death = self.database.find_event_from_id(death_id)
            died_info = self.event_info (death)
            if died_info:
                if born_info:
                    ret += '; '
                else:
                    ret += ', '

                ret += _('died') + died_info

        return ret

    def parents_of (self, person_id):
        person = self.database.find_person_from_id(person_id)
        gender = person.get_gender ()

        family = person.get_main_parents_family_id ()
        ret = '.  '
        if family:
            fathername = mothername = None
            father_id = family.get_father_id ()
            father = self.database.find_person_from_id(father_id)
            if father:
                fathername = self.person_name (father_id)
            mother_id = family.get_mother_id ()
            mother = self.database.find_person_from_id(mother_id)
            if mother:
                mothername = self.person_name (mother_id)

            if not mother and not father:
                pass
            elif not father:
                if gender == RelLib.Person.female:
                    ret += _("She is the daughter of %(mother)s.") % \
                           {'mother': mothername}
                else:
                    ret += _("He is the son of %(mother)s.") % \
                           {'mother': mothername}
            elif not mother:
                if gender == RelLib.Person.female:
                    ret += _("She is the daughter of %(father)s.") % \
                           {'father': fathername}
                else:
                    ret += _("He is the son of %(father)s.") % \
                           {'father': fathername}
            else:
                if gender == RelLib.Person.female:
                    ret += \
                        _("She is the daughter of %(father)s and %(mother)s.")%\
                        {'father': fathername,
                         'mother': mothername}
                else:
                    ret +=_("He is the son of %(father)s and %(mother)s.") % \
                           {'father': fathername,
                            'mother': mothername}

        return ret

    def first_name_or_nick (self, person):
        nickname = person.get_nick_name ()
        if nickname:
            return nickname

        name = person.get_primary_name ().get_first_name ()
        return name.split (' ')[0]

    def title (self, person):
        name = person.get_primary_name ()
        t = name.get_title ()
        if t:
            return t

        gender = person.get_gender ()
        if gender == RelLib.Person.female:
            if name.get_type () == 'Married Name':
                return _('Mrs.')

            return _('Miss')
        elif gender == RelLib.Person.male:
            return _('Mr.')
        else:
            return _('(gender unknown)')

    def cite_sources (self, sourcereflist):
        citation = ""
        if self.opt_cite:
            for ref in sourcereflist:
                if ref in self.sourcerefs:
                    continue

                self.sourcerefs.append (ref)
                source_id = ref.get_base_id ()
                if source_id in self.sources:
                    ind = self.sources.index (source_id) + 1
                else:
                    self.sources.append (source_id)
                    ind = len (self.sources)

                citation += "[%d" % ind
                comments = ref.get_comments ()
                if comments and comments.find ('\n') == -1:
                    # Work around rstrip('.') which is not working 
                    # with python2.2.1 and earlier
                    #citation += " - %s" % comments.rstrip ('.')
                    comments = comments.rstrip()
                    if comments[-1] == '.':
                        comments = comments[:-1]
                    citation += " - %s" % comments

                citation += "]"

        return citation

    def person_name (self, person_id):
        person = self.database.find_person_from_id(person_id)
        primary = person.get_primary_name ()

        name = primary.get_title ()
        if name:
            name += ' '

        first = primary.get_first_name ()
        last = primary.get_surname ()
        first_replaced = first.replace ('?', '')
        if first_replaced == '':
            name += self.title (person)
        else:
            name += first

        nick = person.get_nick_name ()
        if nick:
            #nick = nick.strip ('"')
            # Work around strip('"') which is not working 
            # with python2.2.1 and earlier
            nick = nick.strip()
            if nick[0] == '"':
                nick = nick[1:]
            if nick[-1] == '"':
                nick = nick[:-1]
                name += ' ("%s")' % nick

        if last.replace ('?', '') == '':
            if first_replaced == '':
                name += _(' (unknown)')
        else:
            name += ' ' + last

        suffix = primary.get_suffix ()
        if suffix:
            name += ', ' + suffix

        type = primary.get_type ()
        if type != 'Birth Name':
            name += ' (%s)' % type

        name += self.cite_sources (primary.get_source_references ())
        return name

    def married_whom (self, person, from_family, listing_children = 0):
        gender = person.get_gender ()
        first_marriage = 1
        ret = ''
        for family_id in person.get_family_id_list ():
            family = self.database.find_family_from_id(family_id)
            mother_id = family.get_mother_id ()
            mother = self.database.find_person_from_id(mother_id)
            for spouse_id in [family.get_father_id (), mother_id]:
                spouse = self.database.find_person_from_id(spouse_id)
                if spouse_id == person.get_id() or not spouse_id:
                    continue

                children = ''
                childlist = family.get_child_id_list ()
                child_count = len (childlist)
                if ((listing_children or family != from_family) and
                    child_count > 0):
                    if child_count == 1:
                        children = _(', and they had a child named ')
                    else:
                        children += _(', and they had %d children: ') % \
                                    child_count

                    count = 1
                    for child_id in childlist:
                        child = self.database.find_person_from_id(child_id)
                        children += self.first_name_or_nick (child)
                        children += self.cite_sources (child.get_primary_name ().
                                                       get_source_references ())
                        children += self.abbrev_born_died (child)
                        if child_count - count > 1:
                            children += ', '
                        elif child_count - count == 1:
                            children += _(' and ')

                        count += 1

                for event_id in family.get_event_list():
                    if event_id:
                        event = self.database.find_event_from_id(event_id)
                        if event.get_name() == "Marriage":
                            marriage = event
                            break
                else:
                    continue

                #marriage = family.get_marriage ()
                if not first_marriage:
                    if gender == RelLib.Person.female:
                        ret += _('  She later married %(name)s') % \
                               {'name': self.person_name (spouse_id)}
                    else:
                        ret += _('  He later married %(name)s') % \
                               {'name': self.person_name (spouse_id)}

                    if marriage:
                        ret += self.event_info (marriage)
                    ret += children + '.'
                elif (listing_children or
                      spouse_id == mother_id or
                      family_id != from_family.get_id()):
                    if gender == RelLib.Person.female:
                        ret += _('  She married %(name)s') % \
                               {'name': self.person_name (spouse_id)}
                    else:
                        ret += _('  He married %(name)s') % \
                               {'name': self.person_name (spouse_id)}

                    if marriage:
                        ret += self.event_info (marriage)
                    ret += children + '.'

            first_marriage = 0

        return ret

    def inline_notes (self, person):
        name_note = person.get_primary_name ().get_note ()
        if not (name_note == '' or name_note.find ('\n') != -1):
            return _('  Note about their name: ') + name_note
        note = person.get_note ()
        if not (person.get_note_format () != 0 or
                note == '' or note.find ('\n') != -1):
            return '  ' + note

        return ''

    def long_details (self, note, paras):
        para_end = note.find ('\n')
        if para_end != -1:
            paras = self.long_details (note[note.find ('\n') + 1:], paras)
        else:
            para_end = len (note)

        paras.insert (0, (self.doc.end_paragraph, []))
        paras.insert (0, (self.doc.write_text, [note[:para_end]]))
        paras.insert (0, (self.doc.start_paragraph, ['AR-Details']))
        return paras

    def long_notes (self, person, suppress_children = 0,
                    already_described = []):
        note = person.get_note ()
        format = person.get_note_format ()
        if format != 0:
            paras = [ (self.doc.write_note, [note, format, 'AR-Details']) ]
        elif note != '' and note.find ('\n') != -1:
            paras = self.long_details (note, [])
        else:
            paras = []

        names = person.get_alternate_names ()
        event_ids = person.get_event_list ()
        addresses = person.get_address_list ()
        if (len (event_ids) + len (addresses) + len (names)) > 0:
            paras.append ((self.doc.start_paragraph, ['AR-SubEntry']))
            paras.append ((self.doc.write_text,
                           [_("More about %(name)s:") %
                            {'name': self.first_name_or_nick (person)}]))
            paras.append ((self.doc.end_paragraph, []))

        for name in names:
            paras.append ((self.doc.start_paragraph, ['AR-Details']))
            paras.append ((self.doc.write_text,
                           [const.NameTypesMap.find_value(name.get_type ()) +
                            ': ' + name.get_regular_name ()]))
            paras.append ((self.doc.end_paragraph, []))

        for event_id in [person.get_birth_id (), person.get_death_id ()]:
            if not event_id:
                continue
            event = self.database.find_event_from_id(event_id)
            note = event.get_note ()
            note_format = event.get_note_format ()
            if note and (note_format != 0):
                paras.append ((self.doc.write_note, [note, format,
                                                     'AR-Details']))

        for event_id in event_ids:
            if not event_id:
                continue
            event = self.database.find_event_from_id(event_id)
            paras.append ((self.doc.start_paragraph, ['AR-Details']))
            paras.append ((self.doc.write_text, [self.event_info (event)]))
            paras.append ((self.doc.end_paragraph, []))
            note = event.get_note ()
            note_format = event.get_note_format ()
            if note and (note_format != 0):
                paras.append ((self.doc.write_note, [note, format,
                                                     'AR-Details']))

        for address in addresses:
            paras.append ((self.doc.start_paragraph, ['AR-Details']))
            paras.append ((self.doc.write_text, [self.address_info (address)]))
            paras.append ((self.doc.end_paragraph, []))

        return paras

def _make_default_style(default_style):
    """Make the default output style for the Comprehensive Ancestors report."""
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the title of the page.'))
    default_style.add_style("AR-Title",para)
    
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the generation header.'))
    default_style.add_style("AR-Heading",para)

    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=1.0,pad=0.25)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("AR-Entry",para)

    para = BaseDoc.ParagraphStyle ()
    para.set_description(_('Text style for missing photo.'))
    default_style.add_style("AR-NoPhotoText", para)

    details_font = BaseDoc.FontStyle()
    details_font.set(face=BaseDoc.FONT_SANS_SERIF,size=8,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=2.7,pad=0,font = details_font)
    para.set_description(_('Style for details about a person.'))
    default_style.add_style("AR-Details",para)

    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=2.5,pad=0.25)
    para.set_description(_('The basic style used for the text display.'))
    para.set_header_level (4)
    default_style.add_style("AR-SubEntry",para)

    para = BaseDoc.ParagraphStyle()
    para.set(pad=0.05)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("AR-Endnotes",para)

    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=1.0,pad=0.05)
    para.set_description(_('Introduction to the children.'))
    para.set_header_level (3)
    default_style.add_style("AR-ChildTitle",para)


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ComprehensiveAncestorsReportDialog(Report.TextReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person,self.report_options)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def doc_uses_tables (self):
        return 1

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Comprehensive Ancestors Report"),
                                     _("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ancestors for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ancestor Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ancestors_report.xml"
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def add_user_options (self):
        self.cb_cite = gtk.CheckButton (_("Cite sources"))
        self.cb_cite.set_active (gtk.TRUE)
        self.add_option ('', self.cb_cite)

    def parse_report_options_frame (self):
        # Call base class
        Report.ReportDialog.parse_report_options_frame (self)
        self.opt_cite = self.cb_cite.get_active ()

    def make_report(self):

        """Create the object that will produce the Comprehensive
        Ancestors Report.  All user dialog has already been handled
        and the output file opened."""
        try:
            MyReport = ComprehensiveAncestorsReport(self.db, self.person,
                                                    self.max_gen, self.pg_brk,
                                                    self.opt_cite, self.doc,
                                                    self.target_path)
            MyReport.write_report()
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Standalone report function
#
#------------------------------------------------------------------------
def report(database,person):
    ComprehensiveAncestorsReportDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ancestors_report.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 10
_pg_brk = 0
_opt_cite = 1

_options = ( _person_id, _max_gen, _pg_brk, _opt_cite )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class ComprehensiveAncestorsBareReportDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.max_gen = int(self.options[1]) 
        self.pg_brk = int(self.options[2])
        self.opt_cite = int(self.options[3])
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.pagebreak_checkbox.set_active(self.pg_brk)
        self.cb_cite.set_active(self.opt_cite)

        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Comprehensive Ancestors Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Comprehensive Ancestors Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def add_user_options (self):
        self.cb_cite = gtk.CheckButton (_("Cite sources"))
        self.add_option ('', self.cb_cite)

    def parse_report_options_frame (self):
        # Call base class
        Report.BareReportDialog.parse_report_options_frame (self)
        self.opt_cite = self.cb_cite.get_active ()

    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.get_id(), self.max_gen, self.pg_brk, self.opt_cite )
        self.style_name = self.selected_style.get_name() 

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Comprehensive Ancestors Report using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        opt_cite = int(options[3])
        return ComprehensiveAncestorsReport(database, person,
            max_gen, pg_brk, opt_cite, doc, None, newpage)
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
Plugins.register_report(
    report,
    _("Comprehensive Ancestors Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a detailed ancestral report."),
    author_name="Tim Waugh",
    author_email="twaugh@redhat.com"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
Plugins.register_book_item( 
    _("Comprehensive Ancestors Report"), 
    _("Text"),
    ComprehensiveAncestorsBareReportDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )
