from ReportBase._SimpleAccess import SimpleAccess, by_date
from ReportBase._SimpleDoc import SimpleDoc

def run(database, document, person):
    
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    # get the personal events
    event_list = sa.events(person)

    # get the events of each family in which the person is 
    # a parent
    for family in sa.parent_in(person):
        event_list += sa.events(family)

    # Sort the events by their date
    event_list.sort(by_date)

    # display the results

    sd.title("Sorted events of %s" % sa.name(person))
    sd.paragraph("")

    sd.header1("Event Type\tEvent Date\tEvent Place")
    for event in event_list:
        sd.paragraph("%-12s\t%-12s\t%s" % (sa.event_type(event), 
                                           sa.event_date(event), 
                                           sa.event_place(event)))

    sd.paragraph("Marriage %s" % sa.marriage_place(person))
