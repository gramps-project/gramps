
import logging

from _ErrorView import ErrorView


class GtkHandler(logging.Handler):
    """
    A handler class which pops up a Gtk Window when a log message occurs.
    """
    
    def __init__(self,rotate_handler=None):
        """
        Initialize the handler with a optional rotate_logger instance.
        """
        logging.Handler.__init__(self)
        self._rotate_handler = rotate_handler



    def emit(self, record):
        """
        Add the record to the rotating buffer.

        """

        ErrorView(error_detail=self.format(record),rotate_handler=self._rotate_handler)
