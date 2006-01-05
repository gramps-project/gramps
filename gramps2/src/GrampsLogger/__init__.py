"""
This package implements some extensions to the standard Python logging module that
support a consistent logging and bug reporting framework for Gramps.

The package provides:

  GtkHandler - a log handler that will pop up a gtk dialog when a log message is
               sent to it. The dialog offers the user the chance to start
               ErrorReportAssistant to send a bug report.

  RotateHandler - a log handler that just keeps a rotating buffer of the last N
               log messages sent to it. This can be used with the GtkHandler to
               pass a history of log messages to the ErrorReportAssistant.

Usage:

   These handlers can be used in same way a all the other logger module handlers.

   Simple example:

        from GrampsLogger import GtkHandler, RotateHandler

        rh = RotateHandler(capacity=20)
        rh.setLevel(logging.DEBUG)
        
        gtkh = GtkHandler(rotate_handler=rh)
        gtkh.setLevel(logging.ERROR)

        l = logging.getLogger("GtkHandlerTest")        
        l.setLevel(logging.DEBUG)

        l.addHandler(rh)
        l.addHandler(gtkh)

        log_message = "Debug message"
        try:
            wibble
        except:
            l.error(log_message,exc_info=True)

        gtk.main()

"""

from _GtkHandler import GtkHandler
from _RotateHandler import RotateHandler
