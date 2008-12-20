from DataViews import register, Gramplet

class AgeStatsGramplet(Gramplet):
    def on_load(self):
        self.no_wrap()
        tag = self.gui.buffer.create_tag("fixed")
        tag.set_property("font", "Courier 8")

    def db_changed(self):
        self.update()

    def main(self):
        self.clear_text()
        age_dict = {}
        mother_dict = {}
        father_dict = {}
        age_handles = [[] for age in range(120)]
        mother_handles = [[] for age in range(60)]
        father_handles = [[] for age in range(60)]
        text = ""
        handles = self.dbstate.db.get_person_handles(sort_handles=False)
        for h in handles:
            yield True
            p = self.dbstate.db.get_person_from_handle(h)
            # if birth_date and death_date, compute age
            birth_ref = p.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.dbstate.db.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            death_ref = p.get_death_ref()
            death_date = None
            if death_ref:
                death_event = self.dbstate.db.get_event_from_handle(death_ref.ref)
                death_date = death_event.get_date_object()
            if death_date and birth_date and birth_date.get_year() != 0:
                age = death_date.get_year() - birth_date.get_year()
                if age >= 0 and age < 120:
                    age_dict[age] = age_dict.get(age, 0) + 1
                    age_handles[age].append(h)
                #else:
                #    print "Age out of range: %d for %s" % (age,
                #                                           p.get_primary_name().get_first_name()
                #                                           + " " + p.get_primary_name().get_surname())
            # for each parent m/f:
            family_list = p.get_parent_family_handle_list()
            if len(family_list) > 0:
                family = self.dbstate.db.get_family_from_handle(family_list[0]) # first is primary, I think
                if family:
                    f_handle = family.get_father_handle()
                    m_handle = family.get_mother_handle()
                    # if they have a birth_date, compute difference each m/f
                    if f_handle:
                        f = self.dbstate.db.get_person_from_handle(f_handle)
                        bref = f.get_birth_ref()
                        if bref:
                            bevent = self.dbstate.db.get_event_from_handle(bref.ref)
                            bdate  = bevent.get_date_object()
                            if bdate and birth_date and birth_date.get_year() != 0:
                                diff = birth_date.get_year() - bdate.get_year()
                                if diff >= 0 and diff < 60:
                                    father_dict[diff] = father_dict.get(diff, 0) + 1
                                    father_handles[diff].append(f_handle)
                                #else:
                                #    print "Father diff out of range: %d for %s" % (diff,
                                #                                                   p.get_primary_name().get_first_name()
                                #                                                   + " " + p.get_primary_name().get_surname())
                    if m_handle:
                        m = self.dbstate.db.get_person_from_handle(m_handle)
                        bref = m.get_birth_ref()
                        if bref:
                            bevent = self.dbstate.db.get_event_from_handle(bref.ref)
                            bdate  = bevent.get_date_object()
                            if bdate and birth_date and birth_date.get_year() != 0:
                                diff = birth_date.get_year() - bdate.get_year()
                                if diff >= 0 and diff < 60:
                                    mother_dict[diff] = mother_dict.get(diff, 0) + 1
                                    mother_handles[diff].append(m_handle)
                                #else:
                                #    print "Mother diff out of range: %d for %s" % (diff,
                                #                                                   p.get_primary_name().get_first_name()
                                #                                                   + " " + p.get_primary_name().get_surname())            
        width = 60
        graph_width = width - 8
        self.create_bargraph(age_dict, age_handles, "Lifespan Age Distribution", "Age", graph_width, 5, 120) 
        self.create_bargraph(father_dict, father_handles, "Father - Child Age Diff Distribution", "Diff", graph_width, 5, 60) 
        self.create_bargraph(mother_dict, mother_handles, "Mother - Child Age Diff Distribution", "Diff", graph_width, 5, 60) 
        start, end = self.gui.buffer.get_bounds()
        self.gui.buffer.apply_tag_by_name("fixed", start, end)
        self.append_text("", scroll_to="begin")

    def ticks(self, width, start = 0, stop = 100, fill = " "):
        """ Returns the tickmark numbers for a graph axis """
        count = int(width / 10.0)
        retval = "%-3d" % start
        space = int((width - count * 3) / float(count - 1))
        incr = (stop - start) / float(count - 1)
        lastincr = 0
        for i in range(count - 2):
            retval += " " * space
            newincr = int(start + (i + 1) * incr)
            if newincr != lastincr:
                retval += "%3d" % newincr
            else:
                retval += " | "
            lastincr = newincr
        rest = width - len(retval) - 3 + 1
        retval += " " * rest
        retval += "%3d" % int(stop)
        return retval
    
    def format(self, text, width, align = "left", borders = "||", fill = " "):
        """ Returns a formatted string for nice, fixed-font display """
        if align == "center":
            text = text.center(width, fill)
        elif align == "left":
            text = (text + (fill * width))[:width]
        elif align == "right":
            text = ((fill * width) + text)[-width:]
        if borders[0] != None:
            text = borders[0] + text
        if borders[1] != None:
            text = text + borders[1]
        return text
    
    def compute_stats(self, hash):
        """ Returns the statistics of a dictionary of data """
        hashkeys = hash.keys()
        hashkeys.sort()
        count = sum(hash.values())
        sumval = sum([k * hash[k] for k in hash])
        minval = min(hashkeys)
        maxval = max(hashkeys)
        median = 0
        average = 0
        if count > 0:
            current = 0
            for k in hashkeys:
                if current + hash[k] > count/2:
                    median = k
                    break
                current += hash[k]
            average = sumval/float(count)
        retval = "Statistics:\n"
        retval += "  Total  : %d\n" % count
        retval += "  Minimum: %d\n" % minval
        retval += "  Average: %.2f\n" % average
        retval += "  Median : %d\n" % median
        retval += "  Maximum: %d\n" % maxval
        return retval
    
    def make_handles_set(self, min, max, handles):
        retval = []
        for i in range(min, max):
            try:
                retval.extend(handles[i])
            except:
                pass
        return retval

    def create_bargraph(self, hash, handles, title, column, graph_width, bin_size, max_val):
        """
        Create a bargraph based on the data in hash. hash is a dict, like:
        hash = {12: 4, 20: 6, 35: 13, 50: 5}
        where the key is the age, and the value stored is the count.
        """
        # first, binify:
        bin = [0] * (max_val/bin_size)
        for value in hash.keys():
            bin[value/bin_size] += hash[value]
        text = ""
        max_bin = float(max(bin))
        if max_bin != 0:
            i = 0
            self.append_text("--------" + self.format("", graph_width, fill = "-", borders="++") + "\n")
            self.append_text(column.center(8) + self.format(title, graph_width, align="center") + "\n")
            self.append_text("--------" + self.format("", graph_width, fill = "-", borders="++") + "\n")
            for bin in bin:
                self.append_text((" %3d-%3d" % (i * 5, (i+1)* 5,)))
                selected = self.make_handles_set(i * 5, (i+1) *5, handles)
                self.link(self.format("X" * int(bin/max_bin * graph_width), graph_width),
                          'PersonList', 
                          selected,
                          tooltip=_("Double-click to see %d people" % len(selected)))
                self.append_text("\n")
                i += 1
            self.append_text("--------" + self.format("", graph_width, fill = "-", borders="++") + "\n")
            self.append_text(" Counts " + self.ticks(graph_width, start = 0, stop = int(max_bin)) + "\n\n")
            self.append_text(self.compute_stats(hash))
            self.append_text("\n")
    
register(type="gramplet", 
         name = "Age Stats Gramplet",
         tname = _("Age Stats Gramplet"),
         height=300,
         expand=True,
         content = AgeStatsGramplet,
         title=_("Age Stats"),
         detached_width = 600,
         detached_height = 450,
         )
    
    
