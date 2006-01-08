import logging

class RotateHandler(logging.Handler):
    """
  A handler class which buffers logging records in memory. A rotating
  buffer is used so that the last X records are always available.
    """
    def __init__(self, capacity):
        """
        Initialize the handler with the buffer size.
        """
        logging.Handler.__init__(self)

        self.set_capacity(capacity)


    def emit(self, record):
        """
        Add the record to the rotating buffer.

        """
        self._buffer[self._index] = record
        self._index = (self._index + 1 ) % self._capacity


    def get_buffer(self):
        """
        Return the buffer with the records in the correct order.
        """

        return [record for record in self._buffer[self._index:] + self._buffer[:self._index]
                if record is not None]

    def get_formatted_log(self, remove_tail_duplicate=None):
        """
        Return the log buffer after it has been formatted.

        Returns a list of strings.
        """

        return [self.format(record) for record in self._buffer[self._index:] + self._buffer[:self._index]
                if record is not None and record != remove_tail_duplicate]

    def set_capacity(self,capacity):
        """
        Set the number of log records that will be stored.
        """
        self._capacity = capacity
        self._index = 0
        self._buffer = self._capacity * [None]
