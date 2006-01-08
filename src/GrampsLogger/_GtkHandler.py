
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

	self._record = record
        ErrorView(error_detail=self,rotate_handler=self._rotate_handler)

    def get_formatted_log(self):
	return self.format(self._record)

    def get_record(self):
	return self._record
